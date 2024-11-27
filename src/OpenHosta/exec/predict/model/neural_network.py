import json
from typing import Optional

from torch import nn

from .neural_network_types import LayerType, OptimizerAlgorithm, LossFunction, Layer
from ....utils.torch_nn_utils import pytorch_layer_to_custom, pytorch_loss_to_custom, pytorch_optimizer_to_custom, custom_layer_to_pytorch


class NeuralNetwork:
    def __init__(self):
        """
        Initialize a NeuralNetwork object.
        """
        self.layers: list[Layer] = []
        self.loss_function: Optional[LossFunction] = None
        self.optimizer: Optional[OptimizerAlgorithm] = None
        self._type = "UNDEFINED"

    def add_layer(self, layer: Layer):
        """
        Add a layer to the neural network.

        :param layer: The layer to be added.
        :type layer: Layer
        :raises TypeError: If the _inputs is not an instance of Layer.
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
            "type": self._type,
            "layers": [
                layer.to_json()
                for layer in self.layers
            ]
        }
        if self.loss_function is not None:
            network_dict["loss_function"] = self.loss_function.name
        if self.optimizer is not None:
            network_dict["optimizer"] = self.optimizer.name
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
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")

        network = cls()

        # Set loss function
        loss_fn_name = network_dict.get("loss_function")
        if loss_fn_name:
            try:
                network.loss_function = LossFunction[loss_fn_name]
            except KeyError:
                raise ValueError(f"Unsupported loss function: {loss_fn_name}")

        # Set optimizer
        optimizer_name = network_dict.get("optimizer")
        if optimizer_name:
            try:
                network.optimizer = OptimizerAlgorithm[optimizer_name]
            except KeyError:
                raise ValueError(f"Unsupported optimizer: {optimizer_name}")

        # Add layers
        for layer_dict in network_dict.get("layers", []):
            try:
                layer_type = LayerType[layer_dict["layer_type"]]
                layer = Layer(
                    layer_type=layer_type,
                    in_features=layer_dict.get("in_features"),
                    out_features=layer_dict.get("out_features"),
                    kernel_size=layer_dict.get("kernel_size"),
                    stride=layer_dict.get("stride"),
                    padding=layer_dict.get("padding"),
                    dropout=layer_dict.get("dropout")
                )
                network.add_layer(layer)
            except KeyError as e:
                raise ValueError(f"Missing key in layer definition: {e}")
            except ValueError as e:
                raise ValueError(f"Invalid value in layer definition: {e}")

        return network


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
        for layer in torch_model.model.children(): # assuming that the model as a attribut model ! 
            nn_layer = pytorch_layer_to_custom(layer)
            if nn_layer is not None:
                network.add_layer(nn_layer)
            else:
                pass
                # print(f"Skipping unsupported layer: {e}")

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
    
    def to_pytorch_sequential_model(self) -> nn.Sequential:
        """
        Convert the NeuralNetwork instance to a PyTorch nn.Sequential model.

        :return: A PyTorch nn.Sequential model.
        """
        layers = []
        for layer in self.layers:
            try:
                pytorch_layer = custom_layer_to_pytorch(layer)
                if pytorch_layer is not None:
                    layers.append(pytorch_layer)
            except ValueError as e:
                print(f"Skipping unsupported layer: {e}")
        return nn.Sequential(*layers)
