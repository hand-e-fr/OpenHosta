from typing import Union

from ..neural_network import NeuralNetwork, Layer, LayerType


class ClassificationBuilder(NeuralNetwork):
    def __init__(self,
                 input_size: Optional[int] = None,
                 output_size: Optional[int] = None,
                 complexity: Optional[float] = None,
                 activation: LayerType = LayerType.RELU
             ):
        super().__init__()

        if input_size is None or output_size is None:
            raise ValueError("Input and output size must be specified")

        _complexity: float = complexity if complexity is not None else 1.0

        hidden_size_1 = int(input_size * (2 * _complexity))
        transition_size = int(((input_size * output_size) / 2) * _complexity)

        if input_size > output_size:
            hidden_size_2 = int(transition_size / output_size)
        else:
            hidden_size_2 = transition_size

        hidden_size_3 = int(output_size * (2 * _complexity))

        self.add_layer(Layer(LayerType.LINEAR, in_features=input_size, out_features=hidden_size_1))
        self.add_layer(Layer(activation))
        self.add_layer(Layer(LayerType.LINEAR, in_features=hidden_size_1, out_features=hidden_size_2))
        self.add_layer(Layer(activation))
        self.add_layer(Layer(LayerType.LINEAR, in_features=hidden_size_2, out_features=hidden_size_3))
        self.add_layer(Layer(activation))
        self.add_layer(Layer(LayerType.LINEAR, in_features=hidden_size_3, out_features=output_size))
        self.add_layer(Layer(LayerType.SOFTMAX))
