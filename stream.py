import asyncio
import websockets
import subprocess


async def stream_video(websocket, path):
    # Start the GStreamer pipeline to receive the video stream over TCP
    gst_command = [
        "gst-launch-1.0",
        "tcpclientsrc",
        "host=10.0.0.23",
        "port=8080",
        "!",
        "decodebin",
        "!",
        "videoconvert",
        "!",
        "x264enc",
        "!",
        "rtph264pay",
        "!",
        "appsink",
    ]

    gst_process = subprocess.Popen(
        gst_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    while True:
        # Read the video stream and send it over WebSocket
        data = gst_process.stdout.read(1024)  # adjust buffer size as needed
        if data:
            await websocket.send(data)


async def main():
    async with websockets.serve(stream_video, "localhost", 8765):
        print("Server started on ws://localhost:8765")
        await asyncio.Future()  # Run server indefinitely


asyncio.run(main())
