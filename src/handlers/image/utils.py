from io import BytesIO
import cv2
import numpy as np
from handlers.pxls.utils import query


def hex2rgba(hex_num: str):
    """
    Convert hex_num to a (R, G, B, 255) tuple containing color components represented\
    by integers between 0 and 255.
    :param hex_num: A hex color string with no leading #
    """
    rgb = tuple(int(hex_num[i : i + 2], 16) for i in (0, 2, 4))
    return (*rgb, 255)


def buffer2image(buffer: BytesIO) -> np.ndarray:
    """
    Convert a data buffer to a RGBA numpy array.
    """
    res_bgr = cv2.imdecode(np.frombuffer(buffer.read(), np.uint8), cv2.IMREAD_UNCHANGED)
    return cv2.cvtColor(res_bgr, cv2.COLOR_BGRA2RGBA)


def image2buffer(image: np.ndarray) -> BytesIO:
    """
    Convert a RGBA numpy array to a data buffer.
    """
    image_bgr = cv2.cvtColor(image, cv2.COLOR_RGBA2BGRA)
    success, img_buffer = cv2.imencode(".png", image_bgr)
    assert success is True
    return BytesIO(img_buffer)


async def download_image(url: str) -> np.ndarray:
    """
    Download an image from a given url as an rgba numpy array.
    """
    response = await query(url, "binary")
    return buffer2image(BytesIO(response))
