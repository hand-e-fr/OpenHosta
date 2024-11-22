from typing import Optional

import torch
from torch import nn
from torch import optim

from .algo_architecture import get_algo_architecture
from ..hosta_model import HostaModel
from ..neural_network import NeuralNetwork
from .....utils.torch_nn_utils import custom_optimizer_to_pytorch, custom_loss_to_pytorch, custom_layer_to_pytorch
from .....core.logger import Logger, ANSIColor


class Classification(HostaModel):
    def __init__(self, neural_network: Optional[NeuralNetwork], input_size: int, output_size: int, complexity: int, num_classes: int, logger: Logger, device: Optional[str] = None):
        super().__init__(device)

        self.complexity = complexity
        self.num_classes = num_classes
        self.logger = logger
        self.device = device

        if neural_network is None or neural_network.layers is None or len(neural_network.layers) == 0:
            growth_rate = 1.5
            max_layer_coefficent = 150
            layer_size = get_algo_architecture(input_size, output_size, complexity, growth_rate, max_layer_coefficent)

            layers = []
            for i in range(len(layer_size) - 1):
                in_features = layer_size[i]
                out_features = layer_size[i + 1]

                linear_layer = nn.Linear(in_features, out_features)
                layers.append(linear_layer)

                if i < len(layer_size) - 2:
                    activation = nn.ReLU()
                    layers.append(activation)
            self.model = nn.Sequential(*layers)
        else:
            layers = [custom_layer_to_pytorch(layer) for layer in neural_network.layers]
            self.model = nn.Sequential(*layers)

        # for i, layer in enumerate(self.model):
        #     setattr(self, f'fc{i + 1}', layer)

        if neural_network is None or neural_network.loss_function is None:
            if num_classes == 2:
                self.loss = nn.BCEWithLogitsLoss()
            else:
                self.loss = nn.CrossEntropyLoss()
        else:
            self.loss = custom_loss_to_pytorch(neural_network.loss_function)

        if neural_network is None or neural_network.optimizer is None:
            self.optimizer = optim.Adam(self.parameters(), lr=0.001)
        else:
            self.optimizer = custom_optimizer_to_pytorch(neural_network.optimizer, self, lr=0.001) # TODO: Add learning rate parameter

        self.to(self.device)


    def trainer(self, train_set, epochs):
        """
        Train the model on the training set
        """
        self.train()

        for epoch in range(epochs):

            running_loss = 0.0
            correct_predictions = 0
            total_samples = 0
    
            for inputs, labels in train_set:
                inputs = inputs.to(self.device)
                labels = labels.to(self.device).long() # Ensure it's long for cross entropy loss ! 
                batch_size = inputs.size(0)

                self.optimizer.zero_grad()
                outputs = self.model(inputs)
                loss = self.loss(outputs, labels)

                loss.backward()
                self.optimizer.step()

                running_loss += loss.item()

                if self.num_classes == 2:
                    predicted_classes = (torch.sigmoid(outputs) > 0.5).float()
                else:
                    predicted_classes = torch.argmax(outputs, dim=1)

                correct_predictions += (predicted_classes == labels).sum().item()
                total_samples += batch_size

            epoch_loss = running_loss / len(train_set)
            epoch_accuracy = (correct_predictions / total_samples) * 100

            self.logger.log_custom("Epoch", f"{epoch + 1}/{epochs}, Loss: {epoch_loss:.4f}, Accuracy: {epoch_accuracy:.2f}%", color=ANSIColor.CYAN)

    def validate(self, validation_set):
        """Validate the model's performance"""
        return None
        # self.eval()  # Set model to evaluation mode
        # validation_loss = 0.0
        # correct = 0
        # total = 0
        # with torch.no_grad():
        #     for inputs, labels in validation_set:
        #         inputs, labels = inputs.to(self.device), labels.to(self.device)
        #         outputs = self(inputs)

        #         loss = self.loss(outputs, labels)
        #         validation_loss += loss.item()

        #         # For Classification Metrics (like binary or multi-class accuracy)
        #         if self.num_classes == 2:
        #             # Binary classification: Apply sigmoid and threshold at 0.5
        #             preds = (torch.sigmoid(outputs) > 0.5).float()
        #             correct += (preds == labels).sum().item()
        #         else:
        #             # Multi-class classification: Use argmax to get class labels
        #             preds = torch.softmax(outputs, dim=1)
        #             correct += (preds == labels.argmax(dim=1)).sum().item()

        #         total += labels.size(0)

        # avg_val_loss = validation_loss / len(validation_set)
        # accuracy = correct / total
        # print(f"Validation Loss: {avg_val_loss:.4f}, Accuracy: {accuracy * 100:.2f}%")

        # return avg_val_loss, accuracy

    def inference(self, x):
        """Make prediction on inputs using the model
        Returns:
            probability distribution for each class (softmax)
        """
        self.eval()
        with torch.no_grad():
            x = x.to(self.device)
            
            # Add batch dimension if needed
            if len(x.shape) == 1:
                x = x.unsqueeze(0)
            elif len(x.shape) == 2:
                if x.shape[0] != 1:
                    x = x.unsqueeze(0)
                    
            outputs = self.model(x)

            probabilities = torch.softmax(outputs, dim=1)
            return probabilities.cpu()