import math
from typing import List

def _get_nb_layer(complexity: int):
    """
    Get the number of layers for a neural network based on its complexity.
    L_total refers to the total number of layers.
    L_up refers to the number of layers in the upward path.
    L_down refers to the number of layers in the downward path.
    """
    l_total = 2 * complexity + 1
    l_up = (l_total - 1) // 2
    l_down = l_total - l_up - 1
    return l_up, l_down


def _round_to_power_of_two(value: float) -> int:
    """
    Round a number to the nearest power of 2.
    """
    return 2 ** int(round(math.log2(value)))

def _get_layers_size(n_in, n_out, n_peak, l_up, l_down, growth_rate, max_layer_size) -> List[int]:
    """
    this function calculates the size of each layer in a neural network.
    """
    layers_size = [n_in]
    current_size = n_in

    # Upward Phase
    for i in range(l_up):
        next_size = current_size * growth_rate
        next_size = min(next_size, n_peak, max_layer_size)
        next_size = _round_to_power_of_two(next_size)
        layers_size.append(int(next_size))
        current_size = next_size

    # Downward Phase
    for i in range(l_down):
        next_size = current_size / growth_rate
        next_size = max(next_size, n_out)
        next_size = _round_to_power_of_two(next_size)
        layers_size.append(int(next_size))
        current_size = next_size

    # Ensure that the last layer size is n_out
    layers_size[-1] = n_out

    return layers_size


def get_algo_architecture(input_size: int, output_size: int, complexity: int, growth_rate: float, max_layer_coefficient: int) -> List[int]:
    """
    this function generates the architecture of a neural network.
    the complexity defines the number of layers in the network.
    growth_rate defines the rate at which the number of neurons grows.
    max_layer_coefficient defines the maximum size of the maximum layer.
    """
    n_in = input_size
    n_out = output_size
    n_max = max(n_in, n_out)

    max_layer_size = max_layer_coefficient * n_max

    l_up, l_down = _get_nb_layer(complexity)

    n_peak = n_in * (growth_rate ** l_up)
    n_peak = min(n_peak, max_layer_size)
    n_peak = _round_to_power_of_two(n_peak)  # Assurer que n_peak est une puissance de 2

    layers_size = _get_layers_size(n_in, n_out, n_peak, l_up, l_down, growth_rate, max_layer_size)

    return layers_size


# test the algorithm
########################################################

# if __name__ == "__main__":
#     input_size = 8
#     output_size = 2
#     complexity = 5
#     growth_rate = 1.5
#     max_layer_coefficient = 150

#     architecture = get_algo_architecture(input_size, output_size, complexity, growth_rate, max_layer_coefficient)
#     print("Generated architecture:", architecture)