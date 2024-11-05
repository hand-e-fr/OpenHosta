import json
from typing import Union, Tuple

from .base import BaseArchitecture
from enum import Enum

class LayerType(Enum):
    """
    Enum for different types of layers in a neural network.
    https://pytorch.org/docs/stable/nn.html
    """
    LINEAR = 1
    CONV2D = 2
    RELU = 3
    DROPOUT = 4
    BATCHNORM1D = 5
    BATCHNORM2D = 6
    MAXPOOL2D = 7
    AVGPOOL2D = 8
    SIGMOID = 9
    SOFTMAX = 10
    TANH = 11

class OptimizerAlgorithm(Enum):
    """
    Enum for different types of optimizers in a neural network.
    https://pytorch.org/docs/stable/optim.html#algorithms
    """
    ADADELTA = 1
    ADAFACTOR = 2
    ADAGRAD = 3
    ADAM = 4
    ADAMW = 5
    SPARSEADAM = 6
    ADAMAX = 7
    ASGD = 8
    LBFGS = 9
    NADAM = 10
    RADAM = 11
    RMSPROP = 12
    RPROP = 13
    SGD = 14


class Device(Enum):
    """
    Enum for different types of devices to run the neural network
    """
    CPU = "cpu"
    CUDA = "cuda"


class LossFunction(Enum):
    """
    Enum for different types of loss functions in a neural network.
    https://pytorch.org/docs/stable/nn#loss-functions
    """
    L1_LOSS = 1
    MSE_LOSS = 2
    CROSS_ENTROPY_LOSS = 3
    CTC_LOSS = 4
    NLL_LOSS = 5
    POISSON_NLL_LOSS = 6
    GAUSSIAN_NLL_LOSS = 7
    KL_DIV_LOSS = 8
    BCE_LOSS = 9
    BCE_WITH_LOGITS_LOSS = 10
    MARGIN_RANKING_LOSS = 11
    HINGE_EMBEDDING_LOSS = 12
    MULTI_LABEL_MARGIN_LOSS = 13
    HUBER_LOSS = 14
    SMOOTH_L1_LOSS = 15
    SOFT_MARGIN_LOSS = 16
    MULTI_LABEL_SOFT_MARGIN_LOSS = 17
    COSINE_EMBEDDING_LOSS = 18
    MULTI_MARGIN_LOSS = 19
    TRIPLET_MARGIN_LOSS = 20
    TRIPLET_MARGIN_WITH_DISTANCE_LOSS = 21

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
    def __init__(
        self,
        layer_type,
        in_features: Union[int, None] = None,
        out_features: Union[int, None] = None,
        kernel_size: Union[int, Tuple[int, int], None] = None,
        stride: Union[int, Tuple[int, int], None] = None,
        padding: Union[int, str, None] = None,
        dropout: Union[float, None] = None,
    ):
        self.layer_type: LayerType = layer_type
        self.in_features: Union[int, None] = in_features
        self.out_features: Union[int, None] = out_features
        self.kernel_size: Union[int, Tuple[int, int], None] = kernel_size
        self.stride: Union[int, Tuple[int, int], None] = stride
        self.padding: Union[int, str, None] = padding
        self.dropout: Union[float, None] = dropout

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
        self.layers: list[Layer] = []
        self.loss_function: Union[LossFunction, None] = None
        self.optimizer: Union[OptimizerAlgorithm, None] = None

    def add_layer(self, layer: Layer):
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

    def set_loss_function(self, loss_function: LossFunction):
        """
        Set the loss function for the neural network.

        :param loss_function: The loss function to be set.
        :type loss_function: LossFunction
        """
        self.loss_function = loss_function

    def set_optimizer(self, optimizer: OptimizerAlgorithm):
        """
        Set the optimizer for the neural network.

        :param optimizer: The optimizer to be set.
        :type optimizer: OptimizerAlgorithm
        """
        self.optimizer = optimizer

    def to_json(self) -> str:
        """
        Convert the neural network configuration to a JSON string.

        :return: JSON string representation of the neural network
        :rtype: str
        """
        network_dict = {
            "layers": [
                {
                    "layer_type": layer.layer_type.name,
                    "in_features": layer.in_features,
                    "out_features": layer.out_features,
                    "kernel_size": layer.kernel_size,
                    "stride": layer.stride,
                    "padding": layer.padding,
                    "dropout": layer.dropout
                }
                for layer in self.layers
            ],
            "loss_function": self.loss_function.name if self.loss_function else None,
            "optimizer": self.optimizer.name if self.optimizer else None
        }
        return json.dumps(network_dict, indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> 'NeuralNetwork':
        """
        Create a neural network from a JSON string configuration.

        :param json_str: JSON string containing the neural network configuration
        :type json_str: str
        :return: A new NeuralNetwork instance
        :rtype: NeuralNetwork
        :raises ValueError: If the JSON string is invalid or contains invalid configuration
        """
        try:
            network_dict = json.loads(json_str)
            network = cls()

            # Set loss function if specified
            if network_dict.get("loss_function"):
                network.loss_function = LossFunction[network_dict["loss_function"]]

            # Set optimizer if specified
            if network_dict.get("optimizer"):
                network.optimizer = OptimizerAlgorithm[network_dict["optimizer"]]

            # Add layers
            for layer_dict in network_dict.get("layers", []):
                layer = Layer(
                    layer_type=LayerType[layer_dict["layer_type"]],
                    in_features=layer_dict.get("in_features"),
                    out_features=layer_dict.get("out_features"),
                    kernel_size=layer_dict.get("kernel_size"),
                    stride=layer_dict.get("stride"),
                    padding=layer_dict.get("padding"),
                    dropout=layer_dict.get("dropout")
                )
                network.add_layer(layer)

            return network

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise ValueError(f"Invalid JSON configuration: {str(e)}")
