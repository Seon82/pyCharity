import numpy as np
cimport numpy as np
import cython
from cython.parallel cimport prange

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
def fast_detemplatize(np.uint8_t[:, :, :] array, int true_height, int true_width, int block_size):

    result = np.zeros((true_height, true_width,4), dtype=np.uint8)
    cdef np.uint8_t[:, :, :] result_view = result
    
    cdef np.uint8_t red, green, blue, alpha
    
    cdef int x, y, b_y, b_x

    for y in prange(block_size*true_height, nogil=True):
        for x in range(block_size*true_width):
            alpha = array[y, x, 3]
            if alpha!=0:
                b_y = y//block_size
                b_x = x//block_size
                result_view[b_y,b_x,0] = array[y, x, 0]
                result_view[b_y,b_x,1] = array[y, x, 1]
                result_view[b_y,b_x,2] = array[y, x, 2]
                result_view[b_y,b_x,3] = alpha

    return result