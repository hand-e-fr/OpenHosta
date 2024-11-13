from enum import Enum
from typing import Optional, Union

class ArchitectureType(Enum):
    """
    Enum for different built-in architectures for neural networks.
    """
    LINEAR_REGRESSION = 1
    CLASSIFICATION = 2


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
        in_features: Optional[int] = None,
        out_features: Optional[int] = None,
        kernel_size: Optional[Union[int, tuple[int, int]]] = None,
        stride: Optional[Union[int, tuple[int, int]]] = None,
        padding: Optional[Union[int, str]] = None,
        dropout: Optional[float] = None,
    ):
        self.layer_type: LayerType = layer_type
        self.in_features: Optional[int] = in_features
        self.out_features: Optional[int] = out_features
        self.kernel_size: Optional[Union[int, tuple[int, int]]] = kernel_size
        self.stride: Optional[Union[int, tuple[int, int]]] = stride
        self.padding: Optional[Union[int, str]] = padding
        self.dropout: Optional[float] = dropout

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

    def to_json(self):
        """
        Convert the layer configuration to a JSON string.

        :return: JSON string representation of the layer
        :rtype: str
        """
        json = {}

        if self.layer_type is not None:
            json["layer_type"] = self.layer_type.name
        if self.in_features is not None:
            json["in_features"] = self.in_features
        if self.out_features is not None:
            json["out_features"] = self.out_features
        if self.kernel_size is not None:
            json["kernel_size"] = self.kernel_size
        if self.stride is not None:
            json["stride"] = self.stride
        if self.padding is not None:
            json["padding"] = self.padding
        if self.dropout is not None:
            json["dropout"] = self.dropout

        return json
