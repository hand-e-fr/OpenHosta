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
        self.verbose = True #TODO: change here 
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

        if neural_network is None or neural_network.loss_function is None:
            self.loss = nn.MSELoss()
        else:
            self.loss = custom_loss_to_pytorch(neural_network.loss_function)

        if neural_network is None or neural_network.optimizer is None:
            self.optimizer = optim.Adam(self.parameters(), lr=0.001)
        else:
            self.optimizer = custom_optimizer_to_pytorch(neural_network.optimizer, self, lr=0.001)

        self.to(self.device)

    def trainer(self, train_set, epochs):
        """
        Training loop for regression model
        Args:
            train_set: DataLoader containing training data
            epochs: Number of training epochs
        """
        self.train()
        
        for epoch in range(epochs):
            running_loss = 0.0
            correct_predictions = 0
            total_samples = 0
            
            for inputs, labels in train_set:
                inputs = inputs.to(self.device)
                labels = labels.to(self.device).float()  # Ensure float type for regression
                batch_size = labels.size(0)

                self.optimizer.zero_grad()
                outputs = self(inputs)

                loss = self.loss(outputs, labels)

                loss.backward()
                self.optimizer.step()

                running_loss += loss.item()
                
                correct_predictions = (outputs == labels).sum().item()
                total_samples += batch_size

            epoch_loss = running_loss / len(train_set)
            epochs_accuracy = (correct_predictions / total_samples) * 100

            print(f"Epoch {epoch + 1}/{epochs} | Loss: {epoch_loss:.4f} | Accuracy: {epochs_accuracy:.2f}%")

            # Learning rate scheduling to check later
            # if self.scheduler:
            #     self.scheduler.step()



    def validate(self, validation_set):
        """Validate the model on a given validation set."""
        return None #TODO: add example !
        # self.eval()  # Set model to eval mode (disable dropout, etc.)
        # validation_loss = 0.0
        # with torch.no_grad():  # No need to track gradients during validation
        #     for inputs, labels in validation_set:
        #         inputs, labels = inputs.to(self.device), labels.to(self.device)
        #         outputs = self(inputs)
        #         loss = self.loss(outputs, labels)
        #         validation_loss += loss.item()
        # return validation_loss / len(validation_set)


    def inference(self, x):
        """Make predictions for the given test set."""
        self.eval()
        with torch.no_grad():
            x = x.to(self.device)

            outputs = self(x)

            return outputs
