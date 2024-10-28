from .base import BaseArchitecture
from enum import Enum

class LayerType(Enum):
    """
    Enum for different types of layers in a neural network.
    """
    LINEAR = "Linear"
    CONV2D = "Conv2d"
    RELU = "ReLU"
    DROPOUT = "Dropout"
    BATCHNORM1D = "BatchNorm1d"
    BATCHNORM2D = "BatchNorm2d"
    MAXPOOL2D = "MaxPool2d"
    AVGPOOL2D = "AvgPool2d"

class Layer:
    """
    Initialize a Layer object.

    :param layer_type: The type of the layer.
    :param in_features: Number of input features or channels.
    :param out_features: Number of output features or channels.
    :param kernel_size: Size of the kernel/filter.
    :param stride: Stride of the kernel/filter.
    :param padding: Padding added to the input.
    :param dropout: Dropout rate.
    """
    def __init__(self, layer_type, in_features=None, out_features=None, kernel_size=None, stride=None, padding=None, dropout=None):
        self.layer_type = layer_type
        self.in_features = in_features
        self.out_features = out_features
        self.kernel_size = kernel_size
        self.stride = stride
        self.padding = padding
        self.dropout = dropout

    def __repr__(self):
        """
        Return a string representation of the Layer object.

        :return: String representation of the Layer object.
        :rtype: str
        """
        return (
            f"Layer(type={self.layer_type}, "
            f"in_features={self.in_features}, "
            f"out_features={self.out_features}, "
            f"kernel_size={self.kernel_size}, "
            f"stride={self.stride}, "
            f"padding={self.padding}, "
            f"dropout={self.dropout})"
        )

class NeuralNetwork(BaseArchitecture):
    def __init__(self):
        """
        Initialize a NeuralNetwork object.
        """
        self.layers = []

    def add_layer(self, layer):
        """
        Add a layer to the neural network.

        :param layer: The layer to be added.
        :type layer: Layer
        :raises TypeError: If the input is not an instance of Layer.
        """
        if not isinstance(layer, Layer):
            raise TypeError("Expected a Layer instance")
        self.layers.append(layer)

    def summary(self):
        """
        Print a summary of the neural network layers.
        """
        for i, layer in enumerate(self.layers):
            print(f"Layer {i + 1}: {layer}")
