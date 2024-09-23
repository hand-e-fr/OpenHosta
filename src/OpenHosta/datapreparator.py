import torch
from torch.utils.data import DataLoader

from encoder import HostaEncoder
from decoder import HostaDecoder

class Datapreparator():
    def __init__(self, encoder, decoder) -> None:
        self.encoder = encoder if encoder else HostaEncoder()
        self.decoder = decoder if decoder else HostaDecoder()
        self.dataset = []

    def prepare(self, ho_examples, skip_data, out_data):
        self.dataset = []
        for examples in ho_examples:
            if isinstance(examples, list):
                for example in examples:
                    self.parse_dict(example, skip_data, out_data)
            else:
                self.parse_dict(examples, skip_data, out_data)

        return self.dataset

    def parse_dict(self, example, skip_data, out_data):
        input_data = []
        output_data = []
        for key, value in example.items():
            if key in out_data or key == "hosta_out":
                parsed_value = [v / 100000 for v in self.encoder.encode(value)]
                output_data.extend(parsed_value)
            elif key not in skip_data:
                parsed_value = self.encoder.encode(value)
                input_data.extend(parsed_value)
        self.dataset.append([input_data, output_data])

    def split(self, dataset):
        datatensor = []

        for examples in dataset:
            feature_tensor = torch.tensor(examples[0], dtype=torch.float32)
            label_tensor = torch.tensor(examples[1], dtype=torch.float32) 

            # feature_tensor = torch.nan_to_num(feature_tensor, nan=0.0, posinf=0.0, neginf=0.0)
            # label_tensor = torch.nan_to_num(label_tensor, nan=0.0, posinf=0.0, neginf=0.0)

            tensor = [feature_tensor, label_tensor]
            datatensor.append(tensor)

        train_size = int(0.8 * len(datatensor))
        train_data = datatensor[:train_size]
        val_data = datatensor[train_size:]
        
        train = DataLoader(train_data, batch_size=16, shuffle=True)
        val = DataLoader(val_data, batch_size=16, shuffle=False)

        return train, val
