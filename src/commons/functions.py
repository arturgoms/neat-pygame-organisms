from math import sqrt
from typing import List, Dict, Iterable, Union
from random import gauss, random, choice, randint


def append_dict(dict_a: dict, *args: Union[List[dict], dict]) -> dict:
    """
    Appends dicts, does not handle conflicts.
    """
    new_dict = {}
    for k, v in dict_a.items():
        new_dict[k] = v
    for dictionary in args:
        for k, v in dictionary.items():
            new_dict[k] = v

    return new_dict


def ignore(iterable: Iterable, *args) -> list:
    """
    Returns the list without any elements that are in args.
    """
    return [element for element in iterable if element not in args]


def euclidian_distance(ax: float, ay: float, bx: float, by: float) -> float:
    """
    Calculates euclidian distance between two 2D points.
    """

    return sqrt(pow(ax - bx, 2) + pow(ay - by, 2))