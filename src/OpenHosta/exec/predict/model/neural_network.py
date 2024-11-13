import json
from typing import Optional

from torch import nn

from .neural_network_types import LayerType, OptimizerAlgorithm, LossFunction, Layer
from ....utils.torch_nn_utils import pytorch_layer_to_custom, pytorch_loss_to_custom, pytorch_optimizer_to_custom


class NeuralNetwork:
    def __init__(self):
        """
        Initialize a NeuralNetwork object.
        """
        self.layers: list[Layer] = []
        self.loss_function: Optional[LossFunction] = None
        self.optimizer: Optional[OptimizerAlgorithm] = None

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
                    "layer_type": layer.layer_type.name if layer.layer_type else None,
                    "in_features": layer.in_features if layer.in_features else None,
                    "out_features": layer.out_features if layer.out_features else None,
                    "kernel_size": layer.kernel_size if layer.kernel_size else None,
                    "stride": layer.stride if layer.stride else None,
                    "padding": layer.padding if layer.padding else None,
                    "dropout": layer.dropout if layer.dropout else None
                }
                for layer in self.layers
            ],
            "loss_function": self.loss_function.name if self.loss_function else None,
            "optimizer": self.optimizer.name if self.optimizer else None
        }

        # Remove any entries with None values
        for layer in network_dict["layers"]:
            layer = {k: v for k, v in layer.items() if v is not None}

        network_dict = {k: v for k, v in network_dict.items() if v is not None}
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

            network.loss_function = LossFunction[network_dict.get("loss_function", None)]

            network.optimizer = OptimizerAlgorithm[network_dict.get("optimizer", None)]

            # Add layers
            for layer_dict in network_dict.get("layers", []):
                layer = Layer(
                    layer_type=LayerType[layer_dict.get("layer_type", None)],
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


    @classmethod
    def from_torch_nn(cls, torch_model: nn.Module, loss_fn=None, optimizer=None) -> 'NeuralNetwork':
        """
        Creates a NeuralNetwork instance from a torch.nn.Module model,
        with optional loss function and optimizer mappings.

        :param torch_model: The PyTorch neural network model.
        :param loss_fn: PyTorch loss function instance (optional).
        :param optimizer: PyTorch optimizer instance (optional).
        :return: A NeuralNetwork instance.
        """
        network = cls()

        # Iterating through the PyTorch model's children (layers)
        for layer in torch_model.children():
            try:
                nn_layer = pytorch_layer_to_custom(layer)
                network.add_layer(nn_layer)
            except ValueError as e:
                print(f"Skipping unsupported layer: {e}")

        # Set loss function and optimizer if specified
        if loss_fn is not None:
            try:
                network.loss_function = pytorch_loss_to_custom(loss_fn)
            except ValueError as e:
                print(f"Skipping unsupported loss function: {e}")

        # Set optimizer if specified
        if optimizer is not None:
            try:
                network.optimizer = pytorch_optimizer_to_custom(optimizer)
            except ValueError as e:
                print(f"Skipping unsupported optimizer: {e}")

        return network
