import json
import os
import torch

from .encoder import HostaEncoder, FloatEncoder, BoolEncoder, StringEncoder
from .decoder import HostaDecoder, IntDecoder, FloatDecoder, BoolDecoder, StringDecoder

from .model import CustomModel, CustomLinearModel

class Builder():
    def __init__(self, hidden_dir):

        self.hidden_dir = hidden_dir


    def build(self, len_input, len_output, complexity, config, optimizer, loss):
        assert len_input > 0, "Input size must be greater than 0"
        assert len_output > 0, "Output size must be greater than 0"

        if complexity == None:
            complexity = 5
        if optimizer != None:
            print("\033[93mWarning: The change of optimizer is not available for now, AdamW is actually used.\033[0m")
            optimizer = "AdamW"
        if loss != None:
            print("\033[93mWarning: The change of loss are not available for now, Smooth1Loss is actually used.\033[0m")
            loss = "SmoothL1Loss"

        if config == None:
            config = {
                "architecture": "LinearRegression",
                "input_size": len_input,
                "hidden_size_1": len_input * (2 * complexity),
                "hidden_size_2": len_input * (4 * complexity),
                "hidden_size_3": len_input * (2 * complexity),
                "output_size": len_output,
                "optimizer": optimizer,
                "loss": loss
            }

        config_json = json.dumps(config)        
        config_path = os.path.join(self.hidden_dir, "config.json")
        
        with open(config_path, "w") as f:
            f.write(config_json)
        return config["architecture"]

    def load_inference(self, config_path, weight_path, inference):
        with open(config_path, "r") as file:
            config = json.load(file)
  
        model = CustomLinearModel(config, self.hidden_dir)
        model.load_state_dict(torch.load(weight_path))
        output = model.forward(inference)
        return output

    def trains(self, config, train, val, epochs):
        
        # TODO: polimorphic call
        model = CustomLinearModel(config, self.hidden_dir)
        model.train(train, val, epochs, self.hidden_dir)
