from OpenHosta.exec.predict.architecture.pytorch_nn import PyTorchNeuralNetwork
from OpenHosta.exec.predict.architecture.pytorch_nn import PyTorchNeuralNetwork

# from keras import
if __name__ == "__main__":
    nn = NeuralNetwork()

    # Adding layers to the neural network
    nn.add_layer(Layer(LayerType.CONV2D, in_features=3, out_features=64,
                       kernel_size=(3, 3), stride=(1, 1), padding='same'))
    nn.add_layer(Layer(LayerType.RELU))
    nn.add_layer(Layer(LayerType.MAXPOOL2D, kernel_size=(2, 2), stride=(2, 2)))
    nn.add_layer(Layer(LayerType.DROPOUT, dropout=0.5))
    nn.add_layer(Layer(LayerType.LINEAR, in_features=1024, out_features=10))

    # Set loss function and optimizer
    nn.set_loss_function("CrossEntropyLoss")
    nn.set_optimizer("Adam")

    # Create PyTorch model
    pytorch_nn = PyTorchNeuralNetwork(nn)
    print(pytorch_nn)