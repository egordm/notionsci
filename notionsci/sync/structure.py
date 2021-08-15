from abc import abstractmethod
from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import TypeVar, Generic, Optional, Dict, List, Iterable, Callable

A = TypeVar('A')
B = TypeVar('B')


class ActionType(Enum):
    IGNORE = 'IGNORE',
    PUSH = 'PUSH',
    DELETE = 'DELETE'
    MERGE = 'MERGE'


class ActionTarget(Enum):
    A = 'A',
    B = 'B'


@dataclass
class Action(Generic[A, B]):
    action_type: ActionType
    target: Optional[ActionTarget] = None
    a: Optional[A] = None
    b: Optional[B] = None

    def is_create(self):
        return self.action_type == ActionType.PUSH and (
                (self.target == ActionTarget.B and not self.b) or
                (self.target == ActionTarget.A and not self.a)
        )

    @staticmethod
    def ignore() -> 'Action[A, B]':
        return Action(ActionType.IGNORE)

    @staticmethod
    def push(target: ActionTarget, a: Optional[A] = None, b: Optional[B] = None) -> 'Action[A, B]':
        return Action(ActionType.PUSH, target, a, b)

    @staticmethod
    def delete(target: ActionTarget, a: Optional[A] = None, b: Optional[B] = None) -> 'Action[A, B]':
        return Action(ActionType.DELETE, target, a, b)


class Sync(Generic[A, B]):
    def sync(self):
        items_a = self.fetch_items_a()
        items_b = self.fetch_items_b()

        keys = list({*items_a.keys(), *items_b.keys()})
        items_a, items_b, keys = self.preprocess(items_a, items_b, keys)
        actions = [
            self.compare(items_a.get(key, None), items_b.get(key, None))
            for key in keys
        ]
        # TODO: apply topo sort on resulting graph

        print('Executing actions')
        for a in actions:
            if a.target == ActionTarget.A:
                self.execute_a(a)
            elif a.target == ActionTarget.B:
                self.execute_b(a)

    def preprocess(self, items_a: Dict[str, A], items_b: Dict[str, B], keys: List[str]):
        return items_a, items_b, keys

    @abstractmethod
    def fetch_items_a(self) -> Dict[str, A]:
        pass

    @abstractmethod
    def fetch_items_b(self) -> Dict[str, B]:
        pass

    def compare(self, a: Optional[A], b: Optional[A]) -> Action[A, B]:
        if a is None or b is None:
            return Action.push(ActionTarget.A if not a else ActionTarget.B, a, b)
        return None

    def execute_a(self, action: Action[A, B]):
        raise Exception('Action is unsupported during one way sync')

    def execute_b(self, action: Action[A, B]):
        raise Exception('Action is unsupported during one way sync')


T = TypeVar('T')


def topo_sort(xs: List[T], children_fn: Callable[[T], Iterable[T]]) -> List[T]:
    depth = 0
    counter = {}
    q = deque(xs)
    while len(q) > 0:
        x = q.popleft()
        counter[x] = max(depth, counter.get(x, 0))
        depth += 1

        children = children_fn(x)
        q.extend(children)
    return sorted(counter.keys(), key=lambda x: counter[x])
