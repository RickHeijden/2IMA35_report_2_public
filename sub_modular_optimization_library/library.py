import sys

from argparse import ArgumentParser
from asyncio import InvalidStateError
from datetime import datetime

from typing import Literal, get_args, cast

from .algorithms import *

AlgorithmType = Literal['pure_python', 'full_spark', 'single_partition', 'single_slice', 'intermediate_collect', 'config']
def is_algorithm_type(value: str) -> bool:
    return value in get_args(AlgorithmType)
def get_algorithm_type_or_throw(value: str) -> AlgorithmType:
    if is_algorithm_type(value):
        return cast(AlgorithmType, value)
    else:
        raise ValueError(f'Invalid algorithm type: {value}')

class SubModularOptimizationLibrary(Generic[T]):
    file_name: str
    algorithm_name: str
    k: int
    epsilon: float

    def __init__(
        self,
        parse_file_python: Callable[[str], list[T]],
        parse_file_spark: Callable[[str, pyspark.SparkContext, Optional[int], Optional[bool]], pyspark.RDD[tuple[T, int]]],
        func: Callable[[set[T]], float],
        empty_value: T,
    ):
        self.parse_file_python = parse_file_python
        self.parse_file_spark = parse_file_spark
        self.func = func
        self.empty_value = empty_value
        self.parsed_args = False

    def parse_args(
        self,
        file_name_default: str = 'Data/example.dat',
        algorithm_name_default: AlgorithmType = 'pure_python',
        k_default: int = 3,
        epsilon_default: float = 0.5,
    ):
        parser = ArgumentParser()
        parser.add_argument('--file', help='The file to run the program on.', type=str, default=file_name_default)
        parser.add_argument('--algorithm', help='The algorithm to use.', type=str, default=algorithm_name_default)
        parser.add_argument('--k', help='The k to run the algorithm for.', type=int, default=k_default)
        parser.add_argument('--epsilon', help='The epsilon to run the algorithm for', type=float, default=epsilon_default)
        args = parser.parse_args()

        self.file_name: str = args.file
        self.algorithm_name: AlgorithmType = get_algorithm_type_or_throw(args.algorithm.lower())
        self.k: int = args.k
        self.epsilon: float = args.epsilon

        self.parsed_args = True

    def run(self):
        if not self.parsed_args:
            raise InvalidStateError('parse_args must be called before run')

        algorithm: SubModular[T, P, U]

        if self.algorithm_name == 'pure_python':
            algorithm = PurePython[T](self.file_name, self.k, self.epsilon, self.parse_file_python, self.func)
        elif self.algorithm_name == 'full_spark':
            algorithm = FullSpark[T](self.file_name, self.k, self.epsilon, self.parse_file_spark, self.func, self.empty_value)
        elif self.algorithm_name == 'single_partition':
            algorithm = SinglePartition[T](self.file_name, self.k, self.epsilon, self.parse_file_spark, self.func, self.empty_value)
        elif self.algorithm_name == 'single_slice':
            algorithm = SingleSlice[T](self.file_name, self.k, self.epsilon, self.parse_file_spark, self.func, self.empty_value)
        elif self.algorithm_name == 'intermediate_collect':
            algorithm = IntermediateCollect[T](self.file_name, self.k, self.epsilon, self.parse_file_spark, self.func, self.empty_value)
        elif self.algorithm_name == 'config':
            algorithm = Config[T](self.file_name, self.k, self.epsilon, self.parse_file_spark, self.func, self.empty_value)
        else:
            print('Invalid algorithm name')
            sys.exit(1)

        start_algorithm = datetime.now()
        result = algorithm.run()
        end_algorithm = datetime.now()
        print('result: ', result)
        return result, end_algorithm - start_algorithm
