from typing import Optional

import torch
import torch.nn as nn
import torch.optim as optim

from ....exec.predict.architecture.neural_network import LayerType, NeuralNetwork, OptimizerAlgorithm, Device, LossFunction, Layer
from ....utils.progress_bar import print_progress_bar


class PyTorchNeuralNetwork(nn.Module):
    def __init__(self, neural_network: NeuralNetwork):
        super(PyTorchNeuralNetwork, self).__init__()
        self.layers = nn.ModuleList()
        self.build_layers(neural_network.layers)

        self.loss_function: nn.Module = self.get_loss_function(
            neural_network.loss_function)
        if self.loss_function is None:
            raise ValueError(
                f"Unknown loss function: {neural_network.loss_function}")

        self.optimizer: optim.Optimizer = self.get_optimizer(
            neural_network.optimizer)
        if self.optimizer is None:
            raise ValueError(f"Unknown optimizer: {neural_network.optimizer}")

        self.device: Device = Device.CUDA if torch.cuda.is_available() else Device.CPU

    def build_layers(self, layers: list[Layer]):
        for layer in layers:
            if layer.layer_type == LayerType.LINEAR:
                self.layers.append(
                    nn.Linear(layer.in_features, layer.out_features))
            elif layer.layer_type == LayerType.CONV2D:
                self.layers.append(nn.Conv2d(
                    layer.in_features, layer.out_features, layer.kernel_size, layer.stride, layer.padding))
            elif layer.layer_type == LayerType.RELU:
                self.layers.append(nn.ReLU())
            elif layer.layer_type == LayerType.DROPOUT:
                self.layers.append(nn.Dropout(layer.dropout))
            elif layer.layer_type == LayerType.BATCHNORM1D:
                self.layers.append(nn.BatchNorm1d(layer.in_features))
            elif layer.layer_type == LayerType.BATCHNORM2D:
                self.layers.append(nn.BatchNorm2d(layer.in_features))
            elif layer.layer_type == LayerType.MAXPOOL2D:
                self.layers.append(nn.MaxPool2d(
                    layer.kernel_size, layer.stride, layer.padding))
            elif layer.layer_type == LayerType.AVGPOOL2D:
                self.layers.append(nn.AvgPool2d(
                    layer.kernel_size, layer.stride, layer.padding))
            elif layer.layer_type == LayerType.SIGMOID:
                self.layers.append(nn.Sigmoid())
            elif layer.layer_type == LayerType.TANH:
                self.layers.append(nn.Tanh())
            elif layer.layer_type == LayerType.SOFTMAX:
                self.layers.append(nn.Softmax())

    def get_loss_function(self, loss_function: LossFunction) -> Optional[nn.Module]:
        """
        Get the loss function based on the loss function provided.
        :param loss_function:
        :return nn.Module or None:
        """
        return {
            LossFunction.L1_LOSS: lambda: nn.L1Loss(),
            LossFunction.MSE_LOSS: lambda: nn.MSELoss(),
            LossFunction.CROSS_ENTROPY_LOSS: lambda: nn.CrossEntropyLoss(),
            LossFunction.CTC_LOSS: lambda: nn.CTCLoss(),
            LossFunction.NLL_LOSS: lambda: nn.NLLLoss(),
            LossFunction.POISSON_NLL_LOSS: lambda: nn.PoissonNLLLoss(),
            LossFunction.GAUSSIAN_NLL_LOSS: lambda: nn.GaussianNLLLoss(),
            LossFunction.KL_DIV_LOSS: lambda: nn.KLDivLoss(),
            LossFunction.BCE_LOSS: lambda: nn.BCELoss(),
            LossFunction.BCE_WITH_LOGITS_LOSS: lambda: nn.BCEWithLogitsLoss(),
            LossFunction.MARGIN_RANKING_LOSS: lambda: nn.MarginRankingLoss(),
            LossFunction.HINGE_EMBEDDING_LOSS: lambda: nn.HingeEmbeddingLoss(),
            LossFunction.MULTI_LABEL_MARGIN_LOSS: lambda: nn.MultiLabelMarginLoss(),
            LossFunction.HUBER_LOSS: lambda: nn.HuberLoss(),
            LossFunction.SMOOTH_L1_LOSS: lambda: nn.SmoothL1Loss(),
            LossFunction.SOFT_MARGIN_LOSS: lambda: nn.SoftMarginLoss(),
            LossFunction.MULTI_LABEL_SOFT_MARGIN_LOSS: lambda: nn.MultiLabelSoftMarginLoss(),
            LossFunction.COSINE_EMBEDDING_LOSS: lambda: nn.CosineEmbeddingLoss(),
            LossFunction.MULTI_MARGIN_LOSS: lambda: nn.MultiMarginLoss(),
            LossFunction.TRIPLET_MARGIN_LOSS: lambda: nn.TripletMarginLoss(),
            LossFunction.TRIPLET_MARGIN_WITH_DISTANCE_LOSS: lambda: nn.TripletMarginWithDistanceLoss()
        }.get(loss_function, lambda: None)()

    def get_optimizer(self, optimizer_algorithm: OptimizerAlgorithm) -> Optional[optim.Optimizer]:
        """
        Get the optimizer based on the optimizer algorithm provided.
        :param optimizer_algorithm:
        :return optim.Optimizer or None:
        """
        return {
            OptimizerAlgorithm.ADADELTA: lambda: optim.Adadelta(self.parameters()),
            OptimizerAlgorithm.ADAFACTOR: lambda: optim.Adafactor(self.parameters()),
            OptimizerAlgorithm.ADAGRAD: lambda: optim.Adagrad(self.parameters()),
            OptimizerAlgorithm.ADAM: lambda: optim.Adam(self.parameters()),
            OptimizerAlgorithm.ADAMW: lambda: optim.AdamW(self.parameters()),
            OptimizerAlgorithm.SPARSEADAM: lambda: optim.SparseAdam(self.parameters()),
            OptimizerAlgorithm.ADAMAX: lambda: optim.Adamax(self.parameters()),
            OptimizerAlgorithm.ASGD: lambda: optim.ASGD(self.parameters()),
            OptimizerAlgorithm.LBFGS: lambda: optim.LBFGS(self.parameters()),
            OptimizerAlgorithm.NADAM: lambda: optim.NAdam(self.parameters()),
            OptimizerAlgorithm.RADAM: lambda: optim.RAdam(self.parameters()),
            OptimizerAlgorithm.RMSPROP: lambda: optim.RMSprop(self.parameters()),
            OptimizerAlgorithm.RPROP: lambda: optim.Rprop(self.parameters()),
            OptimizerAlgorithm.SGD: lambda: optim.SGD(self.parameters())
        }.get(optimizer_algorithm, lambda: None)()

    def forward(self, x):
        for layer in self.layers:
            x = layer(x)
        return x

    def train_model(self, dataset_name: str, epochs: int, learning_rate: float, batch_size: int = 32):
        self.train()
        self.to(self.device)
        self.optimizer.zero_grad()

        # dataset_manager = DatasetManager.from_source("path/to/dataset.pt", "PYTORCH")
        # dataset = dataset_manager.datasets[dataset_name]
        # loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)

        for epoch in range(epochs):
            for batch in loader:
                inputs, targets = batch
                inputs = inputs.to(self.device)
                targets = targets.to(self.device)
                outputs = self(inputs)
                loss = self.loss_function(outputs, targets)
                loss.backward()
                self.optimizer.step()
                self.optimizer.zero_grad()
            print_progress_bar(
                epoch + 1, epochs, prefix=f'Epoch: {epoch + 1}/{epochs}', suffix=f'Loss: {loss.item():.4f}')

        print(f"{p("Predict Training")} Training complete.")
