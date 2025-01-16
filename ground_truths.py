import itertools
import numpy as np

def find_universe(lines: list[str], format: str, print_universe: bool = False) -> list[int]:

    match format:
        case "set_k_cover":

            unique_numbers = set(num for line in lines for num in map(int, line.split()))

            universe = list(unique_numbers)

    if print_universe:
        print("Universe:", universe)
    
    return universe

def find_ground_truth(file_path: str, format: str, k: int = 1):
   
    with open(file_path, "r") as file:
        lines = file.readlines()

    if k > len(lines):
        return f"Error: k ({k}) is bigger than the amount of lines ({len(lines)})!"

    match format:
        case "set_k_cover":
            line_sets = [set(map(int, line.split())) for line in lines]

            max_length = 0

            for combo in itertools.combinations(line_sets, k):
                combined_set = set().union(*combo)
                max_length = max(max_length, len(combined_set))
            
            return max_length
        
        case "matrix":
            matrix = [list(map(int, row.split())) for row in lines] 
            matrix = np.array(matrix)

            n_rows = matrix.shape[0]

            max_rank = 0
            for rows in itertools.combinations(range(n_rows), k):
                submatrix = matrix[list(rows), :]
                rank = np.linalg.matrix_rank(submatrix)
                max_rank = max(max_rank, rank)

            return max_rank
                


#Test functions:
file_locations = ["Data\example.dat", "Data\chess.dat", "Data\chess_small.dat", "Data\mushroom.dat", r"Data\retail.dat", "Data\matrix.dat"]

for file_path in file_locations:
    with open(file_path, "r") as file:
        lines = file.readlines()
    print(len(find_universe(lines, "set_k_cover")))

print(find_ground_truth("Data\matrix.dat", "matrix", 4))

    
    