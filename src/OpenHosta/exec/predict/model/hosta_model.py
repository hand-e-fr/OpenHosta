from abc import ABC
from typing import Optional

import torch
from torch import nn

from ..predict_memory import PredictMemory


class HostaModel(ABC, nn.Module):
    def __init__(self, device: Optional[str]):
        self.device = device if device is not None else ('cuda' if torch.cuda.is_available() else 'cpu')
        self.layers = []
        super().__init__()

    def trainer(self, train_set, epochs):
        pass

    def forward(self, x):
        # print("mon x", x)
        for layer in self.layers:
            x = layer(x)
        return x

    def validate(self, validation_set):
        pass

    def predict(self, test_set):
        pass

    def init_weights(self):
        pass

    def save_architecture(self, memory: PredictMemory):
        pass
