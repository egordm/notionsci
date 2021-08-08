from functools import partial
from typing import Callable


def filter_dict(fn: Callable[[dict], bool], d: dict) -> dict:
    return {
        k: v for k, v in d.items() if fn(v)
    }


filter_none_dict = partial(filter_dict, lambda x: x is not None)
