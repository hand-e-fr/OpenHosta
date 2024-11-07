import csv
import json
import os
import pickle
from enum import Enum
from typing import Optional


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
        self.data = []

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
        pass

    def encode(self, encoder, tokenizer, max_tokens: int):
        """
        todo: Implement dataset encoding
        """
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

    def save(self, path: str, source_type: SourceType = SourceType.CSV):
        """
        Save the dataset to a file in the specified format.

        Args:
            path: Path where to save the file
            source_type: Type of file format to save (CSV, JSONL, or PICKLE)
        """
        self.path = path

        if source_type == SourceType.CSV:
            with open(path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.data[0].keys())
                writer.writeheader()
                for row in self.data:
                    writer.writerow(row)

        elif source_type == SourceType.JSONL:
            with open(path, 'w') as f:
                for row in self.data:
                    json.dump(row, f)
                    f.write('\n')

        elif source_type == SourceType.PICKLE:
            with open(path, 'wb') as f:
                pickle.dump(self.data, f)
        else:
            raise ValueError(f"Unsupported source type: {source_type}")

    @staticmethod
    def from_source(path: str, source_type: Optional[SourceType] = None, min_max=None):
        """
        Load dataset from a file.

        Args:
            path: Path to the source file
            source_type: Type of file to load (CSV, JSONL, or PICKLE)
            min_max: Optional tuple of (min, max) values to filter numeric data

        Returns:
            HostaDataset instance
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
                raise ValueError(f"Please specify the source type for the file: {path}, Supported types are: CSV, JSONL, PICKLE")

        dataset = HostaDataset()
        dataset.path = path

        if source_type == SourceType.CSV:
            with open(path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Convert numeric values to float if possible
                    for key in row:
                        try:
                            row[key] = float(row[key])
                        except ValueError:
                            pass
                    dataset.add(row)

        elif source_type == SourceType.JSONL:
            with open(path, 'r') as f:
                for line in f:
                    record = json.loads(line)
                    dataset.add(record)

        elif source_type == SourceType.PICKLE:
            with open(path, 'rb') as f:
                dataset.data = pickle.load(f)
        else:
            raise ValueError(f"Unsupported source type: {source_type}")

        # Apply min_max filtering if specified
        if min_max is not None:
            min_val, max_val = min_max
            dataset.data = [row for row in dataset.data if all(min_val <= value <= max_val for value in row.values() if isinstance(value, (int, float)))]

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
