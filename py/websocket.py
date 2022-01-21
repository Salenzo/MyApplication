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
    async with websockets.connect('10.10.6.91:5141') as websocket:

        await recv_level(websocket)

asyncio.get_event_loop().run_until_complete(main())
