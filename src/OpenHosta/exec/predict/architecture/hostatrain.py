from time import sleep

import torch

from ....exec.predict.architecture.neural_network import LayerType, NeuralNetwork, Layer, LossFunction, OptimizerAlgorithm
from ....exec.predict.architecture.pytorch_nn import PyTorchNeuralNetwork
from ....utils.progress_bar import print_progress_bar


# from OpenHosta import prefix as p

class HostaTrainer(PyTorchNeuralNetwork):
    def __init__(self, neural_network : NeuralNetwork):
        super().__init__(neural_network)
        self.loss = self.get_loss_function(neural_network.loss_function)
        self.optimizer = self.get_optimizer(neural_network.optimizer)
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.to(self.device)

    
    def training_model(self, epochs: int, train_set: torch.utils.data.DataLoader, verbose: bool = False):
        for epoch in range(epochs):
            self.train()
            for i, data in enumerate(train_set):
                sleep(0.01)
                inputs, labels = data
                inputs, labels = inputs.to(self.device), labels.to(self.device)
                
                self.optimizer.zero_grad()
                outputs = self(inputs)
                loss = self.loss(outputs, labels)
                loss.backward()
                self.optimizer.step()
                
                if verbose:
                    print_progress_bar(epoch + 1, epochs, prefix=f'Epoch: {epoch + 1}/{epochs}', suffix=f'Loss: {loss.item():.4f}')
                    # print(f"Epoch {epoch + 1}, Loss: {loss.item()}")
                    
        if verbose:
            print("Finished Training")

    def tesing_model(self, test_set: torch.utils.data.DataLoader):
        self.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for data in test_set:
                inputs, labels = data
                inputs, labels = inputs.to(self.device), labels.to(self.device)
                outputs = self(inputs)
                predicted = outputs.argmax(dim=1, keepdim=True)
                total += labels.size(0)
                correct += predicted.eq(labels.view_as(predicted)).sum().item()

        print(f"Accuracy of the network on the test set: {100 * correct / total:.2f}%")



### test

nn_arch = NeuralNetwork()
nn_arch.add_layer(Layer(LayerType.LINEAR, in_features=10, out_features=20))
nn_arch.add_layer(Layer(LayerType.RELU))
nn_arch.add_layer(Layer(LayerType.LINEAR,in_features=20 ,out_features=1))
nn_arch.set_loss_function(LossFunction.MSE_LOSS)
nn_arch.set_optimizer(OptimizerAlgorithm.ADAM)

dataset = torch.utils.data.DataLoader(list(zip(torch.randn(100, 10), torch.randn(100, 1))), batch_size=10)

trainer = HostaTrainer(nn_arch)
trainer.training_model(100, dataset, verbose=True)
# trainer.train_model(10, dataset, verbose=True)