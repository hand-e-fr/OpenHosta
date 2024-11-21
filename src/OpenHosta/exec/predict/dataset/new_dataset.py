from typing import Any, Dict, List, Optional, Tuple, Union, get_origin, get_args
from typing_extensions import Literal

import os
import csv, json
import torch
from torch.utils.data import DataLoader, TensorDataset, random_split

from enum import Enum

from .sample_type import Sample
from ..encoder.simple_encoder import SimpleEncoder
from ....core.hosta import Func
from ....core.logger import Logger

class SourceType(Enum):
    """
    Enum for different types of sources for the dataset.
    """
    CSV = "csv"
    JSONL = "jsonl"
    JSON = "json"

class HostaDataset:
    """
    class for managing datasets in Hosta
    """
    def __init__(self, verbose: int = 1):
        self.path: Optional[str] = None  # Path to the file
        self.data: List[Sample] = []  # List of Sample objects
        self.dictionary: Dict[int, str] = {}  # Dictionary for mapping str to id for encoding (for simple encoder -> Mini word2vec)
        self.inference: Optional[Sample] = None  # Inference data for understanding the data
        self.verbose: int = verbose  # Verbose level for debugging

    ########################################################
    ### Managing data ###
    def add(self, data : Any, dataset : Optional[List[Sample]] = None) -> None:
        """
        Add data to the dataset
        """
        if dataset is None:
            dataset = self.data
        
        data_sampled = Sample(data)
        dataset.append(data_sampled)
        return None


    ########################################################
    ### Preparation of the data ###
    def encode(self, max_tokens: int, dataset: Optional[List[Sample]] = None, inference_data: Optional[Sample] = None,
               func : Func = None, dictionary_path : str = None ,inference : bool = False) -> List[Sample]:
        """
        Encode data with a token limit for str values.
        """
        assert func is not None, "Func attribut must be provided for encoding"
        mapping_dict : Dict[Any, int] = None


        output_type = func.f_type[1]
        if get_origin(output_type) is Literal:
            mapping_dict = self._generate_mapping_dict(output_type)
            # print("Mapping dict : ", mapping_dict)

        self.get_dictionary(dictionary_path)
        self.encoder = SimpleEncoder.init_encoder(max_tokens, self.dictionary, dictionary_path, mapping_dict, inference) #TODO: Future, we will can choose our own encoder

        if inference:
            inference_data = inference_data if inference_data is not None else self.inference
            data_encoded = self.encoder.encode([inference_data])
            self.inference = data_encoded[0]
        else:
            dataset = dataset if dataset is not None else self.data
            data_encoded = self.encoder.encode(dataset)
            self.data = data_encoded

        return data_encoded


    def decode(self, predictions: Optional[Union[List[torch.Tensor], torch.Tensor]], func_f_type: Any) -> List[Any]:
        """
        Decode the model predictions based on the function's return type.
        """
        output_type = func_f_type[1]
        output = self.encoder.decode(predictions, output_type)
        return output, predictions


    def tensorize(self, value : Optional[Union[List[Sample], Sample]] = None, dtype : torch.dtype = None) -> List[torch.Tensor]:
        """
        Convert data to tensors for training.
        """
        dtype = dtype if dtype is not None else torch.float32

        if value is None:
            value = self.data
        else :
            if isinstance(value, Sample):
                value = [value]
            if not isinstance(value, List[Sample]):
                raise TypeError("Value must be a list of samples or a single sample")  
        for sample in value:
            sample.input = torch.tensor(sample.input, dtype=dtype)

            if sample.output is not None:
                if isinstance(sample.output, int, float):
                    sample.output = torch.tensor(sample.output, dtype=dtype)
                else:
                    sample.output = torch.tensor(sample.output, dtype=torch.long) # For CrossEntropyLoss used in classification (mandatory to be in Literal) 

        return value


    def normalize_data(data: List[Sample]) -> List[Sample]:
        """Applique une normalisation sur les données."""
        pass


    def to_dataloaders(self, data: Optional[List[Sample]] = None, batch_size: int = 1,
                       train_ratio : float = 0.8, shuffle: bool = True) -> Tuple[DataLoader, DataLoader]:
        """
        Process the data into DataLoader objects.
        """
        assert train_ratio > 0 and train_ratio < 1, "Train ratio must be between 0 and 1"
        assert batch_size > 0, "Batch size must be greater than 0"

        data = data if data is not None else self.data

        if not isinstance(data[0].input, torch.Tensor):
            data = self.tensorize(data)

        inputs = torch.stack([sample.input for sample in data])

        if all(sample.output is not None for sample in data):
            outputs = torch.stack([sample.output for sample in data])
        else:
            raise ValueError("Output data is missing in the dataset at least for one sample")
        dataset = TensorDataset(inputs, outputs)

        train_size = int(train_ratio * len(dataset))
        val_size = len(dataset) - train_size

        train_set, val_set = torch.utils.data.random_split(dataset, [train_size, val_size])

        train_loader = DataLoader(train_set, batch_size=batch_size, shuffle=shuffle)
        val_loader = DataLoader(val_set, batch_size=batch_size, shuffle=shuffle)

        return train_loader, val_loader


    ########################################################
    ### Internal function process ###
    def _generate_mapping_dict(self, literal) -> dict:
        """
        Generate a mapping dictionary for the output type.
        Parameters:
            out: A Literal type containing the possible values
        Returns:
            dict: A dictionary mapping each value to a unique integer (starting from 0)
        """
        if get_origin(literal) is not Literal:
            raise ValueError("The literal arg must be a Literal type")

        unique_values = list(get_args(literal))
        mapping_dict = {value: idx for idx, value in enumerate(unique_values)}
        return mapping_dict
    
    def get_dictionary (self, dictionary_path: str) -> None:
        """
        Load the tokenizer dictionary from a file
        """
        if not os.path.exists(dictionary_path):
            self.dictionary = {}
        else:
            with open(dictionary_path, 'r') as f:
                loaded_dict = json.load(f)
                self.dictionary = loaded_dict if loaded_dict else {}

    def save_dictionary(self, dictionary_path: str) -> None:
        """
        Save the tokenizer dictionary of mapping to a file
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(dictionary_path), exist_ok=True)

        with open(dictionary_path, 'w') as f:
            json.dump(self.dictionary, f, indent=2, sort_keys=True)


    ########################################################
    ### Conversion ##
    def convert_files(self, path: str, source_type: Optional[SourceType] = None) -> List[Sample]:
        """
        Load dataset from a file and convert each row to a Sample object.

        Args:
            path: Path to the source file
            source_type: Type of file to load (CSV, JSONL, or PICKLE)

        Returns:
            self.data will be updated with the loaded data
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
        self.path = path # Save the pass for acces easily later

        if source_type is None:
            if path.endswith('.csv'):
                source_type = SourceType.CSV
            elif path.endswith('.jsonl'):
                source_type = SourceType.JSONL
            elif path.endswith('.json'):
                source_type = SourceType.JSON
            else:
                raise ValueError(f"Please specify the source type for the file: {path}")

        if source_type == SourceType.CSV:
            with open(path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    processed_row = {}
                    for key, value in row.items():
                        try:
                            processed_row[key] = float(value)
                        except ValueError:
                            processed_row[key] = value
                    self.data.append(Sample(processed_row))

        elif source_type == SourceType.JSONL:
            with open(path, 'r') as f:
                for line in f:
                    record = json.loads(line)
                    if not isinstance(record, dict):
                        record = {'input_0': record}
                    self.data.append(Sample(record))

        elif source_type == SourceType.JSON:
            with open(path, 'r') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    self.convert_dict(data)
                elif isinstance(data, list):
                    self.convert_list(data)
                else:
                    raise ValueError(f"Unsupported data format in JSON file: {path}")

        else:
            raise ValueError(f"Unsupported source type: {source_type}")
        return self.data


    def convert_list(self, data: list = None) -> List[Sample]:
        """
        Convert a dataset from a list.
        """
        data = data if data is not None else self.data
        output_data = []
        for entry in data:
            if isinstance(entry, dict):
                # If the entry is already a dictionary, let's assume it has the keys in the right structure
                output_data.append(Sample(entry))
            elif isinstance(entry, (list, tuple)):
                # If it's a list or tuple, we assume it's structured as (_inputs..., [_outputs])
                inputs = list(entry[:-1])  # All but last element are _inputs
                output = entry[-1] if len(entry) > 1 else None  # Last element could be _outputs if present
                sample_dict = {f'input_{i}': input_value for i, input_value in enumerate(inputs)}
                if output is not None:
                    sample_dict['_outputs'] = output
                output_data.append(Sample(sample_dict))
            else:
                raise ValueError(f"Unsupported data format in list entry: {entry}")

        self.data = output_data
        return self.data


    def convert_dict(self, data: dict) -> List[Sample]:
        """
        Convert a dataset from a dict.
        """
        data = data if data is not None else self.data
        output_data = []
        for key, value in data.items():
            if not isinstance(value, dict):
                value = {'_outputs': value}
            value['_outputs'] = value.pop(key, None)
            output_data.append(Sample(value))
        return output_data

    ########################################################
    ### Data Handler ###
    def generate_synthetic_samples(self, model: Any, num_samples: int) -> List[Sample]:
        """Utilise un modèle pour générer des données synthétiques."""
        pass

    def generate_synthetic_samples_with_feedback(self, func: Func, num_samples: int) -> List[Sample]:
        """Génère des données synthétiques avec feedback."""
        pass


    ########################################################
    ### Class Generator ###
    @staticmethod
    def from_files(path: str, source_type: Optional[SourceType], logger: Logger) -> 'HostaDataset':
        """
        Load a dataset from a file.
        """
        dataset = HostaDataset(logger)
        dataset.convert_files(path, source_type)
        return dataset
    
    @staticmethod
    def from_list(data: list, logger: Logger) -> 'HostaDataset':
        """
        Create a dataset from a list.
        """
        dataset = HostaDataset(logger)
        dataset.convert_list(data)
        return dataset
    
    @staticmethod
    def from_input(inference_data: dict, logger: Logger, max_tokens : int, func: Func, dictionary_path : str) -> 'HostaDataset':
        """
        Crée un dataset à partir de données d'inférence
        """
        dataset = HostaDataset(logger)
        dataset.prepare_inference(inference_data, max_tokens, func, dictionary_path)
        return dataset


    @staticmethod
    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)