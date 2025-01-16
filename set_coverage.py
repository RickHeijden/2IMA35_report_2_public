import sys

import pyspark

from datetime import datetime
from sub_modular_optimization_library import Library

SetType = frozenset[int]

def parse_file_python(file: str) -> list[SetType]:
    with open(file, 'r') as f:
        return [frozenset([int(z) for z in line.split()]) for line in f]


def parse_file_spark(
    file: str,
    sc: pyspark.SparkContext,
    min_partitions: int | None = None,
    preserves_partitioning: bool = False
) -> pyspark.RDD[tuple[SetType, int]]:
    return (sc.textFile(file, min_partitions)
            .zipWithIndex()
            .map(lambda pair: (frozenset([int(z) for z in pair[0].split()]), pair[1]), preserves_partitioning)
            )


def set_coverage(sets: set[SetType]):
    if len(sets) == 0:
        return 0
    return len(frozenset.union(*sets))


if __name__ == '__main__':
    start_time = datetime.now()
    empty_value: SetType = frozenset([-1])

    library = Library[SetType](
        parse_file_python,
        parse_file_spark,
        set_coverage,
        empty_value,
    )

    library.parse_args()
    result, algorithm_time = library.run()
    end_time = datetime.now()

    with open(library.file_name, 'r') as f:
         problem_size = len(f.readlines())

    total_time = end_time - start_time
    print(
        ';'.join([str(x) for x in [
            library.file_name.split('/')[-1],
            str(problem_size),
            str(algorithm_time),
            str(total_time),
            str(set_coverage(result))
        ]]),
        file=sys.stderr
    )

