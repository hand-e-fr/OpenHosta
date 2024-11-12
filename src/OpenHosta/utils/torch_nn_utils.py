from torch import nn
from enum import Enum
from typing import Optional, Union
from ..exec.predict.architecture.neural_network import Layer, LayerType

def map_pytorch_layer_to_custom(layer) -> Layer:
    """
    Maps a PyTorch layer instance to a custom Layer representation.

    :param layer: PyTorch layer object.
    :return: A custom Layer object representing the PyTorch layer.
    """
    if isinstance(layer, nn.Linear):
        return Layer(
            layer_type=LayerType.LINEAR,
            in_features=layer.in_features,
            out_features=layer.out_features,
        )

    elif isinstance(layer, nn.Conv2d):
        return Layer(
            layer_type=LayerType.CONV2D,
            in_features=layer.in_channels,
            out_features=layer.out_channels,
            kernel_size=layer.kernel_size,
            stride=layer.stride,
            padding=layer.padding,
        )

    elif isinstance(layer, nn.Dropout):
        return Layer(
            layer_type=LayerType.DROPOUT,
            dropout=layer.p  # Dropout rate
        )

    elif isinstance(layer, nn.ReLU):
        return Layer(
            layer_type=LayerType.RELU
        )

    elif isinstance(layer, nn.BatchNorm1d):
        return Layer(
            layer_type=LayerType.BATCHNORM1D,
            out_features=layer.num_features
        )

    elif isinstance(layer, nn.BatchNorm2d):
        return Layer(
            layer_type=LayerType.BATCHNORM2D,
            out_features=layer.num_features
        )

    elif isinstance(layer, nn.MaxPool2d):
        return Layer(
            layer_type=LayerType.MAXPOOL2D,
            kernel_size=layer.kernel_size,
            stride=layer.stride,
            padding=layer.padding,
        )

    elif isinstance(layer, nn.AvgPool2d):
        return Layer(
            layer_type=LayerType.AVGPOOL2D,
            kernel_size=layer.kernel_size,
            stride=layer.stride,
            padding=layer.padding,
        )

    elif isinstance(layer, nn.Sigmoid):
        return Layer(
            layer_type=LayerType.SIGMOID
        )

    elif isinstance(layer, nn.Softmax):
        return Layer(
            layer_type=LayerType.SOFTMAX
        )

    elif isinstance(layer, nn.Tanh):
        return Layer(
            layer_type=LayerType.TANH
        )

    else:
        raise ValueError(f"Unsupported PyTorch layer type: {layer.__class__.__name__}")


def print_supported_layers():
    """
    Utility to print out the supported PyTorch layers.
    """
    supported_layers = [
        "nn.Linear", "nn.Conv2d", "nn.Dropout", "nn.ReLU",
        "nn.BatchNorm1d", "nn.BatchNorm2d", "nn.MaxPool2d",
        "nn.AvgPool2d", "nn.Sigmoid", "nn.Softmax", "nn.Tanh"
    ]
    print("Supported PyTorch layers:")
    for layer in supported_layers:
        print(f"  - {layer}")
