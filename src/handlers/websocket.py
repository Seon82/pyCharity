import asyncio
from os import stat
import websockets
import json
import threading


class WebsocketClient:
    """
    A threaded websocket client in charge of updating the canvas board in real-time.
    """

    def __init__(self, uri: str, canvas):
        self.uri = uri
        self.canvas = canvas
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._start, daemon=True)
        self._paused = False

    def start(self):
        self.thread.start()

    def _start(self):
        self.loop.run_until_complete(self._listen())

    def pause(self):
        self._paused = True

    def resume(self):
        self._paused = False

    async def _listen(self):
        while True:
            try:
                async with websockets.connect(self.uri) as websocket:
                    print("Connected to websocket.")
                    async for message in websocket:
                        while self._paused:
                            pass
                        try:
                            data = json.loads(message)
                            if data["type"] == "pixel":
                                for update in data["pixels"]:
                                    self.canvas.update_pixel(**update)
                        except Exception as e:
                            print("Websocket client raised", e)
            except Exception as e:
                print(f"Websocket disconected: {e}")
                print("Attempting reconnect...")
