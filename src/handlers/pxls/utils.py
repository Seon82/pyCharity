from urllib.parse import urljoin, urlencode
from aioify import aioify
import numpy as np
import aiohttp


@aioify
def style_dotted(image: np.ndarray, block_size=3) -> np.ndarray:
    """
    Generate a dotted style template image from a template.

    :param block_size: The size of the transparent pixel blocks
    the origin pixel sits in the middle of. Better-looking results
    with an odd number.
    """
    img = np.asarray(image)
    styled_img = np.zeros(
        (img.shape[0] * block_size, img.shape[1] * block_size, 4), dtype=np.uint8
    )
    idx_y = [block_size // 2 + i for i in range(0, styled_img.shape[0], block_size)]
    idx_x = [block_size // 2 + i for i in range(0, styled_img.shape[1], block_size)]
    idx = tuple(np.meshgrid(idx_y, idx_x, indexing="ij"))
    styled_img[idx] = img
    return styled_img


def generate_template_url(template, base_url: str, styled_url: str) -> str:
    """
    Generate a pxls.space template link.

    :param template: The BaseTemplate we're generating the link for.
    :param base_url: The website base url (eg: https://pxls.space)
    :param styled_url: url of the styled template image.
    """
    center_x = template.width // 2 + template.ox
    center_y = template.height // 2 + template.oy
    params = {
        "x": center_x,
        "y": center_y,
        "ox": template.ox,
        "oy": template.oy,
        "oo": 1,
        "template": styled_url,
        "tw": template.width,
    }
    return urljoin(base_url, "#" + urlencode(params))


def check_template_link(url):
    """
    Make sure the template link has a valid format.
    """
    for elmt in ["://", "ox", "oy", "template", "tw"]:
        if not elmt in url:
            return False
    return True


def cooldown(num_users: int):
    """Get the cooldown when num_users users are online."""
    return 2.5 * np.sqrt(num_users + 11.96) + 6.5


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
            raise BadResponseError("Query returned {response.status} code.")
