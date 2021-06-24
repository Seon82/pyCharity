from PIL import Image
import numpy as np
from aioify import aioify


class PalettizedImage:
    """
    A quantized image.
    """

    def __init__(self, array):
        self.image = array

    @aioify
    def render(self, palette):
        """
        Convert the quantized image to a PIL rgba image.
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
