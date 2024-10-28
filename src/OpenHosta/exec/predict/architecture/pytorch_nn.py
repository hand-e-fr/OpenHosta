import torch.nn as nn
import torch.optim as optim
from .neural_network import LayerType


class PyTorchNeuralNetwork(nn.Module):
    def __init__(self, neural_network):
        super(PyTorchNeuralNetwork, self).__init__()
        self.layers = nn.ModuleList()
        self.build_layers(neural_network.layers)
        self.loss_function = self.get_loss_function(neural_network.loss_function)
        self.optimizer = self.get_optimizer(neural_network.optimizer)

    def build_layers(self, layers):
        for layer in layers:
            if layer.layer_type == LayerType.LINEAR:
                self.layers.append(nn.Linear(layer.in_features, layer.out_features))
            elif layer.layer_type == LayerType.CONV2D:
                self.layers.append(nn.Conv2d(layer.in_features, layer.out_features, layer.kernel_size, layer.stride, layer.padding))
            elif layer.layer_type == LayerType.RELU:
                self.layers.append(nn.ReLU())
            elif layer.layer_type == LayerType.DROPOUT:
                self.layers.append(nn.Dropout(layer.dropout))
            elif layer.layer_type == LayerType.BATCHNORM1D:
                self.layers.append(nn.BatchNorm1d(layer.in_features))
            elif layer.layer_type == LayerType.BATCHNORM2D:
                self.layers.append(nn.BatchNorm2d(layer.in_features))
            elif layer.layer_type == LayerType.MAXPOOL2D:
                self.layers.append(nn.MaxPool2d(layer.kernel_size, layer.stride, layer.padding))
            elif layer.layer_type == LayerType.AVGPOOL2D:
                self.layers.append(nn.AvgPool2d(layer.kernel_size, layer.stride, layer.padding))

    def get_loss_function(self, loss_function_name):
        if loss_function_name == "CrossEntropyLoss":
            return nn.CrossEntropyLoss()
        elif loss_function_name == "MSELoss":
            return nn.MSELoss()
        # Todo: Add more loss functions
        else:
            raise ValueError(f"Unknown loss function: {loss_function_name}")

    def get_optimizer(self, optimizer_name):
        if optimizer_name == "Adam":
            return optim.Adam(self.parameters())
        elif optimizer_name == "SGD":
            return optim.SGD(self.parameters())
        # Todo: Add more optimizers
        else:
            raise ValueError(f"Unknown optimizer: {optimizer_name}")

    def forward(self, x):
        for layer in self.layers:
            x = layer(x)
        return x
