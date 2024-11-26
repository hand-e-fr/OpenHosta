from typing import get_origin, Literal, Union

from torch import nn
from torch import optim

from ..exec.predict.model.neural_network_types import LayerType, LossFunction, OptimizerAlgorithm, Layer


def pytorch_layer_to_custom(layer) -> Layer:
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


def custom_layer_to_pytorch(layer: Layer) -> Union[nn.Module, None]:
    """
    Maps a custom Layer instance to a PyTorch layer.

    :param layer: The custom Layer instance.
    :return: The PyTorch layer instance.
    """
    if layer.layer_type == LayerType.LINEAR:
        return nn.Linear(layer.in_features, layer.out_features)

    elif layer.layer_type == LayerType.CONV2D:
        return nn.Conv2d(
            in_channels=layer.in_features,
            out_channels=layer.out_features,
            kernel_size=layer.kernel_size,
            stride=layer.stride,
            padding=layer.padding
        )

    elif layer.layer_type == LayerType.DROPOUT:
        return nn.Dropout(p=layer.dropout)

    elif layer.layer_type == LayerType.RELU:
        return nn.ReLU()

    elif layer.layer_type == LayerType.BATCHNORM1D:
        return nn.BatchNorm1d(num_features=layer.out_features)

    elif layer.layer_type == LayerType.BATCHNORM2D:
        return nn.BatchNorm2d(num_features=layer.out_features)

    elif layer.layer_type == LayerType.MAXPOOL2D:
        return nn.MaxPool2d(
            kernel_size=layer.kernel_size,
            stride=layer.stride,
            padding=layer.padding
        )

    elif layer.layer_type == LayerType.AVGPOOL2D:
        return nn.AvgPool2d(
            kernel_size=layer.kernel_size,
            stride=layer.stride,
            padding=layer.padding
        )

    elif layer.layer_type == LayerType.SIGMOID:
        return nn.Sigmoid()

    elif layer.layer_type == LayerType.SOFTMAX:
        return nn.Softmax()

    elif layer.layer_type == LayerType.TANH:
        return nn.Tanh()

    else:
        return None


_LOSS_FUNC_MAP = {
    nn.L1Loss: LossFunction.L1_LOSS,
    nn.MSELoss: LossFunction.MSE_LOSS,
    nn.CrossEntropyLoss: LossFunction.CROSS_ENTROPY_LOSS,
    nn.CTCLoss: LossFunction.CTC_LOSS,
    nn.NLLLoss: LossFunction.NLL_LOSS,
    nn.PoissonNLLLoss: LossFunction.POISSON_NLL_LOSS,
    nn.GaussianNLLLoss: LossFunction.GAUSSIAN_NLL_LOSS,
    nn.KLDivLoss: LossFunction.KL_DIV_LOSS,
    nn.BCELoss: LossFunction.BCE_LOSS,
    nn.BCEWithLogitsLoss: LossFunction.BCE_WITH_LOGITS_LOSS,
    nn.MarginRankingLoss: LossFunction.MARGIN_RANKING_LOSS,
    nn.HingeEmbeddingLoss: LossFunction.HINGE_EMBEDDING_LOSS,
    nn.HuberLoss: LossFunction.HUBER_LOSS,
    nn.SmoothL1Loss: LossFunction.SMOOTH_L1_LOSS,
    nn.CosineEmbeddingLoss: LossFunction.COSINE_EMBEDDING_LOSS,
    nn.MultiLabelSoftMarginLoss: LossFunction.MULTI_LABEL_SOFT_MARGIN_LOSS,
    nn.TripletMarginLoss: LossFunction.TRIPLET_MARGIN_LOSS,
    nn.MultiMarginLoss: LossFunction.MULTI_MARGIN_LOSS,
    nn.SoftMarginLoss: LossFunction.SOFT_MARGIN_LOSS,
    nn.MultiLabelMarginLoss: LossFunction.MULTI_LABEL_MARGIN_LOSS,
    nn.TripletMarginWithDistanceLoss: LossFunction.TRIPLET_MARGIN_WITH_DISTANCE_LOSS,
}


def pytorch_loss_to_custom(loss_instance) -> LossFunction:
    """
    Maps a PyTorch loss function instance to a custom LossFunction enum.

    :param loss_instance: PyTorch loss function object.
    :return: The custom LossFunction enum.
    """

    loss_type = type(loss_instance)
    if loss_type in _LOSS_FUNC_MAP:
        return _LOSS_FUNC_MAP[loss_type]
    raise ValueError(f"Unsupported PyTorch loss function: {loss_type.__name__}")

def custom_loss_to_pytorch(loss_function: LossFunction) -> Union[nn.Module, None]:
    """
    Maps a custom LossFunction enum to a PyTorch loss function.

    :param loss_function: The custom LossFunction enum.
    :return: The PyTorch loss function instance.
    """

    if loss_function in _LOSS_FUNC_MAP:
        return _LOSS_FUNC_MAP[loss_function]
    return None


_OPTIMIZER_MAP = {
    optim.Adadelta: OptimizerAlgorithm.ADADELTA,
    optim.Adagrad: OptimizerAlgorithm.ADAGRAD,
    optim.Adam: OptimizerAlgorithm.ADAM,
    optim.AdamW: OptimizerAlgorithm.ADAMW,
    optim.Adamax: OptimizerAlgorithm.ADAMAX,
    optim.SparseAdam: OptimizerAlgorithm.SPARSEADAM,
    optim.ASGD: OptimizerAlgorithm.ASGD,
    optim.RMSprop: OptimizerAlgorithm.RMSPROP,
    optim.Rprop: OptimizerAlgorithm.RPROP,
    optim.SGD: OptimizerAlgorithm.SGD,
    optim.LBFGS: OptimizerAlgorithm.LBFGS,
    optim.NAdam: OptimizerAlgorithm.NADAM,
    optim.RAdam: OptimizerAlgorithm.RADAM,
}

def pytorch_optimizer_to_custom(optimizer_instance) -> OptimizerAlgorithm:
    """
    Maps a PyTorch optimizer instance to a custom OptimizerAlgorithm enum.

    :param optimizer_instance: PyTorch optimizer.
    :return: The custom OptimizerAlgorithm enum.
    """

    optimizer_type = type(optimizer_instance)
    if optimizer_type in _OPTIMIZER_MAP:
        return _OPTIMIZER_MAP[optimizer_type]
    raise ValueError(f"Unsupported PyTorch optimizer: {optimizer_type.__name__}")


def custom_optimizer_to_pytorch(optimizer_algorithm: OptimizerAlgorithm, model: nn.Module, **kwargs) -> Union[optim.Optimizer, None]:
    """
    Maps a custom OptimizerAlgorithm enum to a PyTorch optimizer.

    :param optimizer_algorithm: The custom OptimizerAlgorithm enum.
    :param model: The PyTorch model.
    :return: The PyTorch optimizer instance.
    """

    if optimizer_algorithm in _OPTIMIZER_MAP:
        return _OPTIMIZER_MAP[optimizer_algorithm](model.parameters(), **kwargs)
    return None

def type_size(data, tokens_size=10):
    """
    Calculate the inputs/outputs size based on the type of the inputs data.

    Parameters:
        tokens_size: The size of the tokens in the _inputs data.
        data: Can be of type int, float, list, tuple, numpy array, PyTorch tensor, set, dict, or string.

    Returns:
        The size (number of elements) of the given data.
    """
    if data is str:
        return tokens_size
    elif data is int:
        return 1
    elif data is float:
        return 1
    elif data is bool:
        return 1
    elif data is list:
        return len(data) * type_size(data[0]) if data else 0
    elif data is tuple:
        return sum(type_size(item) for item in data)
    elif data is set:
        return sum(type_size(item) for item in data)
    elif data is dict:
        return sum(type_size(k) + type_size(v) for k, v in data.items())
    elif get_origin(data) is Literal:
        return len(data.__args__)
    else:
        raise TypeError(f'Unsupported data type: {type(data)}')
