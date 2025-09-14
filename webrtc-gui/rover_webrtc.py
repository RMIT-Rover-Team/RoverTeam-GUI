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

class RoverCameraTrack(MediaStreamTrack):
    kind = "video"

    def __init__(self, camera_id=0):
        super().__init__()
        self.camera_id = camera_id
        self.cap = cv2.VideoCapture(camera_id)
        if not self.cap.isOpened():
            raise Exception(f"Could not open video source {camera_id}")
        # NORMAL RESOLUTION
        # self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')) #video codec MJPG
        # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640) # frame width and height (640x480)
        # self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        # TESTING - LOWER RESOLUTION 
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))  # MJPEG compression
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)   # reduce width
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)  # reduce height
        self.cap.set(cv2.CAP_PROP_FPS, 15)            # lower fps

    async def recv(self):
        start_time = time.time()
        ret, frame = self.cap.read()
        end_time = time.time()
        log_path = "bandwidth-Logs.txt"
        if not ret:
            logging.error("Failed to grab frame from camera")
            log_msg = "[Bandwidth/Frame] Failed to grab frame from camera\n"
            print(log_msg.strip())
            with open(log_path, "a") as f:
                f.write(log_msg)
            raise Exception("Camera frame not available")
        # Resize frame to 640x480 before streaming
        frame_resized = cv2.resize(frame, (640, 480))
        frame_size = frame_resized.nbytes if hasattr(frame_resized, 'nbytes') else 0
        elapsed = end_time - start_time
        log_msg = f"[Bandwidth/Frame] Frame size: {frame_size} bytes, Acquisition time: {elapsed:.4f} seconds\n"
        print(log_msg.strip())
        with open(log_path, "a") as f:
            f.write(log_msg)
        if elapsed > 0.1:
            warn_msg = f"[Bandwidth/Frame] WARNING: Frame acquisition took {elapsed:.2f}s (possible bandwidth/camera issue)\n"
            print(warn_msg.strip())
            with open(log_path, "a") as f:
                f.write(warn_msg)
        new_frame = VideoFrame.from_ndarray(frame_resized, format="bgr24")
        new_frame.pts = int(time.time() * 1000000)
        new_frame.time_base = Fraction(1, 1000000)
        return new_frame

    def stop(self):
        if self.cap.isOpened():
            self.cap.release()
        super().stop()


async def offer(request):
    if request.method == "OPTIONS":
        # Respond to CORS preflight
        return web.Response(status=200, headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        })

    params = await request.json()
    logging.info(f"Received offer: {json.dumps(params)[:500]}")
    camera_id = params.get("camera_id", 0)
    try:
        offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])
        pc = RTCPeerConnection()
        pcs.add(pc)

        @pc.on("connectionstatechange")
        async def on_connectionstatechange():
            logging.info(f"Connection state is {pc.connectionState}")
            if pc.connectionState == "failed" or pc.connectionState == "closed":
                await pc.close()
                pcs.discard(pc)

        try:
            camera_track = RoverCameraTrack(camera_id=camera_id)
            pc.addTrack(camera_track)
        except Exception as cam_err:
            logging.error(f"Camera error: {cam_err}")
            return web.Response(status=500, text=f"Camera error: {cam_err}")

        await pc.setRemoteDescription(offer)
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)
    except Exception as e:
        logging.error(f"Error during offer/answer: {e}")
        return web.Response(status=500, text=str(e))

    logging.info("Returning answer to browser.")
    return web.Response(
        content_type="application/json",
        text=json.dumps({"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}),
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

import glob
def get_available_cameras():
    available = []
    max_checks = 20  # Maximum indices to check
    max_failures = 5  # Stop after this many consecutive failures
    failures = 0
    for i in range(max_checks):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None and hasattr(frame, 'size') and frame.size > 0:
                available.append(i)
                failures = 0  # Reset failures on success
            else:
                failures += 1
            cap.release()
        else:
            failures += 1
            cap.release()
        if failures >= max_failures:
            break
    return available

async def list_cameras(request):
    available = get_available_cameras()
    # Determine which cameras are currently connected via WebRTC
    connected_ids = set()
    for pc in pcs:
        for transceiver in pc.getTransceivers():
            if transceiver.kind == "video" and transceiver.receiver.track:
                track = transceiver.receiver.track
                if hasattr(track, "camera_id"):
                    connected_ids.add(track.camera_id)
    camera_list = []
    for idx in available:
        camera_list.append({
            'id': idx,
            'label': f'USB Camera {idx}',
            'connected': idx in connected_ids
        })
    return web.json_response({'cameras': camera_list})

async def root(request):
    return web.Response(text="Rover WebRTC server is running.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Add CORS support
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
    app.router.add_get("/cameras", list_cameras)  # <-- Add this line here

    logging.info(f"Starting rover server at http://{HOST}:{PORT}")
    web.run_app(app, host=HOST, port=PORT)

    import cv2
    cap = cv2.VideoCapture(CAMERA_ID)
    ret, frame = cap.read()
    print(ret, frame is not None)
    if ret:
        cv2.imshow('Test', frame)
        cv2.waitKey(0)
    cap.release()
