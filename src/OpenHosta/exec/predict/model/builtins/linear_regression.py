from typing import Optional

import torch
from torch import nn
from torch import optim

from ..hosta_model import HostaModel
from ..neural_network import NeuralNetwork
from .....utils.torch_nn_utils import custom_optimizer_to_pytorch, custom_loss_to_pytorch, custom_layer_to_pytorch


class LinearRegression(HostaModel):
    def __init__(self, neural_network: Optional[NeuralNetwork], input_size: int, output_size: int, complexity: int, device: Optional[str] = None):
        super().__init__(device)

        self.complexity = complexity

        self.layers = []
        if neural_network is None or neural_network.layers is None or len(neural_network.layers) == 0:
            transition_value = int(((input_size * output_size) / 2) * self.complexity)

            input_layer = int(input_size * (2 * self.complexity))
            if input_size > output_size:
                hidden_layer_1 = int(transition_value / output_size)
            else:
                hidden_layer_1 = transition_value

            self.layers.append(nn.Linear(input_size, input_layer))
            self.layers.append(nn.ReLU())
            self.layers.append(nn.Linear(input_layer, hidden_layer_1))
            self.layers.append(nn.ReLU())
            self.layers.append(nn.Linear(hidden_layer_1, output_size))
        else:
            self.layers = [custom_layer_to_pytorch(layer) for layer in neural_network.layers]

        for i, layer in enumerate(self.layers):
            setattr(self, f'fc{i + 1}', layer)

        # Set the loss function
        if neural_network is None or neural_network.loss_function is None:
            self.loss = nn.MSELoss()
        else:
            self.loss = custom_loss_to_pytorch(neural_network.loss_function)

        # Set the optimizer
        if neural_network is None or neural_network.optimizer is None:
            self.optimizer = optim.Adam(self.parameters(), lr=0.001)
        else:
            self.optimizer = custom_optimizer_to_pytorch(neural_network.optimizer, self, lr=0.001)

        # Move model to the selected device (CPU or GPU)
        self.to(self.device)

    def trainer(self, train_set, epochs, verbose=False):
        self.train()

        for epoch in range(epochs):
            running_loss = 0.0
            for inputs, labels in train_set:
                # Move _inputs and labels to the right device
                inputs, labels = inputs.to(self.device), labels.to(self.device)

                # Zero the parameter gradients
                self.optimizer.zero_grad()

                # Forward pass
                outputs = self(inputs)
                
                loss = self.loss(outputs, labels)

                # Backward pass and update
                loss.backward()
                self.optimizer.step()

                running_loss += loss.item()
            # if verbose:
            print(f"Epoch {epoch + 1}/{epochs}, Loss: {running_loss / len(train_set)}")

    def validate(self, validation_set):
        """Validate the model on a given validation set."""
        self.eval()  # Set model to eval mode (disable dropout, etc.)
        validation_loss = 0.0
        with torch.no_grad():  # No need to track gradients during validation
            for inputs, labels in validation_set:
                inputs, labels = inputs.to(self.device), labels.to(self.device)
                outputs = self(inputs)
                loss = self.loss(outputs, labels)
                validation_loss += loss.item()
        return validation_loss / len(validation_set)

    def inference(self, x):
        """Make predictions for the given test set."""
        self.eval()
        with torch.no_grad():
            x = x.to(self.device)
            outputs = self(x)
            return outputs
