import copy
import math
import random
from .sub_modular import *


class PurePython(SubModular[T, [str], list[T]]):

    def __init__(self, file: str, k: int, epsilon: float, parse_func: Callable[[str], list[T]], func: Callable[[set[T]], float]):
        super().__init__(file, k, epsilon, parse_func, func)

    def run(self) -> set[T]:
        V: list[T] = self.parse_func(self.file)
        n: int = len(V)
        y: int = math.ceil(math.log(self.k, math.e) / math.log(1 + self.epsilon, math.e))

        e_max, f_max = self.calculate_max_e(V, n)
        constant_threshold: float = f_max / (2.0 * self.k)

        sets: list[set[T]] = [set() for _ in range(y)]

        for j in range(y):
            L: int = 1
            threshold: float = (math.pow(1 + self.epsilon, j) * constant_threshold)

            elements: list[T] = copy.deepcopy(V)
            random.shuffle(elements)
            while L <= self.k:
                for e in elements:
                    updated_set: set[T] = sets[j].copy()
                    updated_set.add(e)
                    if self.marginal_gain(updated_set, sets[j]) >= threshold:
                        sets[j].add(e)
                        elements.remove(e)
                        break
                L += 1

        return max(sets, key=self.func)

    def calculate_max_e(self, V: list[T], n: int) -> tuple[T, float]:
        e_max, f_max = V[0], self.func({V[0]})
        for i in range(1, n):
            e, fe = V[i], self.func({V[i]})
            if fe > f_max:
                e_max, f_max = e, fe

        return e_max, f_max
