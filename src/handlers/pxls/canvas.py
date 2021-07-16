from urllib.parse import urljoin
import numpy as np
from handlers.image import hex2rgba, PalettizedImage
from handlers.pxls.stats import StatsRecord
from handlers.pxls.utils import query


class Canvas:
    """
    An object meant to store info and
    manage requests to pxls.space.
    """

    def __init__(self, base_url):
        self.base_url = base_url
        self.info = {}
        self.palette = []
        self.board = None

    @property
    def code(self) -> str:
        """
        Get the canvas' code
        """
        return self.info["canvasCode"]

    async def setup(self):
        """
        Make initial requests to pxls.space.
        """
        await self.update_info()
        self.board = await self.fetch_board()

    async def query(self, endpoint: str, content_type: str):
        """
        Send a GET request to the endpoint and return the content of the reponse.

        :param content_type: 'json' or 'binary'
        """
        return await query(
            url=urljoin(self.base_url, endpoint), content_type=content_type
        )

    async def fetch_board(self) -> PalettizedImage:
        """
        Get the current canvas' board image.
        """
        response = await self.query("boarddata?", "binary")
        array = np.asarray(list(response), dtype=np.uint8).reshape(
            (self.info["height"], self.info["width"])
        )
        board_image = PalettizedImage(array)
        return board_image

    def update_pixel(self, x: int, y: int, color: int):
        """
        Update a pixel's value on the board.
        """
        self.board.image[y, x] = color

    async def fetch_users(self) -> int:
        """Get the number of online users."""
        response_json = await self.query("users", "json")
        return response_json["count"]

    async def update_info(self) -> None:
        """Update the canvas info, and update the palette."""
        self.info = await self.query("info", "json")
        self.palette = [hex2rgba(c["value"]) for c in self.info["palette"]]

    async def fetch_stats(self) -> StatsRecord:
        """Get the current stats."""
        stats_json = await self.query("stats/stats.json", "json")
        return StatsRecord.from_json(stats_json, self.code)
