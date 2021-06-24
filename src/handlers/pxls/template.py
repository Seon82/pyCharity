from typing import Tuple, Dict, List
from urllib.parse import parse_qs
from PIL import Image
import numpy as np
from aioify import aioify
from .image import PalettizedImage
from .utils import download_image


class Template(PalettizedImage):
    def __init__(self, array, url, ox, oy):
        super().__init__(array)
        self.url = url
        self.ox = ox
        self.oy = oy

    @classmethod
    async def from_url(cls, url, palette):
        """
        Generate a template from a pxls.space url.
        """
        params, styled_image = await cls.process_link(url)
        rendered_image = await cls.detemplatize(styled_image, int(params["tw"][0]))
        palettized_array = await cls.reduce(rendered_image, palette)
        return cls(
            array=palettized_array,
            ox=int(params["ox"][0]),
            oy=int(params["oy"][0]),
        )

    @staticmethod
    async def process_link(
        url: str,
    ) -> Tuple[Dict[str, List[str]], Image.Image]:
        """
        Process a pxls.space template link and download the asociated image.

        :return: A dictionary contaning the template parameters and the stylized template image.
        """
        params = parse_qs(url.split("#", 1)[1])
        image = await download_image(params["template"][0])
        return params, image

    @staticmethod
    @aioify
    def detemplatize(img_raw: Image.Image, true_width: int) -> Image.Image:
        """
        Convert a styled template image back to its original version.
        """
        block_size = img_raw.width // true_width
        if true_width == -1 or block_size == 1:  # Nothing to do :)
            return img_raw
        img_raw = np.asarray(img_raw)

        blocks = img_raw.reshape(
            (
                img_raw.shape[0] // block_size,
                block_size,
                img_raw.shape[1] // block_size,
                block_size,
                4,
            )
        ).swapaxes(1, 2)
        # block -> pixel conversion
        img = np.max(blocks, axis=(2, 3))
        # Transparency sanitation
        transparency = img[:, :, 3]
        transparency[transparency < 255] = 0
        return Image.fromarray(img, mode="RGBA")

    @staticmethod
    @aioify
    def reduce(rendered_image: Image.Image, palette) -> np.ndarray:
        """
        Convert a rendered image to its palettized equivalent.
        Colors that aren't in the palette are automatically mappped to their
        nearest equivalent.
        """
        rendered_array = np.asarray(rendered_image)
        palette.append((0, 0, 0, 0))
        img = np.linalg.norm(
            np.stack([rendered_array - c for c in palette]), axis=-1
        ).argmin(axis=0)
        # Transparent pixels have code 255
        img[img == len(palette) - 1] = 255
        return img
