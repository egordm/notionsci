from typing import Iterable, List, TypeVar, Optional, Union

T = TypeVar('T')


def take_1(x: Union[Iterable[T], List[T]]) -> Optional[T]:
    return next(iter(x), None)
