from urllib.parse import urljoin
import asyncio
import aiohttp
import numpy as np
from .utils import hex2rgba_palette
from .image import PalettizedImage


class BadResponseError(Exception):
    """Raised when response code isn't 200."""

    pass


class Canvas:
    """
    An object meant to store info and
    manage requests to pxsl.space.
    """

    def __init__(self, base_url):
        self.base_url = base_url
        self.info = asyncio.run(self.get_info())
        self.palette = hex2rgba_palette(self.info["palette"])
        self.board = asyncio.run(self.get_board())

    async def query(self, endpoint: str, content_type: str):
        """
        Send a GET request to the endpoint and return the content of the reponse.

        :param content_type: 'json' or 'binary'
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(urljoin(self.base_url, endpoint)) as response:
                if response.status == 200:
                    if content_type == "json":
                        return await response.json()
                    if content_type == "binary":
                        return await response.read()
                raise BadResponseError("Query returned {r.status} code.")

    async def get_board(self):
        """
        Get the current canvas' board image.
        """
        response = await self.query("boarddata?", "binary")
        array = np.asarray(list(response), dtype=np.uint8).reshape(
            (self.info["height"], self.info["width"])
        )
        board_image = PalettizedImage(array)
        return board_image

    async def get_users(self):
        """Get the number of online users."""
        response_json = await self.query("users", "json")
        return response_json["count"]

    async def get_info(self):
        """Get the canvas info."""
        info = await self.query("info", "json")
        return info
