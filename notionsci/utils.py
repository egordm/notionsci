from functools import partial
from typing import Callable, Iterable, Any, Dict


def filter_dict(fn: Callable[[dict], bool], d: dict) -> dict:
    return {k: v for k, v in d.items() if fn(v)}


filter_none_dict = partial(filter_dict, lambda x: x is not None)


def key_by(items: Iterable[Any], key: Callable[[Any], Any]) -> Dict[Any, Any]:
    return {key(item): item for item in items}


class ExplicitNone:
    pass


def strip_none_field(value: Any):
    if isinstance(value, list):
        return [strip_none_field(v) for v in value if v is not None]
    if isinstance(value, dict):
        return {k: strip_none_field(v) for k, v in value.items() if v is not None}
    if isinstance(value, ExplicitNone):
        return None
    return value


def flatten(t):
    return [item for sublist in t for item in sublist]
