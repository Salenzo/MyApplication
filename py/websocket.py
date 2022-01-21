import json
import base64
import asyncio
import websockets


async def recv_level(websocket):
    while True:
        recv_text = await websocket.recv()
        with open(recv_text) as f:
            level = json.load(f)
        base64Data = base64.b64encode(level)
        await websocket.send(base64Data)

async def main():
    async with websockets.serve(recv_level, "localhost", 5141):
        await asyncio.Future()

asyncio.run(main())