from torch import nn
from torch import optim
from enum import Enum
from typing import Optional, Union
from ..exec.predict.architecture.neural_network import Layer, LayerType, LossFunction, OptimizerAlgorithm

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

def map_pytorch_loss_to_custom(loss_instance) -> LossFunction:
    """
    Maps a PyTorch loss function instance to a custom LossFunction enum.

    :param loss_instance: PyTorch loss function object.
    :return: The custom LossFunction enum.
    """

    mapping = {
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

    loss_type = type(loss_instance)
    if loss_type in mapping:
        return mapping[loss_type]
    raise ValueError(f"Unsupported PyTorch loss function: {loss_type.__name__}")


def map_pytorch_optimizer_to_custom(optimizer_instance) -> OptimizerAlgorithm:
    """
    Maps a PyTorch optimizer instance to a custom OptimizerAlgorithm enum.

    :param optimizer_instance: PyTorch optimizer.
    :return: The custom OptimizerAlgorithm enum.
    """

    mapping = {
        optim.Adadelta: OptimizerAlgorithm.ADADELTA,
        optim.Adafactor: OptimizerAlgorithm.ADAFACTOR,
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
        optim.Nadam: OptimizerAlgorithm.NADAM,
        optim.RAdam: OptimizerAlgorithm.RADAM,
    }

    optimizer_type = type(optimizer_instance)
    if optimizer_type in mapping:
        return mapping[optimizer_type]
    raise ValueError(f"Unsupported PyTorch optimizer: {optimizer_type.__name__}")
