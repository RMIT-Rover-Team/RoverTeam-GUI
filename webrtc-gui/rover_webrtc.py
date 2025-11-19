import asyncio
import json
import logging
import cv2
import glob
import time
from fractions import Fraction
from pathlib import Path
from datetime import datetime

from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaStreamTrack
from av import VideoFrame


HOST = "0.0.0.0"
PORT = 3001
pcs = set()
BANDWIDTH_LOG_PATH = None


def setup_run_logging():
    """Create a timestamped run directory under ./logs and configure logging to file+console.

    Returns the path to the bandwidth log file for per-frame appends.
    """
    logs_root = Path("logs")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    run_dir = logs_root / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)

    server_log = run_dir / "server.log"
    bandwidth_log = run_dir / "bandwidth-Logs.txt"

    # Configure root logger: keep console + file handlers
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

    # Stream (console) handler
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)

    # File handler
    fh = logging.FileHandler(server_log, encoding="utf-8")
    fh.setFormatter(formatter)

    # Clear existing handlers then add ours
    if logger.handlers:
        for h in list(logger.handlers):
            logger.removeHandler(h)

    logger.addHandler(sh)
    logger.addHandler(fh)

    logging.info(f"Logging initialized. Run directory: {run_dir}")
    return str(bandwidth_log)


# ---------------------------------------------------------
# CAMERA ENUMERATION — reliable and clean
# ---------------------------------------------------------

def list_camera_indices():
    """Return only real cameras that can deliver frames."""
    cameras = []

    logging.info("[Startup] Scanning /dev/video* devices...")  # <<< ADDED

    for dev in sorted(glob.glob("/dev/video*")):
        idx = int(dev.replace("/dev/video", ""))

        try:
            name = open(f"/sys/class/video4linux/video{idx}/name").read().strip()
            logging.info(f"[Startup] Found device video{idx}: {name}")  # <<< ADDED

            if "loopback" in name.lower():
                logging.info(f"[Startup] Skipping loopback device video{idx}")  # <<< ADDED
                continue

        except Exception as e:
            logging.warning(f"[Startup] Unable to read device name for video{idx}: {e}")  # <<< ADDED
            continue

        cap = cv2.VideoCapture(idx)
        if not cap.isOpened():
            logging.warning(f"[Startup] video{idx} could not be opened.")  # <<< ADDED
            continue

        ret, _ = cap.read()
        cap.release()

        if ret:
            logging.info(f"[Startup] video{idx} is usable.")  # <<< ADDED
            cameras.append(idx)
        else:
            logging.warning(f"[Startup] video{idx} opened but cannot return frames.")  # <<< ADDED

    logging.info(f"[Startup] Final camera list: {cameras}")  # <<< ADDED
    return cameras


# ---------------------------------------------------------
# MEDIA TRACK — handles grabbing frames
# ---------------------------------------------------------

class RoverCameraTrack(MediaStreamTrack):
    kind = "video"

    def __init__(self, camera_id: int):
        super().__init__()
        self.camera_id = camera_id

        self.cap = cv2.VideoCapture(camera_id, cv2.CAP_V4L2)
        if not self.cap.isOpened():
            raise Exception(f"Camera {camera_id} failed to open")

        # Force MJPEG → compatibility with most UVC cameras
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        logging.info(f"[Camera] Streaming from /dev/video{camera_id}")

    async def recv(self):
        ret, frame = self.cap.read()
        if not ret:
            raise Exception(f"Camera {self.camera_id} failed to read frame")

        # Log bandwidth/frame info (size and timestamp) to both console and a run-specific bandwidth file
        try:
            frame_size = frame.nbytes
        except Exception:
            frame_size = None

        log_msg = f"[Bandwidth/Frame] camera={self.camera_id} size={frame_size}B"
        logging.info(log_msg)
        # append to bandwidth log file if available
        if BANDWIDTH_LOG_PATH:
            try:
                with open(BANDWIDTH_LOG_PATH, "a", encoding="utf-8") as f:
                    f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {log_msg}\n")
            except Exception:
                logging.exception("Failed to write bandwidth log")

        frm = VideoFrame.from_ndarray(frame, format="bgr24")
        frm.pts = int(time.time() * 1_000_000)
        frm.time_base = Fraction(1, 1_000_000)
        return frm

    def stop(self):
        if self.cap.isOpened():
            self.cap.release()
        super().stop()


# ---------------------------------------------------------
# API — /offer
# ---------------------------------------------------------

async def handle_offer(request):
    params = await request.json()
    camera_id = params.get("camera_id")

    remote = request.remote
    origin = request.headers.get("Origin")
    logging.info(f"[API] /offer received for camera {camera_id} from {remote} Origin={origin}")  # <<< ADDED

    available = list_camera_indices()
    if camera_id not in available:
        return web.Response(status=404, text=f"Camera {camera_id} not available")

    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on("connectionstatechange")
    async def on_conn_change():
        logging.info(f"WebRTC state: {pc.connectionState}")
        if pc.connectionState in ("failed", "closed"):
            await pc.close()
            pcs.discard(pc)

    track = RoverCameraTrack(camera_id)
    pc.addTrack(track)

    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])
    await pc.setRemoteDescription(offer)

    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    logging.info("[API] Returning SDP answer")  # <<< ADDED

    return web.json_response(
        {
            "sdp": pc.localDescription.sdp,
            "type": pc.localDescription.type,
        },
        headers={"Access-Control-Allow-Origin": "*"}
    )


# ---------------------------------------------------------
# API — /cameras
# ---------------------------------------------------------

async def handle_cameras(request):
    remote = request.remote
    origin = request.headers.get("Origin")
    logging.info(f"[API] /cameras queried from {remote} Origin={origin}")  # <<< ADDED
    cameras = list_camera_indices()
    return web.json_response(
        {"cameras": [{"id": c, "label": f"Camera {c}"} for c in cameras]},
        headers={"Access-Control-Allow-Origin": "*"}
    )


# ---------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------

if __name__ == "__main__":
    # initialize logging (creates ./logs/<timestamp>/server.log and bandwidth log path)
    # set module-level BANDWIDTH_LOG_PATH without using 'global' to satisfy linters
    globals()["BANDWIDTH_LOG_PATH"] = setup_run_logging()

    logging.info("========================================")
    logging.info("   Rover WebRTC Camera Server Starting  ")
    logging.info("========================================")

    available = list_camera_indices()
    logging.info(f"[Startup] Cameras detected at boot: {available}")

    SERVER_IP = "192.168.40.1"

    logging.info(f"To send WebRTC offers:   http://{SERVER_IP}:3001/offer")
    logging.info(f"To list cameras:         http://{SERVER_IP}:3001/cameras")

    app = web.Application()
    app.router.add_post("/offer", handle_offer)
    app.router.add_get("/cameras", handle_cameras)

    logging.info(f"[Startup] Server listening at http://{HOST}:{PORT}")
    web.run_app(app, host=HOST, port=PORT)
