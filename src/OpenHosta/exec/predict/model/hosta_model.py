from abc import ABC

from torch import nn

from ..predict_memory import PredictMemory


class HostaModel(ABC, nn.Module):

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
