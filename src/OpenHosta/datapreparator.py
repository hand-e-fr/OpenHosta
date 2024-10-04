import torch
from torch.utils.data import DataLoader
import os
import json
import csv
import numpy as np

from .encoder import HostaEncoder
from .decoder import HostaDecoder

class Datapreparator():
    def __init__(self, norm_max, norm_min, encoder=None, decoder=None):
        self.encoder = encoder if encoder else HostaEncoder()
        self.decoder = decoder if decoder else HostaDecoder()

        if norm_min:
            self.norm_min = norm_min
        else:
            self.norm_min = 0.1
        if norm_max:
            self.norm_max = norm_max
        else:
            self.norm_max = 1.0
    
        self.data_min_nonzero = None
        self.data_max = None
        self.data_min = None
        self.data_range = None

        self.prediction_min_nonzero = None
        self.prediction_max = None
        self.prediction_min = None
        self.prediction_range = None

    def prepare_input(self, in_value):
        input_data = []
        for key, value in in_value.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    parsed_value = self.encoder.encode(sub_value)
                    input_data.extend(parsed_value)
            elif isinstance(value, list):
                for item in value:
                    parsed_value = self.encoder.encode(item)
                    input_data.extend(parsed_value)
            else:
                parsed_value = self.encoder.encode(value)
                input_data.extend(parsed_value)
        return input_data

    def prepare(self, function_infos, prediction):
        train = []
        val = []
    
        if function_infos["ho_example"] == [] and function_infos["ho_data"] == []:
            raise ValueError("No example provided please provide at least one example for the model")

        if function_infos["ho_data"] != []:
            for example in function_infos["ho_data"]:
                value = self.parse_dict(example, prediction)
                train.extend(value)
            if function_infos["ho_example"] != []:
                for example in function_infos["ho_example"]:
                    value = self.parse_dict(example, prediction)
                    val.extend(value)
        else:
            for example in function_infos["ho_example"]:
                value = self.parse_dict(example, prediction)
                train.extend(value)
        return train, val

    def normalize_dataset(self, train, val):
        dataset = train + val if val != [] else train
        data_values = [example[0] for example in dataset]
        prediction_values = [example[1] for example in dataset]

        data_array = np.array(data_values)
        prediction_array = np.array(prediction_values)

        negative_data = np.any(data_array < 0, axis=0)
        negative_prediction = np.any(prediction_array < 0, axis=0)

        self.data_min_nonzero = np.array([
            np.min(data_array[:, i][data_array[:, i] > 0]) if not negative_data[i] and np.any(data_array[:, i] > 0) else 0
            for i in range(data_array.shape[1])])
        self.data_max = data_array.max(axis=0)
        self.data_min = data_array.min(axis=0)

        self.prediction_min_nonzero = np.array([
            np.min(prediction_array[:, i][prediction_array[:, i] > 0]) if not negative_prediction[i] and np.any(prediction_array[:, i] > 0) else 0
            for i in range(prediction_array.shape[1])])
        self.prediction_max = prediction_array.max(axis=0)
        self.prediction_min = prediction_array.min(axis=0)

        self.data_range = self.data_max - self.data_min_nonzero
        self.data_range[self.data_range == 0] = 1 

        self.prediction_range = self.prediction_max - self.prediction_min_nonzero
        self.prediction_range[self.prediction_range == 0] = 1

        normalized_data = np.zeros_like(data_array)
        for i in range(data_array.shape[1]):
            zero_mask = data_array[:, i] == 0
            normalized_data[:, i] = np.where(zero_mask, 0.0, self.norm_min + ((data_array[:, i] - self.data_min_nonzero[i]) / self.data_range[i]) * (self.norm_max - self.norm_min))

        normalized_prediction = np.zeros_like(prediction_array)
        for i in range(prediction_array.shape[1]):
            zero_mask = prediction_array[:, i] == 0
            normalized_prediction[:, i] = np.where(zero_mask, 0.0, self.norm_min + ((prediction_array[:, i] - self.prediction_min_nonzero[i]) / self.prediction_range[i]) * (self.norm_max - self.norm_min))

        # Maybe unwrap the tolist, stay for now because only work after with list 
        normalized_dataset = list(zip(normalized_data.tolist(), normalized_prediction.tolist()))
        train = normalized_dataset[:len(train)]
        val = normalized_dataset[len(train):] if val else None
        return train, val

    def normalize_inference(self, inference_data):
        inference_data = np.array(inference_data)

        normalized_inference = np.zeros_like(inference_data)
        for i in range(len(inference_data)):
            if inference_data[i] == 0:
                normalized_inference[i] = 0.0
            else:
                normalized_inference[i] = self.norm_min + ((inference_data[i] - self.data_min_nonzero[i]) / self.data_range[i]) * (self.norm_max - self.norm_min)
            
        return normalized_inference.tolist()
    
    def denormalize_prediction(self, prediction):
        prediction = prediction.detach().cpu().numpy()

        denormalized_prediction = np.zeros_like(prediction)
        for i in range(len(prediction)):
            if prediction[i] == 0:
                denormalized_prediction[i] = 0.0
            else:
                denormalized_prediction[i] = self.prediction_min_nonzero[i] + ((prediction[i] - self.norm_min) / (self.norm_max - self.norm_min)) * self.prediction_range[i]
    
        return denormalized_prediction.tolist()

    def save_normalization_params(self, path):
        params = {
            'norm_min': self.norm_min,
            'norm_max': self.norm_max,
            'data_min_nonzero': self.data_min_nonzero.tolist(),
            'data_max': self.data_max.tolist(),
            'data_min': self.data_min.tolist(),
            'data_range': self.data_range.tolist(),
            'prediction_min_nonzero': self.prediction_min_nonzero.tolist(),
            'prediction_max': self.prediction_max.tolist(),
            'prediction_min': self.prediction_min.tolist(),
            'prediction_range': self.prediction_range.tolist()
        }
        with open(path, 'w') as f:
            json.dump(params, f)

    def load_normalization_params(self, path):
        try:
            with open(path, 'r') as f:
                params = json.load(f)
                self.norm_min = params['norm_min']
                self.norm_max = params['norm_max']
                self.data_min_nonzero = np.array(params['data_min_nonzero'])
                self.data_max = np.array(params['data_max'])
                self.data_min = np.array(params['data_min'])
                self.data_range = np.array(params['data_range'])
                self.prediction_min_nonzero = np.array(params['prediction_min_nonzero'])
                self.prediction_max = np.array(params['prediction_max'])
                self.prediction_min = np.array(params['prediction_min'])
                self.prediction_range = np.array(params['prediction_range'])
        except Exception as e:
            raise IOError(f"An error occurred while loading the normalization parameters: {e}")

    def convert(self, inference):
        return torch.tensor(inference, dtype=torch.float32)
    
    def split(self, train_normalization, val_normalization, batch_size):
        datatensor = []

        for examples in train_normalization:
            feature_tensor = torch.tensor(examples[0], dtype=torch.float32)
            label_tensor = torch.tensor(examples[1], dtype=torch.float32)

            tensor = [feature_tensor, label_tensor]
            datatensor.append(tensor)

        # train_size = int(0.8 * len(datatensor))
        # train_data = datatensor[:train_size]
        # val_data = datatensor[train_size:]

        train = DataLoader(datatensor, batch_size=batch_size, shuffle=True)

        if val_normalization:
            valtensor = []
            for examples in val_normalization:
                feature_tensor = torch.tensor(examples[0], dtype=torch.float32)
                label_tensor = torch.tensor(examples[1], dtype=torch.float32)

                tensor = [feature_tensor, label_tensor]
                valtensor.append(tensor)
            val = DataLoader(valtensor, batch_size=batch_size, shuffle=False)
        else : val = None
        return train, val

    def parse_dict(self, example, prediction):
        dataset = []
        input_data = []
        output_data = []
        for key, value in example.items():
            if key in prediction or key == "hosta_out":
                parsed_value = self.encoder.encode(value)
                output_data.extend(parsed_value)
            else:
                parsed_value = self.encoder.encode(value)
                input_data.extend(parsed_value)
        dataset.append([input_data, output_data])
        return dataset

def open_file(ho_examples):
    list_of_examples = []
    for path in ho_examples:
        _, file_extension = os.path.splitext(path)
        try:
            if file_extension == '.jsonl':
                with open(path, "r") as file:
                    for line in file:
                        example = json.loads(line.strip())
                        list_of_examples.append(example)

            elif file_extension == '.csv':
                with open(path, "r", newline='') as file:
                    csv_reader = csv.DictReader(file)
                    for row in csv_reader:
                        list_of_examples.append(row)

            elif file_extension == '.txt':
                with open(path, "r") as file:
                    for line in file:
                        list_of_examples.append(line.strip())
            
            else:
                raise ValueError("Unsupported file type. Please provide a JSONL, CSV, or TXT file.")

        except Exception as e:
            raise IOError(f"An error occurred while processing the file: {e}")
    return list_of_examples
