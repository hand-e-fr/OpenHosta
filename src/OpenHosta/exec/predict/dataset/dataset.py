import os
import pickle
from enum import Enum
import pandas as pd

import torch


class SourceType(Enum):
    """
    Enum for different types of sources for the dataset.
    """
    CSV = 1
    PICKLE = 2
    TORCH = 3

class HostaDataset:
    def __init__(self):
        self.datasets = []

    def new_dataset(self, name: str, shape: tuple):
        self.datasets.append({
            "name": name,
            "shape": shape,
            "data": []
        })

    def add(self, dataset_name: str, data: list):
        for dataset in self.datasets:
            if dataset["name"] == dataset_name:
                if len(data) != dataset["shape"]:
                    raise ValueError(f"Data shape {len(data)} does not match dataset shape {dataset['shape']}")
                dataset["data"].append(data)
                break

    def save(self, path: str, source_type: SourceType = SourceType.TORCH):
        data = {}
        for dataset in self.datasets:
            data[dataset["name"]] = dataset["data"]
        if source_type == SourceType.CSV:
            for dataset_name, dataset in data.items():
                df = pd.DataFrame(dataset)
                df.to_csv(f"{path}/{dataset_name}.csv", index=False)
        elif source_type == SourceType.PICKLE:
            for dataset_name, dataset in data.items():
                with open(f"{path}/{dataset_name}.pkl", "wb") as f:
                    pickle.dump(dataset, f)
        elif source_type == SourceType.TORCH:
            torch.save(data, f"{path}/{dataset_name}.pt")
        else:
            raise ValueError(f"Invalid source type: {source_type}")

    @staticmethod
    def from_source(path: str, source_type: SourceType, min_max=None):
        if source_type == SourceType.CSV:
            data = {}
            for file in os.listdir(path):
                if file.endswith(".csv"):
                    dataset_name = file[:-4]
                    df = pd.read_csv(f"{path}/{file}")
                    data[dataset_name] = df.values.tolist()
            if min_max is not None:
                for dataset_name, dataset in data.items():
                    for i, row in enumerate(dataset):
                        row = [min_max[0] + (x - min(dataset)) / (max(dataset) - min(dataset)) * (min_max[1] - min_max[0]) for x in row]
                        dataset[i] = row
            return HostaDataset.from_dict(data)
        elif source_type == SourceType.PICKLE:
            data = {}
            for file in os.listdir(path):
                if file.endswith(".pkl"):
                    dataset_name = file[:-4]
                    with open(f"{path}/{file}", "rb") as f:
                        data[dataset_name] = pickle.load(f)
            return HostaDataset.from_dict(data)
        elif source_type == SourceType.TORCH:
            data = torch.load(path)
            return HostaDataset.from_dict(data)
        else:
            raise ValueError(f"Invalid source type: {source_type}")

    @staticmethod
    def from_dict(data: dict):
        manager = HostaDataset()
        for name, dataset in data.items():
            manager.new_dataset(name, (len(dataset[0]),))
            for row in dataset:
                manager.add(name, row)
        return manager
