from abc import ABC
from typing import Optional

import torch
from torch import nn
from .neural_network_types import ArchitectureType

class HostaModel(ABC, nn.Module):
    def __init__(self):
        super().__init__()
        if torch.cuda.is_available():
            self.device = torch.device('cuda:0')
        elif torch.backends.mps.is_available():
            self.device = torch.device('mps')
        else:
            self.device = torch.device('cpu')
        
        self.layers = []
        self.architecture_type: Optional["ArchitectureType"] = None

    def trainer(self, train_set, epochs):
        pass

    def forward(self, x):
        pass

    def validate(self, validation_set):
        pass

    def inference(self, x):
        pass

    def init_weights(self, path: str):
        self.load_state_dict(torch.load(path, weights_only=True, map_location=self.device))
        self.eval()

    def save_weights(self, path: str):
        torch.save(self.state_dict(), path)
