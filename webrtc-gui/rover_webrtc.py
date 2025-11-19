import asyncio
import json
import logging
import cv2
import glob
import time
from fractions import Fraction

from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaStreamTrack
from av import VideoFrame


HOST = "0.0.0.0"
PORT = 3001
pcs = set()


# ---------------------------------------------------------
# CAMERA ENUMERATION — reliable and clean
# ---------------------------------------------------------

def list_camera_indices():
    """Return only real cameras that can deliver frames."""
    cameras = []

    for dev in sorted(glob.glob("/dev/video*")):
        idx = int(dev.replace("/dev/video", ""))

        # Skip loopback virtual cams
        try:
            name = open(f"/sys/class/video4linux/video{idx}/name").read().strip()
            if "loopback" in name.lower():
                continue
        except:
            continue

        cap = cv2.VideoCapture(idx)
        if not cap.isOpened():
            continue

        ret, _ = cap.read()
        cap.release()

        if ret:
            cameras.append(idx)

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
    cameras = list_camera_indices()
    return web.json_response(
        {"cameras": [{"id": c, "label": f"Camera {c}"} for c in cameras]},
        headers={"Access-Control-Allow-Origin": "*"}
    )


# ---------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    app = web.Application()
    app.router.add_post("/offer", handle_offer)
    app.router.add_get("/cameras", handle_cameras)

    print(f"Starting WebRTC server at http://{HOST}:{PORT}")
    web.run_app(app, host=HOST, port=PORT)
