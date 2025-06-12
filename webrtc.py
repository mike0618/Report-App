import asyncio
import json
import logging
from aiohttp import web
from aiohttp_cors import setup as cors_setup, ResourceOptions
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer, MediaRelay

# Use a MediaRelay to share a single webcam source across multiple connections
relay = MediaRelay()

# Camera settings
VIDEO_SIZE = "800x600"
options = {
    "video_size": VIDEO_SIZE,
}

# Create webcam instance
webcam = MediaPlayer("/dev/video0", format="v4l2", options=options)
# Track active peer connections
pcs = set()


async def offer(request):
    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    # Create WebRTC connection
    pc = RTCPeerConnection()
    pcs.add(pc)
    # Get video source and use relay to create a new track for this peer connection
    video_track = relay.subscribe(webcam.video)

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        logging.info(f"Connection state changed to: {pc.connectionState}")
        if pc.connectionState in ["failed", "closed", "disconnected"]:
            logging.info("Cleaning up connection")
            # Remove from active connections
            pcs.discard(pc)
            # Close tracks explicitly
            for sender in pc.getSenders():
                if sender.track:
                    sender.track.stop()
            # Close the connection
            await pc.close()

    # Add the relayed video track to this connection
    pc.addTrack(video_track)

    # Handle offer
    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.Response(
        content_type="application/json",
        text=json.dumps(
            {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
        ),
    )


async def on_shutdown(app):
    # Close all peer connections
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()
    # Explicitly close the webcam
    if hasattr(webcam, "video") and webcam.video:
        webcam.video.stop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Create web application
    app = web.Application()
    app.on_shutdown.append(on_shutdown)
    # Configure CORS
    cors = cors_setup(
        app,
        defaults={
            "*": ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods=["GET", "POST", "OPTIONS"],
            )
        },
    )
    resource = cors.add(app.router.add_resource("/offer"))
    cors.add(resource.add_route("POST", offer))
    # Print camera settings being used
    print("Starting WebRTC server with camera settings:")
    print(f"- Resolution: {VIDEO_SIZE}")
    print("- CORS enabled for cross-origin access")
    print("- Using MediaRelay for resource management")

    web.run_app(app, host="10.0.0.23", port=8080)
