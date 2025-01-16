from typing import Optional

import cloudpickle
import math
import os
import pyspark
import random

from pyspark import Broadcast
from .sub_modular import *


os.environ['PYSPARK_PYTHON'] = "../.venv/Scripts/python.exe"


def encode_func(func: Callable) -> bytes:
    return cloudpickle.dumps(func)


def use_func(b: Broadcast[bytes]) -> Callable:
    return cloudpickle.loads(b.value)


class SubModularSpark(SubModular[T, [str, pyspark.SparkContext, Optional[int], Optional[bool]], pyspark.RDD[tuple[str, int]]], ABC):

    def __init__(
        self,
        file: str,
        k: int,
        epsilon: float,
        parse_func: Callable[[str, pyspark.SparkContext, Optional[int], Optional[bool]], pyspark.RDD[tuple[T, int]]],
        func: Callable[[set[T]], float],
        empty_value: T,
        create_spark_context: bool = True,
    ):
        super().__init__(file, k, epsilon, parse_func, func)
        self.emptyValue = empty_value
        if create_spark_context:
            conf = pyspark.SparkConf().setAppName('MST_Algorithm').setMaster('local[*]')
            self.sc = pyspark.SparkContext.getOrCreate(conf=conf)
            self.sc.setLogLevel('OFF')

    @staticmethod
    def reducer_3_func(
        sets: list[set[T]],
        L: int,
        y: int,
        elements: list[T],
        f_max: int,
        k: int,
        epsilon: float,
        marginal_gain_func: Callable[[set[T], set[T], Callable[[set[T]], float]], float],
        func: Callable[[set[T]], float],
        empty_value: T,
    ) -> list[T]:
        if not isinstance(elements, list):
            elements = [elements]

        result: list[T] = []
        found_element: bool
        constant_threshold: float = f_max / (2.0 * k)

        if L <= k:
            for j in range(y):
                threshold: float = (math.pow(1 + epsilon, j) * constant_threshold)
                found_element = False
                random.shuffle(elements)
                for e in elements:
                    updated_set: set[T] = sets[j].copy()
                    updated_set.add(e)
                    if marginal_gain_func(updated_set, sets[j], func) >= threshold:
                        result.append(e)
                        found_element = True
                        break
                if not found_element:
                    result.append(empty_value)
        return result

    @staticmethod
    def reducer_4_func(
        sets: list[set[T]],
        L: int,
        k: int,
        y: int,
        elements: list[list[T]],
        func: callable,
        empty_value: T,
    ) -> list[set[T] | int] | T:
        new_elements = [list() for _ in range(y)]
        for e in elements:
            for i in range(y):
                new_elements[i].append(e[i])

        for i in range(y):
            new_elements[i] = [e for e in filter(lambda x : x != empty_value, new_elements[i])]
            if len(new_elements[i]) == 0:
                continue

            # Add random element from elements to sets[i]
            random_index = random.randrange(len(new_elements[i]))
            sets[i].add(new_elements[i][random_index])
        if L < k:
            return sets + [L + 1]
        return max(sets, key=func)
