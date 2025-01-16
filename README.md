# 2IMA35_report 2

## Sub Modular Optimization Library
One can easily use the library to solve an sub modular optimization problem. It will return a 0.5(1 - epsilon) 
approximate solution. The library is located in the `sub_modular_optimization_library` folder. Examples of how to 
use the library are `set_coverage.py` and `matrix.py`. Do note that the Type that is used for the problem needs to 
be hashable otherwise the library will not work as it uses a set to store the elements. 

To add a new problem, one needs to create a new file and use the Library from the `sub_modular_optimization_library`.
You need to define a parsing function for both python and pyspark, give a monotone submodular function and a empty 
value.

To add an additional algorithm, one can extend the `SubModular` class in 
`sub_modular_optimization_library/algorithms/submodular.py`. The algorithm needs to implement the `run` method. An 
example would be `sub_modular_optimization_library/algorithms/pure_python.py`. For spark algorithms, one can extend 
the `SubModularSpark` class in `sub_modular_optimization_library/algorithms/sub_modular_spark.py`. The algorithm needs to implement the `run` 
method. However, this class has static methods that execute the reducer 3 and reducer 4 code. An example would be 
`sub_modular_optimization_library/algorithms/full_spark.py`.

## Running the code
The requirements of this code is `python3.11` and the other packages are listed in `requirements.txt`.

To run our experiments, you can run the `experiment.py` script.
The results of the experiments can be found in the `results` folder. The results are stored in `.csv` files.

Do note that you need to create a virtual environment with all the requirements installed. This is to ensure that 
the `experiment.py` can find the `.venv/Scripts/python.exe` file. Also, Spark is required to be installed on your machine.

## Visualizations
To visualize the results, you can run the `visualize_results.py` script.

The results of these visualizations can be found in the `visualizations` folder.
