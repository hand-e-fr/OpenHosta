import csv
import json
import os
import pickle
import os
from typing import List, Optional
from .sample_type import Sample
from enum import Enum

class SourceType(Enum):
    """
    Enum for different types of sources for the dataset.
    """
    CSV = 1
    JSONL = 2
    PICKLE = 3

class HostaDataset:
    def __init__(self):
        self.path = None
        self.data : List[Sample] = []
        self.dictionnary = {}

    def add(self, value):
        """
        Add data to the dataset.

        Args:
            value: The value to store
        """
        self.data.append(value)

    def generate(self, model, n_samples: int):
        """
        todo: Implement dataset generation
        """
        self.data_sample
        pass

    def encode(self, encoder, tokenizer, max_tokens: int, classification: bool = False):
        """
        todo: Implement dataset encoding
        """
        if self.data[0].output is None:
            pass
        else :
            if classification:
                pass
            for sample in self.data:
                pass
            

    def normalize(self, min_max=None):
        """
        todo: Implement dataset normalization
        """
        pass

    def tensorify(self):
        """
        todo: Implement dataset tensorification
        """
        pass

    def load_data(self, batch_size: int, shuffle: bool):
        """
        todo: Implement dataset loading
        """
        pass
    def fit(self, data):
        self.data_sample = Sample(self.data)
        self.data_sample.to_sample(data)

    
    def save(self, path: str, source_type: SourceType = SourceType.CSV):
        """
        Save the dataset to a file in the specified format.
        Converts Sample objects back to dictionaries for storage.

        Args:
            path: Path where to save the file
            source_type: Type of file format to save (CSV, JSONL, or PICKLE)
        """
        self.path = path

        # Convert Samples to dictionaries for saving
        dict_data = []
        for sample in self.data:
            sample_dict = {}
            # Add inputs with generic keys
            for i, input_value in enumerate(sample.input):
                sample_dict[f'input_{i}'] = input_value
            # Add output if it exists
            if sample.output is not None:
                sample_dict['output'] = sample.output
            dict_data.append(sample_dict)

        if source_type == SourceType.CSV:
            with open(path, 'w', newline='') as f:
                if not dict_data:
                    return
                writer = csv.DictWriter(f, fieldnames=dict_data[0].keys())
                writer.writeheader()
                writer.writerows(dict_data)

        elif source_type == SourceType.JSONL:
            with open(path, 'w') as f:
                for row in dict_data:
                    json.dump(row, f)
                    f.write('\n')

        elif source_type == SourceType.PICKLE:
            with open(path, 'wb') as f:
                pickle.dump(self.data, f)  # Pour Pickle, on peut sauver les Sample directement
        else:
            raise ValueError(f"Unsupported source type: {source_type}")

    @staticmethod
    def from_source(path: str, source_type: Optional[SourceType] = None):
        """
        Load dataset from a file and convert each row to a Sample object.

        Args:
            path: Path to the source file
            source_type: Type of file to load (CSV, JSONL, or PICKLE)

        Returns:
            HostaDataset instance with Sample objects
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")

        if source_type is None:
            if path.endswith('.csv'):
                source_type = SourceType.CSV
            elif path.endswith('.jsonl'):
                source_type = SourceType.JSONL
            elif path.endswith('.pkl'):
                source_type = SourceType.PICKLE
            else:
                raise ValueError(f"Please specify the source type for the file: {path}")

        dataset = HostaDataset()
        dataset.path = path

        if source_type == SourceType.CSV:
            with open(path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Convert string numbers to float if possible
                    processed_row = {}
                    for key, value in row.items():
                        try:
                            processed_row[key] = float(value)
                        except ValueError:
                            processed_row[key] = value
                    dataset.data.append(Sample(processed_row))

        elif source_type == SourceType.JSONL:
            with open(path, 'r') as f:
                for line in f:
                    record = json.loads(line)
                    if not isinstance(record, dict):
                        record = {'input_0': record}
                    dataset.data.append(Sample(record))

        elif source_type == SourceType.PICKLE:
            with open(path, 'rb') as f:
                loaded_data = pickle.load(f)
                # Si les données sont déjà des Sample, les utiliser directement
                if loaded_data and isinstance(loaded_data[0], Sample):
                    dataset.data = loaded_data
                else:
                    # Sinon, convertir chaque élément en Sample
                    for item in loaded_data:
                        if not isinstance(item, dict):
                            item = {'input_0': item}
                        dataset.data.append(Sample(item))
        else:
            raise ValueError(f"Unsupported source type: {source_type}")
        return dataset

    @staticmethod
    def from_list(data: list):
        """
        Create a dataset from a list.

        Args:
            data: List containing the dataset

        Returns:
            HostaDataset instance
        """
        dataset = HostaDataset()
        dataset.data = data.copy()
        return dataset

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)
