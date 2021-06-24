from urllib.parse import urljoin
import asyncio
import aiohttp
from aioify import aioify
import numpy as np
from PIL import Image
from .utils import hex2rgba_palette


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

    @aioify
    def _parse_binary_board(self, data):
        colors_dict = dict(enumerate(self.palette))
        colors_dict[255] = (0, 0, 0, 0)
        sort_idx = list(range(len(colors_dict)))
        arr = list(data)
        idx = np.searchsorted(sort_idx, arr, sorter=sort_idx)
        out = np.asarray(list(colors_dict.values()), dtype=np.uint8)[sort_idx][idx]
        img = out.reshape((self.info["height"], self.info["width"], 4))
        return Image.fromarray(img, mode="RGBA")

    async def get_board(self):
        """
        Get the current canvas' board image.
        """
        response = await self.query("boarddata?", "binary")
        board_image = await self._parse_binary_board(response)
        return board_image

    async def get_users(self):
        """Get the number of online users."""
        response_json = await self.query("users", "json")
        return response_json["count"]

    async def get_info(self):
        """Get the canvas info."""
        info = await self.query("info", "json")
        return info
