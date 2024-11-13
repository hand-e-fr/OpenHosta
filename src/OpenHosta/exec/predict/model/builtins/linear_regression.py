from torch import nn
from torch import optim

from ..hosta_model import HostaModel
from ..neural_network import NeuralNetwork
from .....utils.torch_nn_utils import custom_optimizer_to_pytorch, custom_loss_to_pytorch, custom_layer_to_pytorch


class LinearRegression(HostaModel):
    def __init__(self, neural_network: NeuralNetwork, input_size : int, output_size : int, complexity : int):
        super().__init__()

        self.complexity = complexity

        # Set the loss function
        if neural_network.loss_function is None:
            self.loss = nn.MSELoss()
        else:
            self.loss = custom_loss_to_pytorch(neural_network.loss_function)

        # Set the optimizer
        if neural_network.optimizer is None:
            self.optimizer = optim.Adam(self.parameters(), lr=0.001)
        else:
            self.optimizer = custom_optimizer_to_pytorch(neural_network.optimizer, self, lr=0.001)

        # Create the layers of the neural network
        self.layers = []
        if neural_network.layers is None or len(neural_network.layers) == 0:
            transition_value = int(((input_size * output_size) / 2) * self.complexity)

            input_layer = int(input_size * (2 * self.complexity))
            if input_size > output_size:
                hidden_layer_1 = int(transition_value / output_size)
            else:
                hidden_layer_1 = transition_value
            output_layer = int(output_size * (2 * self.complexity))

            self.layers.append(nn.Linear(input_size, input_layer))
            self.layers.append(nn.Linear(input_layer, hidden_layer_1))
            self.layers.append(nn.Linear(hidden_layer_1, output_layer))
        else:
            self.layers = [custom_layer_to_pytorch(layer) for layer in neural_network.layers]

    def forward(self, x):
        if self.layers is None or len(self.layers) == 0:
            return x
        for i, layer in enumerate(self.layers):
            x = layer(x)
            if i < len(self.layers) - 1:
                x = nn.ReLU()(x)
        return x

    def training(self, train_set, epochs, verbose):
        self.train()

        for epoch in range(epochs):
            for inputs, labels in train_set:
                self.optimizer.zero_grad()
                outputs = self(inputs)
                loss = self.loss(outputs, labels)
                loss.backward()
                self.optimizer.step()
