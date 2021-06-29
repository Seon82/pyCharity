import asyncio
import logging
import json
import threading
import websockets


logger = logging.getLogger("pyCharity." + __name__)


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
        """Start the websocket in a separate thread."""
        self.thread.start()

    def _start(self):
        self.loop.run_until_complete(self._listen())

    def pause(self):
        """Pause all websocket processing."""
        self._paused = True

    def resume(self):
        """Resume all websocket processing."""
        self._paused = False

    async def _listen(self):
        while True:
            try:
                async with websockets.connect(self.uri) as websocket:
                    logger.info("Connected to websocket.")
                    async for message in websocket:
                        while self._paused:
                            pass
                        try:
                            data = json.loads(message)
                            if data["type"] == "pixel":
                                for update in data["pixels"]:
                                    self.canvas.update_pixel(**update)
                        except Exception as error:
                            logger.warning(f"Websocket client raised {error}")
            except Exception as error:
                logger.warning(f"Websocket disconnected: {error}")
                logger.info("Attempting reconnect...")
