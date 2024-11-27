from typing import Optional

import torch
from torch import nn
from torch import optim
from torch.optim.lr_scheduler import StepLR

from .algo_architecture import get_algo_architecture
from ..hosta_model import HostaModel
from ..neural_network import NeuralNetwork
from ..neural_network_types import ArchitectureType
from ....predict.predict_config import PredictConfig
from .....utils.torch_nn_utils import custom_optimizer_to_pytorch, custom_loss_to_pytorch, custom_layer_to_pytorch
from .....core.logger import Logger, ANSIColor


class LinearRegression(HostaModel):
    def __init__(
            self,
            neural_network: Optional[NeuralNetwork],
            input_size: int,
            output_size: int,
            config: PredictConfig,
            logger: Logger,
            device: Optional[str] = None
    ):
        super().__init__(device)

        self.complexity = config.complexity
        self.logger = logger
        self.device = device
        self.growth_rate = config.growth_rate
        self.max_layer_coefficent = config.coef_layers
        self.architecture_type = ArchitectureType.LINEAR_REGRESSION

        if neural_network is None or neural_network.layers is None or len(neural_network.layers) == 0:
            layer_size : list = get_algo_architecture(input_size, output_size, self.complexity, self.growth_rate, self.max_layer_coefficent)

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
        

        if neural_network is None or neural_network.loss_function is None:
            self.loss = nn.SmoothL1Loss()
        else:
            self.loss = custom_loss_to_pytorch(neural_network.loss_function)

        if neural_network is None or neural_network.optimizer is None:
            self.optimizer = optim.AdamW(self.parameters(), lr=0.01, weight_decay=1e-2)
        else:
            self.optimizer = custom_optimizer_to_pytorch(neural_network.optimizer, self, lr=0.001)

        self.scheduler = StepLR(self.optimizer, step_size=10, gamma=0.1)

        self.to(self.device)

    def trainer(self, train_set, epochs):
        """
        Training loop for regression models.
        Includes accuracy calculation with a tolerance (epsilon).
        """
        epsilon = 0.1
        self.train()

        for epoch in range(epochs):
            running_loss = 0.0
            correct_predictions = 0
            total_samples = 0
            
            for inputs, labels in train_set:
                inputs = inputs.to(self.device)
                labels = labels.to(self.device).float().view(-1, 1)  # Ensure proper shape and type
                batch_size = labels.size(0)

                self.optimizer.zero_grad()
                outputs = self.model(inputs)
                loss = self.loss(outputs, labels)

                loss.backward()
                self.optimizer.step()

                running_loss += loss.item()

                correct_predictions += ((outputs - labels).abs() < epsilon).sum().item()
                total_samples += batch_size
            
            self.scheduler.step()
            current_lr = self.optimizer.param_groups[0]['lr']

            epoch_loss = running_loss / len(train_set)
            epoch_accuracy = (correct_predictions / total_samples) * 100
            if epoch == epochs - 1:
                self.logger.log_custom("Epoch", f"{epoch + 1}/{epochs}, Loss: {epoch_loss:.4f}, Accuracy: {epoch_accuracy:.2f}%, LR: {current_lr:.6f}", color=ANSIColor.CYAN, level=1, one_line=False)
            else :    
                self.logger.log_custom("Epoch", f"{epoch + 1}/{epochs}, Loss: {epoch_loss:.4f}, Accuracy: {epoch_accuracy:.2f}%, LR: {current_lr:.6f}", color=ANSIColor.CYAN, level=1, one_line=True)



    def validate(self, validation_set):
        """
        Validate the model on a given validation set for regression models.
        Includes accuracy calculation with a tolerance (epsilon).
        """
        self.eval()
        validation_loss = 0.0
        correct_predictions = 0
        total_samples = 0
        epsilon = 0.1

        with torch.no_grad():
            for inputs, labels in validation_set:
                inputs = inputs.to(self.device)
                labels = labels.to(self.device).float().view(-1, 1)
                batch_size = labels.size(0)

                outputs = self.model(inputs)
                loss = self.loss(outputs, labels)
                validation_loss += loss.item() * batch_size

                correct_predictions += ((outputs - labels).abs() < epsilon).sum().item()
                total_samples += batch_size

            avg_val_loss = validation_loss / len(validation_set)
            accuracy = (correct_predictions / total_samples) * 100

            self.logger.log_custom("Validation", f"Loss: {avg_val_loss:.4f}, Accuracy: {accuracy:.2f}%", color=ANSIColor.CYAN, level=1, one_line=False)

        return #Nothing to return for now


    def inference(self, x):
        """
        Make predictions on a given input for linear regression task.
        """
        self.eval()
        with torch.no_grad():
            x = x.to(self.device)

            if x.dim() == 1:
                x = x.unsqueeze(0)

            outputs = self.model(x)

            return outputs
