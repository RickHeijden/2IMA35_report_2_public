from abc import ABC, abstractmethod
from typing import Callable, Generic, ParamSpec, TypeVar

T = TypeVar('T')
P = ParamSpec('P')
U = TypeVar('U')

class SubModular(ABC, Generic[T, U, P]):
    def __init__(
        self,
        file: str,
        k: int,
        epsilon: float,
        parse_func: Callable[P, U],
        func: Callable[[set[T]], float]
    ):
        self.file = file
        self.k = k
        self.epsilon = epsilon
        self.parse_func = parse_func
        self.func = func

    @abstractmethod
    def run(self) -> set[T]:
        pass

    def marginal_gain(self, updated_set: set[T], old_set: set[T]) -> float:
        return self.marginal_gain_func(updated_set, old_set, self.func)

    @staticmethod
    def marginal_gain_func(updated_set: set[T], old_set: set[T], func: Callable[[set[T]], float]) -> float:
        return func(updated_set) - func(old_set)
