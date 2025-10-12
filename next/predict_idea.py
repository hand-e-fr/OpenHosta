### The idea behind predict is to have an agent inside a pipeline that dedice of the best implementation for a given task.
### the implementation shall be accessible as a function pointer with the same signature as the parent function.
### the user can then decide to print the implementation and replace return emulate(pipeline=ScikitLearnGenerator) by the implementation code.
from OpenHosta import emulate
from OpenHosta.pipelines import ScikitLearnGenerator

from enum import Enum

class IrisSpecies(Enum):
    SETOSA = "setosa"
    VERSICOLOR = "versicolor"
    VIRGINICA = "virginica"

def separate_points_in_iris_dataset(sepal_length: float, sepal_width: float, petal_length: float, petal_width: float) -> IrisSpecies:
    """
    Separate the points in the iris dataset using a simple classifier.
    """
    return emulate(pipeline=ScikitLearnGenerator)

# The first call will generate the code using state of the art for this known task using the pipeline
# Then the generated code is used for subsequent calls as long as the python interpreter is not restarted.
# ScikitLearnGenerator shall rely on a reproducable LLM (fix seed) so that the generated code is consistent across interpreter restarts.
specie = separate_points_in_iris_dataset(5.1, 3.5, 1.4, 0.2)
print(f"The predicted species is {specie}")

# Then the user can decide to get the generated code and manually replace the call to emulate by the generated code.
# This will indicate that he/she reviewed the code and is happy to use it as is.
# It also speed up the execution as there is no need to call the LLM anymore.
print(ScikitLearnGenerator.get_code_for(separate_points_in_iris_dataset))

# We see here the logic behind PMAC as OpenHosta really acts as a just in time compiler.