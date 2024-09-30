import torch
import torch.nn as nn
import torch.nn.functional as F
import time
import json

class CustomModel(nn.Module):
    def __init__(self, architecture):
        super(CustomModel, self).__init__()
        self.architecture = architecture

    def __call__(self):
        if self.architecture == "LinearRegression":
            return CustomLinearModel()



class CustomLinearModel(nn.Module):

    def __init__(self, config, hidden_dir):
        super().__init__()
        self.hidden_dir = hidden_dir
        self.path = hidden_dir+"/config.json"
        if config == None:
            try:
                with open(self.path, 'r') as f:
                    self.config = json.load(f)
            except Exception as e:
                raise Exception("Config file not found please check the path : ", self.path)
        else:
            self.config = config

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.create_model(self.config)

        self.loss = nn.SmoothL1Loss()
        self.optimizer = torch.optim.AdamW(self.parameters(), lr=0.001)
        self.to(self.device)

    def create_model(self, config):

        input_size = config["input_size"]
        output_size = config["output_size"]

        hidden_sizes = []
        for key in config:
            if key.startswith("hidden_size_"):
                layer_num_str = key.split("_")[-1]
                if layer_num_str.isdigit():
                    layer_num = int(layer_num_str)
                    hidden_sizes.append((layer_num, config[key]))
        hidden_sizes.sort(key=lambda x: x[0])

        layer_sizes = [input_size] + [size for _, size in hidden_sizes] + [output_size]

        for idx in range(len(layer_sizes) - 1):
            in_features = layer_sizes[idx]
            out_features = layer_sizes[idx + 1]
            self.add_module(f"fc{idx + 1}", nn.Linear(in_features, out_features, dtype=torch.float32))

        return 

    def forward(self, x):
        x = x.to(self.device)
        num_layers = len(self.config) - 4
        for idx in range(1, num_layers):
            layer = getattr(self, f"fc{idx}")
            x = F.relu(layer(x))

        layer = getattr(self, f"fc{num_layers}")
        x = layer(x)
        return x
    
    def train(self, train, val,  epochs, path):
        
        total_start = time.time()

        for epoch in range(epochs):
            epoch_start = time.time()
            for X_train, y_train in train:
                
                X_train, y_train = X_train.to(self.device), y_train.to(self.device)
                self.optimizer.zero_grad()
                output = self.forward(X_train)

                loss = self.loss(output, y_train)
                loss.backward()
                self.optimizer.step()
            epoch_end = time.time()
            epoch_time = epoch_end - epoch_start
            print(f"\033[94m{epoch}/{epochs} -> Loss: {loss.item()} in {epoch_time} sec\033[0m", flush=True)
            
        total_end = time.time()
        total_time = total_end - total_start
        print(f"\033[92mTraining complete : Loss: {loss.item()} in a total of {total_time} sec\033[0m", flush=True)

        torch.save(self.state_dict(), path+"/model.pth")
