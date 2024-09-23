import torch
import torch.nn as nn
import torch.nn.functional as F

class CustomModel(nn.Module):
    def __init__(self, architecture):
        super(CustomModel, self).__init__()
        self.architecture = architecture

    def __call__(self):
        if self.architecture == "LinearRegression":
            return CustomLinearModel()



class CustomLinearModel(nn.Module):

    def __init__(self, architecture, config):
        super().__init__()
        self.architecture = architecture
        len_input = 18
        self.config = {
                "architecture": "LinearRegression",
                "optimizer": "adam",
                "loss": "mse",
                "input_size": len_input,
                "hidden_size_1": len_input * (2 * 1),
                "hidden_size_2": len_input * (4 * 1),
                "hidden_size_3": len_input * (2 * 1),
                "output_size": 1
            }

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.loss = nn.MSELoss()
        self.model = self.create_model(self.config)

        self.optimizer = torch.optim.AdamW(self.parameters(), lr=0.001)

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
        num_layers = len(self.config) - 4
        for idx in range(1, num_layers):
            layer = getattr(self, f"fc{idx}")
            x = F.relu(layer(x))

        layer = getattr(self, f"fc{num_layers}")
        x = layer(x)
        return x
    
    def train(self, train, val,  epochs, path):
        if epochs == None:
            epochs = 50 * len(train)

        for epoch in range(epochs):
            for X_train, y_train in train:
                
                X_train, y_train = X_train.to(self.device), y_train.to(self.device)
                self.optimizer.zero_grad()
                output = self.forward(X_train)

                loss = self.loss(output, y_train)
                loss.backward()
                self.optimizer.step()
            print(f"{epoch}/{epochs} -> Loss: {loss.item()}", flush=True)
            
        print("*" *50)
        print(f"Training complete : Loss: {loss.item()}", flush=True)
        torch.save(self.state_dict(), path)
