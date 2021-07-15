from typing import Optional
from aioify import aioify
import numpy as np


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
