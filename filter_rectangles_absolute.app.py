# -*- coding: utf-8 -*-

import sys
import numpy as np


LOGGING_PREFIX = '[filter.rectangles_absolute] '
LOGGING_SUFFIX = '\n'

min_w = 0
min_h = 0
max_w = 0
max_h = 0
min_x1 = 0
min_y1 = 0
max_x2 = 0
max_y2 = 0
dw = 0
dh = 0
verbose = False


def print_out(message):
    sys.stdout.write(LOGGING_PREFIX + message + LOGGING_SUFFIX)
    sys.stdout.flush()


def print_error(message):
    sys.stderr.write(LOGGING_PREFIX + message + LOGGING_SUFFIX)
    sys.stderr.flush()


def on_set(key, val):
    if key == 'min_w':
        global min_w
        min_w = int(val)
    elif key == 'min_h':
        global min_h
        min_h = int(val)
    elif key == 'max_w':
        global max_w
        max_w = int(val)
    elif key == 'max_h':
        global max_h
        max_h = int(val)
    elif key == 'min_x1':
        global min_x1
        min_x1 = int(val)
    elif key == 'min_y1':
        global min_y1
        min_y1 = int(val)
    elif key == 'max_x2':
        global max_x2
        max_x2 = int(val)
    elif key == 'max_y2':
        global max_y2
        max_y2 = int(val)
    elif key == 'dw':
        global dw
        dw = int(val)
    elif key == 'dh':
        global dh
        dh = int(val)
    elif key == 'verbose':
        global verbose
        verbose = val.lower() in ['y', 'yes', 'true']


def on_get(key):
    if key == 'min_w':
        return min_w
    elif key == 'min_h':
        return min_h
    elif key == 'max_w':
        return max_w
    elif key == 'max_h':
        return max_h
    elif key == 'min_x1':
        return min_x1
    elif key == 'min_y1':
        return min_y1
    elif key == 'max_x2':
        return max_x2
    elif key == 'max_y2':
        return max_y2
    elif key == 'dw':
        return str(dw)
    elif key == 'dh':
        return str(dh)
    elif key == 'verbose':
        return str(verbose)


def is_filtering(x1, y1, x2, y2):
    w = x2 - x1
    h = y2 - y1
    if min_w != 0 and w < min_w:
        return True
    elif min_h != 0 and h < min_h:
        return True
    elif max_w != 0 and w > max_w:
        return True
    elif max_h != 0 and h > max_h:
        return True
    elif min_x1 != 0 and x1 < min_x1:
        return True
    elif min_y1 != 0 and y1 < min_y1:
        return True
    elif max_x2 != 0 and x2 > max_x2:
        return True
    elif max_y2 != 0 and y2 > max_y2:
        return True
    elif dw != 0 and w-h < dw:
        return True
    elif dh != 0 and h-w < dh:
        return True
    return False


def on_run(rectangles: np.ndarray):
    rectangles_rank = len(rectangles.shape)

    if verbose:
        print_out(f'Original rectangles: {rectangles}')

    if rectangles_rank == 0:
        if verbose:
            print_out(f'Result rectangles(rectangles_rank={rectangles_rank}): {rectangles}')
        return {'result': rectangles}

    if rectangles_rank == 1:
        assert rectangles.shape[0] >= 4
        if is_filtering(*rectangles[0:4]):
            if verbose:
                print_out(f'Result rectangles: []')
            return {'result': np.array([], dtype=rectangles.dtype)}
        else:
            if verbose:
                print_out(f'Result rectangles: {rectangles}')
            return {'result': rectangles}

    assert rectangles_rank == 2
    assert rectangles.shape[0] >= 1
    assert rectangles.shape[1] >= 4

    remove_list = []
    for i in range(rectangles.shape[0]):
        if is_filtering(*rectangles[i][0:4]):
            remove_list.append(i)

    result = np.delete(rectangles, remove_list, axis=0)
    if verbose:
        print_out(f'Result rectangles: {result}')

    return {'result': result}


if __name__ == '__main__':
    pass
