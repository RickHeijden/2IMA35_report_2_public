from .sub_modular_spark import *


class FullSpark(SubModularSpark[T]):

    def __init__(
        self,
        file: str,
        k: int,
        epsilon: float,
        parse_func: Callable[[str, pyspark.SparkContext, Optional[int], Optional[bool]], pyspark.RDD[tuple[T, int]]],
        func: Callable[[set[T]], float],
        empty_value: T,
    ):
        super().__init__(file, k, epsilon, parse_func, func, empty_value)

    def run(self) -> set[T]:
        if self.k <= 0:
            return set()

        broadcast_func: Broadcast[bytes] = self.sc.broadcast(encode_func(self.func))
        broadcast_marginal_gain_func: Broadcast[bytes] = self.sc.broadcast(encode_func(self.marginal_gain_func))
        broadcast_reduce_3_func: Broadcast[bytes] = self.sc.broadcast(encode_func(self.reducer_3_func))
        broadcast_reducer_4_func: Broadcast[bytes] = self.sc.broadcast(encode_func(self.reducer_4_func))

        rdd: pyspark.RDD[tuple[T, int]] = self.parse_func(self.file, self.sc)
        n: int = rdd.count()
        y: int = max(math.ceil(math.log(self.k, math.e) / math.log(1 + self.epsilon, math.e)), 1)
        L: int = 1
        S: list[set[T]] = [set() for _ in range(y)]
        broadcast_k: Broadcast[int] = self.sc.broadcast(self.k)
        broadcast_epsilon: Broadcast[float] = self.sc.broadcast(self.epsilon)
        broadcast_empty_value: Broadcast[T] = self.sc.broadcast(self.emptyValue)

        mapper1: pyspark.RDD[tuple[int, T]] = (
            rdd
            .map(lambda pair: (math.ceil((int(pair[1]) + 1) / math.sqrt(n)), pair[0]))
        )

        reducer1: pyspark.RDD[tuple[int, tuple[T, float]]] = (
            mapper1
            .map(lambda a: (a[0], (a[1], use_func(broadcast_func)({a[1]}))))
            .reduceByKey(lambda a, b: a if a[1] >= b[1] else b)
        )

        max_element: tuple[T, int] = (
            reducer1
            .reduce(lambda a, b: a if a[1][1] > b[1][1] else b)
        )[1]

        reducer_2_output: Broadcast[list[T | float | set[T]]] = self.sc.broadcast([m for m in max_element] + S)

        while L <= self.k:
            reducer3: pyspark.RDD[tuple[int, list[T]]] = (
                mapper1
                .reduceByKey(
                    lambda a, b:
                    a + b if isinstance(a, list) and isinstance(b, list)
                    else a + [b] if isinstance(a, list)
                    else [a] + b if isinstance(b, list)
                    else [a] + [b]
                )
                .mapValues(
                    lambda elements: use_func(broadcast_reduce_3_func)(
                        reducer_2_output.value[2:],
                        L,
                        y,
                        elements,
                        reducer_2_output.value[1],
                        broadcast_k.value,
                        broadcast_epsilon.value,
                        use_func(broadcast_marginal_gain_func),
                        use_func(broadcast_func),
                        broadcast_empty_value.value,
                    )
                )
            )

            mapper4: pyspark.RDD[tuple[int, list[T]]] = (
                reducer3
                .map(lambda pair: (0, pair[1]))
            )

            reducer4: pyspark.RDD[tuple[int, list[T | int] | T]] = (
                mapper4
                .reduceByKey(
                    lambda a, b:
                    a + b if isinstance(a[0], list) and isinstance(b[0], list)
                    else a + [b] if isinstance(a[0], list)
                    else [a] + b if isinstance(b[0], list)
                    else [a] + [b]
                )
                .mapValues(lambda elements: use_func(broadcast_reducer_4_func)(
                    reducer_2_output.value[2:],
                    L,
                    broadcast_k.value,
                    y,
                    elements,
                    use_func(broadcast_func),
                    broadcast_empty_value.value,
                ))
            )

            result = reducer4.collect()[0][1]
            if isinstance(result, list):
                reducer_2_output = self.sc.broadcast([m for m in max_element] + result[:-1])
                L = result[-1]
            else:
                return result

        raise Exception('No valid result')
