from abc import ABC
from typing import Optional

import torch
from torch import nn

from ..predict_memory import PredictMemory


class HostaModel(ABC, nn.Module):
    def __init__(self, device: Optional[str]):
        self.device = device if device is not None else ('cuda' if torch.cuda.is_available() else 'cpu')
        super().__init__()

    def training(self, train_set, epochs, verbose):
        pass

    def validate(self, validation_set):
        pass

    def predict(self, test_set):
        pass

    def init_weights(self):
        pass

    def save_architecture(self, memory: PredictMemory):
        pass
