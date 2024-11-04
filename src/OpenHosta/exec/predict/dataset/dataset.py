from enum import Enum
import csv
import json
import pickle
import os


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
        self.data = {}

    def add(self, key, value):
        """
        Add data to the dataset with a specific key.

        Args:
            key: The key for the data
            value: The value to store
        """
        self.data[key] = value

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
                writer = csv.writer(f)
                writer.writerow(['key', 'value'])  # Header
                for key, value in self.data.items():
                    writer.writerow([key, value])

        elif source_type == SourceType.JSONL:
            with open(path, 'w') as f:
                for key, value in self.data.items():
                    json.dump({'key': key, 'value': value}, f)
                    f.write('\n')

        elif source_type == SourceType.PICKLE:
            with open(path, 'wb') as f:
                pickle.dump(self.data, f)
        else:
            raise ValueError(f"Unsupported source type: {source_type}")

    @staticmethod
    def from_source(path: str, source_type: SourceType, min_max=None):
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

        dataset = HostaDataset()
        dataset.path = path

        if source_type == SourceType.CSV:
            with open(path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    key = row['key']
                    value = row['value']
                    # Try to convert to float if possible
                    try:
                        value = float(value)
                    except ValueError:
                        pass
                    dataset.data[key] = value

        elif source_type == SourceType.JSONL:
            with open(path, 'r') as f:
                for line in f:
                    record = json.loads(line)
                    dataset.data[record['key']] = record['value']

        elif source_type == SourceType.PICKLE:
            with open(path, 'rb') as f:
                dataset.data = pickle.load(f)
        else:
            raise ValueError(f"Unsupported source type: {source_type}")

        # Apply min_max filtering if specified
        if min_max is not None:
            min_val, max_val = min_max
            filtered_data = {}
            for key, value in dataset.data.items():
                if isinstance(value,
                              (int, float)) and min_val <= value <= max_val:
                    filtered_data[key] = value
            dataset.data = filtered_data

        return dataset

    @staticmethod
    def from_dict(data: dict):
        """
        Create a dataset from a dictionary.

        Args:
            data: Dictionary containing the dataset

        Returns:
            HostaDataset instance
        """
        dataset = HostaDataset()
        dataset.data = data.copy()
        return dataset

    def __len__(self):
        return len(self.data)