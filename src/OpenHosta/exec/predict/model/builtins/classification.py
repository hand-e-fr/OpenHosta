### NOT IMPLEMENTED YET ###

from typing import Optional

import torch
from torch import nn
from torch import optim

from ..hosta_model import HostaModel
from ..neural_network import NeuralNetwork
from .....utils.torch_nn_utils import custom_optimizer_to_pytorch, custom_loss_to_pytorch, custom_layer_to_pytorch


class Classification(HostaModel):
    def __init__(self, neural_network: Optional[NeuralNetwork], input_size: int, output_size: int, complexity: int, num_classes: int, device: Optional[str] = None):
        super().__init__(device)

        self.complexity = complexity
        self.num_classes = num_classes
        self.verbose = True
        self.layers = []
        if neural_network is None or neural_network.layers is None or len(neural_network.layers) == 0:
            transition_value = int(((input_size * output_size) / 2) * self.complexity)

            input_layer = int(input_size * (2 * self.complexity))
            if input_size > output_size:
                hidden_layer_1 = int(transition_value / output_size)
            else:
                hidden_layer_1 = transition_value

            # Define simple fully connected architecture
            self.layers.append(nn.Linear(input_size, input_layer))
            self.layers.append(nn.ReLU())  # Apply ReLU after first layer
            self.layers.append(nn.Linear(input_layer, hidden_layer_1))
            self.layers.append(nn.ReLU())  # Apply ReLU after second layer
            self.layers.append(nn.Linear(hidden_layer_1, output_size))
        else:
            # Use custom user-defined layers from neural network definition if available
            self.layers = [custom_layer_to_pytorch(layer) for layer in neural_network.layers]

        for i, layer in enumerate(self.layers):
            setattr(self, f'fc{i + 1}', layer)

        # Set the loss function for classification
        if neural_network is None or neural_network.loss_function is None:
            if num_classes == 2:
                self.loss = nn.BCEWithLogitsLoss()  # For binary classification
            else:
                self.loss = nn.CrossEntropyLoss()  # For multi-class classification
        else:
            self.loss = custom_loss_to_pytorch(neural_network.loss_function)

        # Set the optimizer
        if neural_network is None or neural_network.optimizer is None:
            self.optimizer = optim.Adam(self.parameters(), lr=0.001)
        else:
            self.optimizer = custom_optimizer_to_pytorch(neural_network.optimizer, self, lr=0.001)

        # Move model to the selected device (CPU or GPU)
        self.to(self.device)


    def trainer(self, train_set, epochs):
        self.train()

        for epoch in range(epochs):
            running_loss = 0.0
            correct = 0
            total = 0
            for inputs, labels in train_set:
                inputs, labels = inputs.to(self.device), labels.to(self.device)

                # Zero parameter gradients
                self.optimizer.zero_grad()

                # Forward pass
                outputs = self(inputs)

                if self.num_classes == 2:
                    preds = (torch.sigmoid(outputs) > 0.5).float()
                else:
                    preds = torch.argmax(outputs, dim=1)

                # Compute Loss
                loss = self.loss(outputs, labels)
                loss.backward()
                self.optimizer.step()

                running_loss += loss.item()

                # Calculate accuracy
                if self.num_classes == 2:
                    correct += (preds == labels).sum().item()
                else:
                    correct += (preds == labels.argmax(dim=1)).sum().item()

                total += labels.size(0)

            accuracy = correct / total
            if self.verbose:
                print(f"Epoch {epoch + 1}/{epochs}, Loss: {running_loss / len(train_set):.4f}, Accuracy: {accuracy * 100:.2f}%")

    def validate(self, validation_set):
        """Validate the model's performance"""
        self.eval()  # Set model to evaluation mode
        validation_loss = 0.0
        correct = 0
        total = 0
        with torch.no_grad():
            for inputs, labels in validation_set:
                inputs, labels = inputs.to(self.device), labels.to(self.device)
                outputs = self(inputs)

                loss = self.loss(outputs, labels)
                validation_loss += loss.item()

                # For Classification Metrics (like binary or multi-class accuracy)
                if self.num_classes == 2:
                    # Binary classification: Apply sigmoid and threshold at 0.5
                    preds = (torch.sigmoid(outputs) > 0.5).float()
                    correct += (preds == labels).sum().item()
                else:
                    # Multi-class classification: Use argmax to get class labels
                    preds = torch.softmax(outputs, dim=1)
                    correct += (preds == labels.argmax(dim=1)).sum().item()

                total += labels.size(0)

        avg_val_loss = validation_loss / len(validation_set)
        accuracy = correct / total
        print(f"Validation Loss: {avg_val_loss:.4f}, Accuracy: {accuracy * 100:.2f}%")

        return avg_val_loss, accuracy


    def inference(self, x):
        """Make prediction on a _inputs inference the model"""
        self.eval()
        with torch.no_grad():
            x = x.to(self.device)
            outputs = self(x)
            if self.num_classes == 2:
                prediction = (torch.sigmoid(outputs) > 0.5).float()
            else:
                prediction = torch.softmax(outputs, dim=1)
            return prediction.cpu()
