from typing import Optional

from ..neural_network import NeuralNetwork, Layer, LayerType
from torch import nn
# import torch.functional as F

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



class Classification(NeuralNetwork, nn.Module):
    def __init__(self, input_size : int, output_size : int, complexity : int):
        super().__init__()

        self.complexity = complexity
        transition_value = int(((input_size * output_size) / 2) * self.complexity)

        self.input_layer = int(input_size * (2 * self.complexity))
        if input_size > output_size:
            self.hidden_layer_1 = int(transition_value / output_size)
        else:
            self.hidden_layer_1 = transition_value
        self.output_layer = int(output_size * (2 * self.complexity))

        self.loss = nn.CrossEntropyLoss()
        self.optimizer = nn.Adam(self.parameters(), lr=0.001)
    

        self.fc1 = nn.Linear(input_size, self.input_layer)
        self.fc2 = nn.Linear(self.input_layer, self.hidden_layer_1)
        self.fc3 = nn.Linear(self.hidden_layer_1, self.output_layer)

    def forwad(self, x):
        x = nn.ReLU(self.fc1(x))
        x = nn.ReLU(self.fc2(x))
        x = nn.Softmax(self.fc3(x))
        return x
    
    def training(self, train_set, epochs, verbose):
        self.train()

        for epoch in range(epochs):
            for inputs, labels in train_set:
                self.optimizer.zero_grad()
                output = self.forward(inputs)
                loss = self.loss(output, labels)
                loss.backward()
                self.optimizer.step()


    

    



