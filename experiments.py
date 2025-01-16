import os, subprocess
from typing import TextIO

def run(python_file: str, args):
    result: str = subprocess.run(
        ['../.venv/Scripts/python.exe', python_file] + args,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True
    ).stderr
    result: list[str] = result.split('\n')
    result: list[str] = list(filter(lambda x: x != '' and ';' in x and 'WARN' not in x, result))
    return result

def run_experiment(python_file: str, file: str, algorithm: str, k: str, epsilon: str) -> list[str]:
    args = []
    args.append('--file')
    args.append(file)
    args.append('--algorithm')
    args.append(algorithm)
    args.append('--k')
    args.append(k)
    args.append('--epsilon')
    args.append(epsilon)

    result = run(python_file, args)
    print(result)

    return result

def main():
    python_files = ['set_coverage.py', 'matrix.py']

    possible_algorithms = [
        'PURE_PYTHON',
        'FULL_SPARK',
        'INTERMEDIATE_COLLECT',
        'CONFIG',
        'SINGLE_PARTITION',
        'SINGLE_SLICE',
    ]

    datasets_per_problem = {
        'set_coverage.py': [
            ('Data/example.dat', '3', '0.25'),
            ('Data/accidents.dat', '3', '0.25'),
            ('Data/chess.dat', '3', '0.25'),
            ('Data/chess_small.dat', '3', '0.25'),
            ('Data/mushroom.dat', '3', '0.25'),
            ('Data/pumsb.dat', '3', '0.25'),
            ('Data/retail.dat', '3', '0.25'),
        ],
        'matrix.py': [
            ('Data/matrix_small.dat', '3', '0.25'),
            ('Data/matrix.dat', '3', '0.25'),
            ('Data/matrix_large.dat', '3', '0.25'),
            ('Data/matrix_ultra.dat', '3', '0.25'),
        ]
    }

    directory_name = 'experiments'
    if os.path.exists(f"results/{directory_name}.csv"):
        os.remove(f"results/{directory_name}.csv")

    with open(f"results/{directory_name}.csv", "w") as f:
        unbuffered_write(f, "problem,algorithm,dataset,problem_size,algorithm_time(ms),total_time(ms),f(solution)\n")

        for python_file in python_files:
            problem = python_file.split('.')[0]
            names_datasets = datasets_per_problem[python_file]

            for algorithm in possible_algorithms:
                for i in range(len(names_datasets)):
                    results = run_experiment(python_file, names_datasets[i][0], algorithm, names_datasets[i][1], names_datasets[i][2])
                    for result in results:
                        size_and_timings = result.split(';')
                        dataset = size_and_timings[0]
                        problem_size = size_and_timings[1]
                        algorithm_time = size_and_timings[2]
                        total_time = size_and_timings[3]
                        f_solution = size_and_timings[4]
                        unbuffered_write(
                            f,
                            f"{problem},{algorithm},{dataset},{problem_size},{algorithm_time},{total_time},{f_solution}\n"
                        )


def unbuffered_write(file: TextIO, string: str):
    file.write(string)
    file.flush()
    os.fsync(file.fileno())


if __name__ == '__main__':
    main()
