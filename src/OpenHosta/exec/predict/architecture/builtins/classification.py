from abc import ABCMeta, ABC
from typing import Optional

from ..neural_network import NeuralNetwork, Layer, LayerType
from ..architecture import BaseArchitecture
from torch import nn

class Classification(nn.Module, BaseArchitecture):
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
