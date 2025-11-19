import asyncio
import json
import logging

import cv2
from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaStreamTrack
from av import VideoFrame

CAMERA_ID = 0
HOST = '0.0.0.0'
import time
from fractions import Fraction
PORT = 3001

import glob

def auto_detect_camera():
    """
    Scan /dev/video* for the first device that can actually provide frames.
    Supports real + virtual cameras (v4l2loopback).
    """
    video_devices = sorted(glob.glob("/dev/video*"))

    for dev in video_devices:
        try:
            idx = int(dev.replace("/dev/video", ""))
            cap = cv2.VideoCapture(idx)

            if cap.isOpened():
                ret, frame = cap.read()
                cap.release()
                if ret:
                    logging.info(f"Auto-detected working device: {dev} (index {idx})")
                    print(f"[Camera] Auto-detected working device: {dev}")
                    return idx
        except:
            logging.debug(f"auto_detect_camera: failed to probe {dev}")
            pass

    raise Exception("No working video device found (physical or virtual)")


class RoverCameraTrack(MediaStreamTrack):
    kind = "video"

    def __init__(self, camera_id=0):
        super().__init__()

        # edit: try requested camera OR auto-detect
        if camera_id is None:
            camera_id = auto_detect_camera()

        self.camera_id = camera_id
        self.cap = cv2.VideoCapture(camera_id)

        # If camera_id fails, auto-detect a fallback virtual cam
        if not self.cap.isOpened():
            logging.warning(f"Camera {camera_id} failed to open, attempting auto-detect")
            print(f"[Camera] Camera {camera_id} failed, attempting auto-detect…")
            camera_id = auto_detect_camera()
            self.camera_id = camera_id
            self.cap = cv2.VideoCapture(camera_id)

        if not self.cap.isOpened():
            logging.error(f"Could not open any video device (tried {camera_id})")
            raise Exception(f"Could not open ANY video device (tried {camera_id})")

        # lower resolution for WebRTC performance
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        logging.info(f"Using camera index {self.camera_id} (320x240 capture), codec MJPG")

    async def recv(self):
        start_time = time.time()
        ret, frame = self.cap.read()
        end_time = time.time()
        log_path = "bandwidth-Logs.txt"

        if not ret:
            logging.error("Failed to grab frame from camera")
            with open(log_path, "a") as f:
                f.write("[Bandwidth/Frame] Failed to grab frame\n")
            logging.warning(f"Camera {self.camera_id}: failed to grab frame")
            raise Exception("Camera frame not available")

        frame_resized = cv2.resize(frame, (640, 480))
        frame_size = frame_resized.nbytes

        elapsed = end_time - start_time
        log_msg = f"[Bandwidth/Frame] camera={self.camera_id} size={frame_size}B acquire_time={elapsed:.4f}s\n"
        # log to terminal and file
        logging.info(log_msg.strip())
        with open(log_path, "a") as f:
            f.write(log_msg)

        new_frame = VideoFrame.from_ndarray(frame_resized, format="bgr24")
        new_frame.pts = int(time.time() * 1_000_000)
        new_frame.time_base = Fraction(1, 1_000_000)
        return new_frame

    def stop(self):
        if self.cap.isOpened():
            self.cap.release()
        super().stop()


async def offer(request):
    if request.method == "OPTIONS":
        return web.Response(status=200, headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        })

    params = await request.json()
    logging.info(f"Received offer: {json.dumps(params)[:500]}")

    camera_id = params.get("camera_id", None)  # allow auto-detect

    try:
        offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])
        pc = RTCPeerConnection()
        pcs.add(pc)

        @pc.on("connectionstatechange")
        async def on_connectionstatechange():
            logging.info(f"Connection state is {pc.connectionState}")
            if pc.connectionState in ("failed", "closed"):
                await pc.close()
                pcs.discard(pc)

        # edit: RoverCameraTrack auto-detects virtual cams
        camera_track = RoverCameraTrack(camera_id)
        pc.addTrack(camera_track)

        await pc.setRemoteDescription(offer)
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)

    except Exception as e:
        logging.error(f"Error during offer/answer: {e}")
        return web.Response(status=500, text=str(e))

    return web.Response(
        content_type="application/json",
        text=json.dumps({
            "sdp": pc.localDescription.sdp,
            "type": pc.localDescription.type
        }),
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        }
    )


pcs = set()


async def on_shutdown(app):
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()


def get_available_cameras():
    """
    Improved detection that works for:
    - USB cameras
    - Pi camera
    - v4l2loopback virtual cameras
    """
    video_devices = sorted(glob.glob("/dev/video*"))
    available = []

    for dev in video_devices:
        idx = int(dev.replace("/dev/video", ""))
        cap = cv2.VideoCapture(idx)
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            if ret:
                available.append(idx)

    return available


async def list_cameras(request):
    available = get_available_cameras()

    connected_ids = set()
    for pc in pcs:
        for transceiver in pc.getTransceivers():
            if transceiver.kind == "video" and transceiver.receiver.track:
                track = transceiver.receiver.track
                if hasattr(track, "camera_id"):
                    connected_ids.add(track.camera_id)

    camera_list = [{
        "id": idx,
        "label": f"Camera {idx}",
        "connected": idx in connected_ids
    } for idx in available]

    return web.json_response({"cameras": camera_list})


async def root(request):
    return web.Response(text="Rover WebRTC server is running.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    from aiohttp.web_middlewares import middleware

    @middleware
    async def cors_middleware(request, handler):
        response = await handler(request)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return response

    app = web.Application(middlewares=[cors_middleware])
    app.on_shutdown.append(on_shutdown)
    app.router.add_post("/offer", offer)
    app.router.add_route("OPTIONS", "/offer", offer)
    app.router.add_get("/", root)
    app.router.add_get("/cameras", list_cameras)

    # Check for available camera interfaces on startup and log helpful messages
    detected = get_available_cameras()
    if not detected:
        logging.warning("No cameras detected. Please check USB connections.")
        print("No cameras detected — please check USB connections.")
    else:
        devs = ", ".join([f"/dev/video{idx}" for idx in detected])
        logging.info(f"Detected camera interfaces: {devs}")
        print(f"Detected camera interfaces: {devs}")

    logging.info(f"Starting rover server at http://{HOST}:{PORT}")
    web.run_app(app, host=HOST, port=PORT)
