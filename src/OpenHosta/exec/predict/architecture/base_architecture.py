from abc import ABC


class BaseArchitecture(ABC):

    def training(self, train_set, epochs, verbose):
        pass

    def validate(self, validation_set):
        pass

    def predict(self, test_set):
        pass

    #todo: add more methods

    def init_weights(self):
        pass

