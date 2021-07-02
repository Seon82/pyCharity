from aioify import aioify
import numpy as np
from handlers.pxls.template import BaseTemplate


@aioify
def layer(canvas_width: int, canvas_height: int, *templates) -> BaseTemplate:
    """
    Sequentially layer each of the received templates, and return the
    corresponding BaseTemplate.
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
    return BaseTemplate(background[min_y:max_y, min_x:max_x], ox=min_x, oy=min_y)
