from functools import partial
from operator import is_not
from typing import Callable, Iterable, Any, Dict, Union


def filter_dict(fn: Callable[[dict], bool], d: dict) -> dict:
    return {k: v for k, v in d.items() if fn(v)}


filter_none_dict = partial(filter_dict, lambda x: x is not None)


def key_by(
        items: Iterable[Any], key: Union[Callable[[Any], Any], str]
) -> Dict[Any, Any]:
    if isinstance(key, str):
        attr = key
        key = lambda x: getattr(x, attr)
    return {key(item): item for item in items}


def flatten(t):
    return [item for sublist in t for item in sublist]


not_none = partial(is_not, None)


def filter_not_none(items):
    return list(filter(not_none, items))
