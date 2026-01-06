import asyncio
import logging
import glob
import os
import platform
from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer

# Listen on all interfaces so LAN devices can connect
HOST = "0.0.0.0"
PORT = 3001

# Store active peer connections to prevent garbage collection
pcs = set()
# Store media players to stop them cleanly
players = {}

def setup_logging():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# ---------------------------------------------------------
# FAST CAMERA SCAN (Filesystem based, Non-blocking)
# ---------------------------------------------------------
def list_camera_indices():
    """Return only known working camera indices."""
    logging.info("[Startup] Returning known camera indices...")
    cameras = [0, 2, 4, 6, 8, 10, 12, 14]  # Your working cameras
    
    # Verify they exist
    for cam in cameras[:]:  # Copy list to iterate
        if not os.path.exists(f"/dev/video{cam}"):
            logging.warning(f"Camera video{cam} doesn't exist, removing from list")
            cameras.remove(cam)
    
    return cameras

# ---------------------------------------------------------
# CONNECTION HANDLER
# ---------------------------------------------------------
async def handle_offer(request):
    params = await request.json()
    camera_id = int(params.get("camera_id", 0))
    
    # Simple check if device file exists
    if not os.path.exists(f"/dev/video{camera_id}"):
        return web.Response(status=404, text=f"Camera {camera_id} not found")

    pc = RTCPeerConnection()
    pcs.add(pc)

    # --- PASSTHROUGH CONFIGURATION ---
    # We request MJPEG from the camera to save USB bandwidth.
    # The MediaPlayer handles reading V4L2 -> Decoding -> Passing to WebRTC
    options = {
        "format": "v4l2", 
        "video_size": "640x480", 
        "framerate": "30",
        "input_format": "mjpeg" 
    }

    try:
        player = MediaPlayer(f"/dev/video{camera_id}", format="v4l2", options=options)
        players[pc] = player
    except Exception as e:
        logging.error(f"Failed to open camera {camera_id}: {e}")
        return web.Response(status=500, text=str(e))

    # Add the track to the connection
    if player.video:
        pc.addTrack(player.video)

    @pc.on("connectionstatechange")
    async def on_conn_change():
        if pc.connectionState in ("failed", "closed"):
            await cleanup_pc(pc)

    # Standard WebRTC Signaling
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])
    await pc.setRemoteDescription(offer)

    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.json_response({
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type,
    })

async def cleanup_pc(pc):
    """Stop the media player and close the connection."""
    if pc in players:
        player = players[pc]
        if player:
            player.stop()
        del players[pc]
    
    await pc.close()
    pcs.discard(pc)

async def handle_cameras(request):
    cameras = list_camera_indices()
    return web.json_response({
        "cameras": [{"id": c, "label": f"Camera {c}"} for c in cameras]
    })

# ---------------------------------------------------------
# CORS MIDDLEWARE
# ---------------------------------------------------------
@web.middleware
async def cors_middleware(request, handler):
    if request.method == "OPTIONS":
        # Preflight request - respond with CORS headers
        return web.Response(
            status=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Max-Age": "86400",  # 24 hours
            }
        )
    
    # Handle actual request
    response = await handler(request)
    
    # Add CORS headers to the response
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    
    return response

# ---------------------------------------------------------
# SERVER SETUP
# ---------------------------------------------------------
async def on_shutdown(app):
    coros = [cleanup_pc(pc) for pc in set(pcs)]
    await asyncio.gather(*coros)

if __name__ == "__main__":
    setup_logging()
    
    app = web.Application(middlewares=[cors_middleware])
    
    app.router.add_post("/offer", handle_offer)
    app.router.add_get("/cameras", handle_cameras)
    
    # Handle OPTIONS requests for all routes
    app.router.add_route("*", "/{tail:.*}", lambda request: web.Response(
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        }
    ) if request.method == "OPTIONS" else web.Response(status=405))
    
    app.on_shutdown.append(on_shutdown)

    logging.info(f"Rover WebRTC Server running on http://{HOST}:{PORT}")
    web.run_app(app, host=HOST, port=PORT)
