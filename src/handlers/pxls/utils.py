import math
from io import BytesIO
from typing import Optional
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


class Progress:
    """
    Template progress data container.
    """

    def __init__(self, correct: int, total: int, array: Optional[np.ndarray] = None):
        """
        :param correct: The number of correct pixels.
        :param total: The number of non-transparent, placeable pixels
        in the template.
        :param array: A numpy array showing visual progress
        (0=wrong, 1=correct, 2=not in placemap, 255=transparent).
        """
        self.correct = correct
        self.total = total
        self.array = array

    @property
    def percentage(self):
        """
        Get progress as a percentage.
        """
        return 100 * self.correct / self.total

    @property
    def remaining(self):
        """
        Get remaining pixels.
        """
        return self.total - self.correct

    def to_dict(self):
        """
        Serialize the object.
        """
        return {"correct": self.correct, "total": self.total}


@aioify
def compute_progress(canvas, template, compute_array=False) -> Progress:
    """
    Measure the completion of a template.

    :param compute_array: Wheter to attach progress_array to the returned Progress.
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
    if compute_array:
        progress_array[
            np.logical_and(np.logical_not(template_transparent), canvas_transparent)
        ] = 2
        return Progress(completed_pixels, total_pixels, progress_array)

    return Progress(completed_pixels, total_pixels)
