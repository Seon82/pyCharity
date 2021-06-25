from typing import Tuple, Dict, List
from urllib.parse import parse_qs
from PIL import Image
import numpy as np
from aioify import aioify
from handlers.pxls.canvas import Canvas
from .image import PalettizedImage
from .utils import download_image


class BaseTemplate(PalettizedImage):
    def __init__(self, array, ox, oy):
        super().__init__(array)
        self.ox = ox
        self.oy = oy

    @classmethod
    async def from_url(cls, template_url, canvas, *args, **kwargs):
        """
        Generate a template from a pxls.space url.
        """
        params, styled_image = await cls.process_link(template_url)
        rendered_image = await cls.detemplatize(styled_image, int(params["tw"][0]))
        palettized_array = await cls.reduce(rendered_image, canvas.palette)
        ox, oy = int(params["ox"][0]), int(params["oy"][0])
        palettized_array, ox, oy = cls.crop_to_canvas(palettized_array, ox, oy, canvas)
        return cls(array=palettized_array, ox=ox, oy=oy, *args, **kwargs)

    @staticmethod
    def crop_to_canvas(array: np.ndarray, ox: int, oy: int, canvas: Canvas):
        """
        Crop a numpy array to the canvas boundaries.
        """
        min_x = 0 if ox > 0 else -ox
        min_y = 0 if oy > 0 else -oy
        array = array[min_y:, min_x:]
        x, y = max(0, ox), max(0, oy)
        if y + array.shape[0] > canvas.board.height:
            height = canvas.board.height - y
        else:
            height = array.shape[0]
        if x + array.shape[1] > canvas.board.width:
            width = canvas.board.width - x
        else:
            width = array.shape[1]
        array = array[:height, :width]
        return array, x, y

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


class Template(BaseTemplate):
    def __init__(self, array, ox, oy, name, url, owner):
        super().__init__(array, ox, oy)
        self.name = name
        self.url = url
        self.owner = owner

    @classmethod
    async def from_url(cls, url: str, canvas: Canvas, name: str, owner: int):
        """
        Generate a template from a pxls.space url.

        :param url: A pxls.space template link.
        :param name: The template's name.
        :param owner: The guild id.
        :param palette: The canvas' palette.
        """
        return await super().from_url(
            template_url=url,
            canvas=canvas,
            name=name,
            url=url,
            owner=owner,
        )
