from PIL import Image
import numpy as np
from aioify import aioify


class PalettizedImage:
    """
    A object used to represent a quantized image in a memory-efficient format.
    At its core, this object is a numpy array containing the indexes of colors.
    """

    def __init__(self, array):
        self.image = array

    @aioify
    def render(self, palette: list) -> Image.Image:
        """
        Convert the quantized image to a PIL rgba image.
        Any color index present in the palettized image but not referenced in the array will be mapped to (0,0,0,0).

        :param palette: The palette used to render.
        """
        colors_dict = dict(enumerate(palette))
        colors_dict[255] = (0, 0, 0, 0)
        img = np.stack(np.vectorize(colors_dict.get)(self.image), axis=-1)
        img = img.astype(np.uint8)
        return Image.fromarray(img, mode="RGBA")

    @property
    def width(self):
        """Get the image's width."""
        return self.image.shape[1]

    @property
    def height(self):
        """Get the image's height."""
        return self.image.shape[0]
