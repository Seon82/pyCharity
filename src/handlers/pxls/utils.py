import math
from io import BytesIO
from PIL import Image
import aiohttp
from aioify import aioify
import numpy as np
from .image import PalettizedImage


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


def check_template_link(url):
    """
    Make sure the template link has a valid format.
    """
    for elmt in ["://", "ox", "oy", "template", "tw"]:
        if not elmt in url:
            return False
    return True


@aioify
def layer(canvas_width: int, canvas_height: int, *templates) -> PalettizedImage:
    """
    Sequentially layer each of the received templates, and return the
    corresponding PalettizedImage.
    """
    background = np.full((canvas_height, canvas_width), 255, np.uint8)
    max_x, max_y = 0, 0
    min_x, min_y = canvas_width, canvas_height
    for template in templates:
        ox, oy = template.ox, template.oy
        mask = template.image != 255
        background[oy : oy + template.height, ox : ox + template.width][
            mask
        ] = template.image[mask]
        min_x = min(ox, min_x)
        min_y = min(oy, min_y)
        max_x = max(ox + template.width, max_x)
        max_y = max(oy + template.height, max_y)
    return PalettizedImage(background[min_y:max_y, min_x:max_x])


@aioify
def progress(canvas, template):
    """
    Measure the completion of a template.

    :return: (progress_array, (completed_pixels, total_pixels).
    progress_array is a np.ndarray containing 1 where the template pixels are correct on
    the canvas and 0 elsewhere.
    completed_pixels in the amound of completed non-transparent pixels, and total_pixels
    the total number of non-transparent pixels the template contains.
    """
    ox, oy = template.ox, template.oy
    canvas_section = canvas.board.image[
        oy : oy + template.height, ox : ox + template.width
    ]
    template_transparent = template.image == 255
    canvas_transparent = canvas_section == 255
    mask = np.logical_or(template_transparent, canvas_transparent)
    progress_array = (canvas_section == template.image).astype(np.uint8)
    progress_array[mask] = 255
    transparent_num = np.count_nonzero(mask)
    completed_pixels = np.count_nonzero(progress_array) - transparent_num
    total_pixels = canvas_section.size - transparent_num
    return progress_array, (completed_pixels, total_pixels)
