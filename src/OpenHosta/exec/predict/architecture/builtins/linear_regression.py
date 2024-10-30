from ..neural_network import NeuralNetwork, Layer, LayerType

class LinearRegressionBuilder(NeuralNetwork):
    def __init__(self):
        super().__init__()

    def architecture(self, input_size, output_size, config=None, complexity=1.0, activation=LayerType.RELU):
        hidden_size_1 = int(input_size * (2 * complexity))
        hidden_size_2 = int(((input_size * output_size) / 2) * complexity)
        hidden_size_3 = int(output_size * (2 * complexity))

        self.add_layer(Layer(LayerType.LINEAR, in_features=input_size, out_features=hidden_size_1))
        self.add_layer(Layer(activation))
        self.add_layer(Layer(LayerType.LINEAR, in_features=hidden_size_1, out_features=hidden_size_2))
        self.add_layer(Layer(activation))
        self.add_layer(Layer(LayerType.LINEAR, in_features=hidden_size_2, out_features=hidden_size_3))
        self.add_layer(Layer(activation))
        self.add_layer(Layer(LayerType.LINEAR, in_features=hidden_size_3, out_features=output_size))

        return config
