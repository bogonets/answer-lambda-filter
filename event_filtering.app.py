# -*- coding: utf-8 -*-

import sys
import time
import math
import numpy as np

# for Logging
LOGGING_PREFIX = '[event_filtering] '
LOGGING_SUFFIX = '\n'


def print_out(message):
    sys.stdout.write(LOGGING_PREFIX + message + LOGGING_SUFFIX)
    sys.stdout.flush()

def print_error(message):
    sys.stderr.write(LOGGING_PREFIX + message + LOGGING_SUFFIX)
    sys.stderr.flush()

# for box coordinates
XMIN_INDEX = 0
YMIN_INDEX = 1
XMAX_INDEX = 2
YMAX_INDEX = 3

# init
measure_time = [30]
measure_count = [10]
data_blocking_time = 30
center_distance_threshold = 0.8

# flag
time_flag = False
wating_flag = False

# for box values
box_list = []

# for time
time_list = []
wating_list = []

# for count
blocking_count_box = []

def on_set(key, val):
    if key == 'measure_time':
        global measure_time
        measure_time = int(val)
    elif key == 'measure_count':
        global measure_count
        measure_count = int(val)
    elif key == 'data_blocking_time':
        global data_blocking_time
        data_blocking_time = int(val)
    elif key == 'center_distance_threshold':
        global center_distance_threshold
        center_distance_threshold = float(val)


def on_get(key):
    if key == 'measure_time':
        return str(measure_time)
    elif key == 'measure_count':
        return str(measure_count)
    elif key == 'data_blocking_time':
        return str(data_blocking_time)
    elif key == 'center_distance_threshold':
        return str(center_distance_threshold)

def get_rect(r):
    return [r[0], r[1], r[2], r[3]]

def get_center(rect):
    center_list = []
    for rec in rect:
        x1 = rec[XMIN_INDEX]
        y1 = rec[YMIN_INDEX]
        x2 = rec[XMAX_INDEX]
        y2 = rec[YMAX_INDEX]

        w = x2 - x1
        h = y2 - y1

        cx = x1 + (w / 2)
        cy = y1 + (h / 2)

        center_list.append((cx, cy))
    return center_list

def get_distance(olds):
    standard_distance = []
    for old in olds:
        a = distance_point_to_point([old[0], old[1]], [old[2], old[3]]) / 2
        standard_distance.append(a)
    return standard_distance

def get_size(rect):
    w_list = []
    h_list = []
    for rec in rect:
        x1 = rec[XMIN_INDEX]
        y1 = rec[YMIN_INDEX]
        x2 = rec[XMAX_INDEX]
        y2 = rec[YMAX_INDEX]

        w = x2 - x1
        h = y2 - y1
        w_list.append(w)
        h_list.append(h)
    return w_list, h_list

def distance_point_to_point(p1, p2):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]

    distance = math.sqrt(dx**2 + dy**2)
    return distance

def compare (old, new, center_distance_threshold=0.8):
    old_c = get_center(old)
    new_c = get_center(new)

    standard_distance = get_distance(old)

    distance_result = list_for_comparison(old_c, new_c, standard_distance, center_distance_threshold)
    return distance_result

def find_similar_boxes(distance, threshold):
    result = []
    for dis in distance:
        for thr in threshold:
            first = True if dis <= thr else False
            result.append(first)
    return result

def list_for_comparison(olds, news, standard, threshold):

    li_threshold = [[(1-threshold) * i for i in standard]]

    li_distance = []
    for old in olds:
        for new in news:
            point = [distance_point_to_point(list(old), list(new))]
            li_distance.append(point)
    return find_similar_boxes(li_distance, li_threshold)

def replace(list_box):
    output_box = list_box[0]
    a = list_box.pop(0)
    return a

def on_run(bboxes: np.ndarray):
    global blocking_count_box
    global box_list
    global time_flag
    global wating_flag

    if isinstance(bboxes, list):
        bboxes = np.array(bboxes)
    elif not isinstance(bboxes, np.ndarray):
        assert False, "bboxes must be np,ndarray"

    boxes = [get_rect(box) for box in bboxes]

    if len(box_list) <= 1:
        box_list.append(boxes)

    if len(box_list) == 2:
        compare_result = compare(box_list[0], box_list[1], 0.8)
        for com in compare_result:
            if com == True:
                blocking_count_box.append(com)
                time_flag = True
            else:
                time_flag = False
        output_box = replace(box_list)
        a = measure_run(blocking_count_box, time_flag)
        #print_error(f'on_run - input - bbox : {bboxes}')
        if a:
            return {}
        else:
            wating_flag=False
            return {'box' : np.array(bboxes)}

# Time for measure
def measure_run(count_box, time_flag=False):
    global measure_time
    global measure_count
    global time_list
    global blocking_count_box
    global data_blocking_time
    global wating_flag
    global wating_list

    cur_t = time.time()

    if time_flag==True:
        time_list.append(cur_t)

    if len(count_box) >= 1:
        if time_checker(time_list, cur_t, measure_time, measure_count):
            wating_flag=True
            wating_list.append(cur_t)
            if wating_starter(wating_list, cur_t, data_blocking_time, wating_flag):
                time_list.clear()
                wating_list.clear()
                return False
            else:
                return True
        elif not len(time_list) == 0 and cur_t - time_list[-1] > measure_time:
            time_list.clear()
            blocking_count_box.clear()
            return False
    else:
        return False

def time_checker(time_list, cur_t, measure_time, measure_count):
    filtered = [x for x in time_list if cur_t - x <= measure_time]
    ln = len(filtered)
    return len(filtered) >= measure_count

def wating_starter(wating_list, current, blocking_time, wating_flag=False):
    filtered_check = [x for x in wating_list if current - x >= int(60*data_blocking_time)]
    if len(filtered_check) >= 1:
        return True
    else:
        return False

