import numpy as np
cimport numpy as np
import cython

@cython.boundscheck(False)
@cython.wraparound(False)
def fast_detemplatize(np.uint8_t[:, :, :] array, int true_height, int true_width, int block_size):

    result = np.zeros((true_height, true_width,4), dtype=np.uint8)
    cdef np.uint8_t[:, :, :] result_view = result
    
    cdef np.uint8_t red, green, blue, alpha
    
    cdef Py_ssize_t x, y, b, b_y, b_x

    for x in range(true_width):
        for y in range(true_height):
            for b in range(block_size*block_size):
                b_x = b%block_size
                b_y = b//block_size
                alpha = array[y*block_size+b_y, x*block_size+b_x, 3]
                if alpha!=0:
                    result_view[y,x,0] = array[y*block_size+b_y, x*block_size+b_x, 0]
                    result_view[y,x,1] = array[y*block_size+b_y, x*block_size+b_x, 1]
                    result_view[y,x,2] = array[y*block_size+b_y, x*block_size+b_x, 2]
                    result_view[y,x,3] = alpha
                    break

    return result