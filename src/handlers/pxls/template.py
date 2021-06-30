from typing import Tuple, Dict, List
from urllib.parse import parse_qs
from PIL import Image
import numpy as np
from aioify import aioify
from .canvas import Canvas
from .image import PalettizedImage
from .utils import download_image, compute_progress, Progress


class BaseTemplate(PalettizedImage):
    """
    A low-level object meant to represent the essential information
    contained in a template.
    """

    def __init__(self, array, ox, oy):
        super().__init__(array)
        self.ox = ox
        self.oy = oy

    @classmethod
    async def from_url(cls, template_url: str, canvas: Canvas):
        """
        Generate a template from a pxls.space url.
        """
        params, styled_image = await cls.process_link(template_url)
        rendered_image = await cls.detemplatize(styled_image, int(params["tw"][0]))
        palettized_array = await cls.reduce(rendered_image, canvas.palette)
        ox, oy = int(params["ox"][0]), int(params["oy"][0])
        palettized_array, ox, oy = cls.crop_to_canvas(palettized_array, ox, oy, canvas)
        return cls(array=palettized_array, ox=ox, oy=oy)

    @staticmethod
    def crop_to_canvas(
        array: np.ndarray, ox: int, oy: int, canvas: Canvas
    ) -> Tuple[np.ndarray, int, int]:
        """
        Crop a numpy array to the canvas boundaries.

        :return: array, x, y -> array is the cropped array, and x and y the new ox and oy values.
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
        if true_width <= 0 or img_raw.width // true_width == 1:  # Nothing to do :)
            return img_raw
        block_size = img_raw.width // true_width
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
        palette = palette.copy()
        rendered_array = np.asarray(rendered_image)
        palette.append((0, 0, 0, 0))
        palette = np.array(palette, dtype=np.uint8)
        # Don't try to vectorize this, using np.stack and argmin
        # uses a crazy amount of memory and is a tad slower on real images.
        best_match_idx = np.zeros(rendered_array.shape[:2], dtype=np.uint8)
        best_match_dist = np.full(rendered_array.shape[:2], 500)  # 500<sqrt(3*255^2)
        for idx, color in enumerate(palette):
            color_distance = np.linalg.norm(rendered_array - color, axis=-1)
            closer_mask = color_distance < best_match_dist
            best_match_dist[closer_mask] = color_distance[closer_mask]
            best_match_idx[closer_mask] = idx
        # Transparent pixels have code 255
        best_match_idx[best_match_idx == len(palette) - 1] = 255
        return best_match_idx


class Template(BaseTemplate):
    """
    An object made to represent a template from the tracker.
    """

    def __init__(
        self,
        array: np.ndarray,
        ox: int,
        oy: int,
        name: str,
        url: str,
        canvas_code: str,
        owner: int,
        scope: str,
        progress: Progress,
    ):
        """
        :param array: A palettized array representing the template image.
        :ox: The x position of the template's top-left corner on the canvas.
        :param oy: The y position of the template's top-left corner on the canvas.
        :param name: The template's name.
        :param url: A pxls.space link to the original template.
        :param canavs_code: The canvas this template belong to.
        :param owner: The id of the faction or user owning this template.
        :param scope: The type of the owner: 'faction'|'user',
        :param progress: The template's progress state.
        """
        super().__init__(array, ox, oy)
        self.name = name
        self.url = url
        self.owner = owner
        self.scope = scope
        self.canvas_code = canvas_code
        self.progress = progress

    # pylint: disable = arguments-differ
    @classmethod
    async def from_url(
        cls, url: str, canvas: Canvas, name: str, owner: int, scope: str
    ):
        """
        Generate a template from a pxls.space url.

        :param url: A pxls.space template link.
        :param canvas: The template's canvas.
        :param name: The template's name.
        :param owner: The owner id.
        :param scope: 'global'|'faction'|'private'
        """
        base_template = await BaseTemplate.from_url(url, canvas)
        return await cls.from_base(
            base_template=base_template,
            name=name,
            url=url,
            canvas=canvas,
            owner=owner,
            scope=scope,
        )

    @classmethod
    async def from_base(
        cls,
        base_template: BaseTemplate,
        name: str,
        url: str,
        canvas: Canvas,
        owner: int,
        scope: str,
    ):
        """
        Create a Template from a BaseTemplate.
        """
        progress = await compute_progress(canvas, base_template)
        return cls(
            array=base_template.image,
            ox=base_template.ox,
            oy=base_template.oy,
            name=name,
            url=url,
            owner=owner,
            canvas_code=canvas.info["canvasCode"],
            scope=scope,
            progress=progress,
        )
