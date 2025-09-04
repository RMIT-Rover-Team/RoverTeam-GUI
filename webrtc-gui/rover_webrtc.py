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
        self.cap = cv2.VideoCapture(camera_id)
        if not self.cap.isOpened():
            raise Exception(f"Could not open video source {camera_id}")

        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    async def recv(self):
        ret, frame = self.cap.read()
        if not ret:
            logging.error("Failed to grab frame from camera")
            raise Exception("Camera frame not available")
        new_frame = VideoFrame.from_ndarray(frame, format="bgr24")
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
    # Find all /dev/video* devices
    video_devices = glob.glob('/dev/video*')
    for device in video_devices:
        # Extract the index from the device name
        try:
            index = int(device.replace('/dev/video', ''))
        except ValueError:
            continue
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            available.append(index)
            cap.release()
    return available

async def list_cameras(request):
    cameras = get_available_cameras()
    return web.json_response({"cameras": cameras})

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
