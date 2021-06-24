import math
from io import BytesIO
from PIL import Image
import aiohttp


class BadResponseError(Exception):
    """Raised when response code isn't 200."""


async def query(url, content_type):
    """
    Send a GET request to the specified url  and return the content of the reponse.

    :param content_type: 'json' or 'binary'
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                if content_type == "json":
                    return await response.json()
                if content_type == "binary":
                    return await response.read()
            raise BadResponseError("Query returned {r.status} code.")


def hex2rgba(hex_num: str):
    """
    Convert hex_num to a (R, G, B, 255) tuple containing color components represented\
    by integers between 0 and 255.
    :param hex_num: A hex color string with no leading #
    """
    rgb = tuple(int(hex_num[i : i + 2], 16) for i in (0, 2, 4))
    return (*rgb, 255)


def cooldown(num_users: int):
    """Get the cooldown when num_users users are online."""
    return 2.5 * math.sqrt(num_users + 11.96) + 6.5


async def download_image(url: str) -> Image.Image:
    """
    Download an image from a given url as an rgba PIL image.
    """
    response = await query(url, "binary")
    return Image.open(BytesIO(response)).convert("RGBA")
