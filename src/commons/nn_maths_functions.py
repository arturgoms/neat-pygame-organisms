import math

from numpy import sqrt


def dist(x2, x1, y2, y1):
    return sqrt((x2-x1)**2 + (y2-y1)**2)


def xy_dist(x2, x1, y2, y1):
    return [x2-x1, y2-y1]


def dist_to_item(org, food):
    return dist(food.LOCATION.x, org.LOCATION.x, food.LOCATION.y, org.LOCATION.y)


def dist_between(first, second):
    return xy_dist(first.LOCATION.x, second.LOCATION.x, first.LOCATION.y, second.LOCATION.y)


def xy_dist_to_item(org1, org2):
    return xy_dist(org2.LOCATION.x, org1.LOCATION.x, org2.LOCATION.y, org1.LOCATION.y)


def rect_distance(rect1, rect2):
    x1, y1 = rect1.topleft
    x1b, y1b = rect1.bottomright
    x2, y2 = rect2.topleft
    x2b, y2b = rect2.bottomright
    left = x2b < x1
    right = x1b < x2
    top = y2b < y1
    bottom = y1b < y2
    if bottom and left:
        print('bottom left')
        return math.hypot(x2b-x1, y2-y1b)
    elif left and top:
        print('top left')
        return math.hypot(x2b-x1, y2b-y1)
    elif top and right:
        print('top right')
        return math.hypot(x2-x1b, y2b-y1)
    elif right and bottom:
        print('bottom right')
        return math.hypot(x2-x1b, y2-y1b)
    elif left:
        print('left')
        return x1 - x2b
    elif right:
        print('right')
        return x2 - x1b
    elif top:
        print('top')
        return y1 - y2b
    elif bottom:
        print('bottom')
        return y2 - y1b
    else:  # rectangles intersect
        print('intersection')
        return 0.
