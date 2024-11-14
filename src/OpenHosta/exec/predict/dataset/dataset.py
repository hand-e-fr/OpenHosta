import csv
import json
import os
from enum import Enum
from typing import List, Optional, Any, Dict

from .sample_type import Sample
from ..encoder.new_encoder import EnhancedEncoder
import torch # Dependances

class SourceType(Enum):
    """
    Enum for different types of sources for the dataset.
    """
    CSV = "csv"
    JSONL = "jsonl"
    JSON = "json"
class HostaDataset:
    def __init__(self, verbose: int = 1):
        self.path: Optional[str] = None  # Path to the file
        self.data: List[Sample] = []  # List of Sample objects
        self.dictionary: Dict[str, int] = {}  # Dictionary for mapping str to id
        self.inference: Optional[Sample] = None  # Inference data for understanding the data
        self.verbose: int = verbose  # Verbose level for debugging
        self._encoder: Optional[EnhancedEncoder] = None  # Will store the encoder instance
    def add(self, sample: Sample):
        """
        Add a Sample object to the dataset.
        """
        self.data.append(sample)

    def encode(self, max_tokens: int, inference : bool = False):
        """
        Encode dataset and/or inference data.
        Training mode: creates dictionary
        Inference mode: uses existing dictionary
        """
        if self._encoder is None:
            # First call (training mode) - create new encoder
            self._encoder = EnhancedEncoder()
        if not inference:
            self.data = self._encoder.encode(self.data, max_tokens=10)
            # Save dictionary after encoding training data
            self.dictionary = self._encoder.dictionary
        else:
            # If there's inference data, encode it using existing dictionary
            inference_encoder = EnhancedEncoder(existing_dict=self.dictionary)
            self.inference = inference_encoder.encode([self.inference], max_tokens)[0]

    def decode(self, predictions: List[Any], position: int) -> List[Any]:
        if self._encoder is None:
            raise ValueError("Dataset must be encoded before decoding")
        return [self._encoder.decode_prediction(pred, position) for pred in predictions]

    def tensorify(self, dtype=None):
        """
        Convertit les données en tenseurs PyTorch
        """
        if dtype is None:
            dtype = torch.float32
            
        for sample in self.data:
            # Vérifier si c'est déjà un tensor
            if not isinstance(sample._input, torch.Tensor):
                sample._input = torch.tensor(sample._input, dtype=dtype)
            
            if sample._output is not None and not isinstance(sample._output, torch.Tensor):
                # Si l'output est un scalaire, le convertir en tensor 0-D
                if isinstance(sample._output, (int, float)):
                    sample._output = torch.tensor(sample._output, dtype=dtype)
                else:
                    sample._output = torch.tensor(sample._output, dtype=dtype)
        
        return self

    # def normalize(self, min_val=0.0, max_val=1.0, inference=False):
    #     """
    #     Normalize the data after tensorification
    #     Args:
    #         min_val: desired minimum value (default: 0.0)
    #         max_val: desired maximum value (default: 1.0)
    #         inference: whether to normalize inference data
    #     """
    #     if not inference:
    #         # Training data normalization
    #         if not isinstance(self.data[0].input, torch.Tensor):
    #             self.tensorify()

    #         # Stack all inputs and outputs to calculate ranges
    #         inputs = torch.stack([sample.input for sample in self.data])
    #         outputs = torch.stack([sample.output for sample in self.data if sample.output is not None])
            
    #         # Calculate and store normalization parameters
    #         self.input_min = inputs.min(dim=0).values
    #         self.input_max = inputs.max(dim=0).values
    #         self.output_min = outputs.min(dim=0).values
    #         self.output_max = outputs.max(dim=0).values
            
    #         # Normalize inputs and outputs
    #         for sample in self.data:
    #             sample.input = self._normalize_tensor(sample.input, self.input_min, self.input_max, min_val, max_val)
    #             if sample.output is not None:
    #                 sample.output = self._normalize_tensor(sample.output, self.output_min, self.output_max, min_val, max_val)
        
    #     else:
    #         # Inference data normalization
    #         if not hasattr(self, 'input_min'):
    #             raise ValueError("Must normalize training data before inference data")
    #         self.inference.input = self._normalize_tensor(self.inference.input, self.input_min, self.input_max, min_val, max_val)
        
    #     return self

    # def denormalize_output(self, output, min_val=0.0, max_val=1.0):
    #     """
    #     Denormalize model predictions back to original scale
    #     """
    #     if not hasattr(self, 'output_min'):
    #         raise ValueError("Dataset must be normalized before denormalization")
    #     return self._normalize_tensor(output, min_val, max_val, self.output_min, self.output_max)

    # def _normalize_tensor(self, x, old_min, old_max, new_min, new_max):
    #     """Helper method for normalization/denormalization"""
    #     return new_min + (x - old_min) * (new_max - new_min) / (old_max - old_min)

    def convert_data(self, batch_size: int, shuffle: bool, train_set_size: float = 0.8) -> tuple:
        """
        Save the dataset to a file in the specified format and convert it into dataloader for training.
        """
        if not isinstance(self.data[0]._input, torch.Tensor):
            self.tensorify()
        
        inputs = torch.stack([sample._input for sample in self.data])
        if all(sample._output is not None for sample in self.data):
            outputs = torch.stack([sample._output for sample in self.data])
            dataset = torch.utils.data.TensorDataset(inputs, outputs)
        else:
            dataset = torch.utils.data.TensorDataset(inputs)
        
        return self._create_dataloaders(dataset, batch_size, shuffle, train_set_size)

    def save_data(self, file_path: str):
        """
        Sauvegarde le dataset au format JSON
        """
        data_to_save = {
            'data': [
                {
                    'input': sample._input.tolist() if isinstance(sample._input, torch.Tensor) else sample._input,
                    'output': sample._output.tolist() if isinstance(sample._output, torch.Tensor) else sample._output
                }
                for sample in self.data
            ]
        }
        with open(file_path, 'w') as f:
            json.dump(data_to_save, f)

    def load_data(self, file_path: str):
        """
        Charge un dataset depuis un fichier JSON
        """
        with open(file_path, 'r') as f:
            data_dict = json.load(f)
        
        for sample_dict in data_dict['data']:
            self.add(Sample(sample_dict))
        

    @staticmethod
    def from_data(data_path: str, batch_size: int, shuffle: bool, train_set_size: float = 0.8, verbose: int = 1) -> tuple:
        """
        Load a dataset from a file and convert it into dataloader for training.
        """
        dataset = HostaDataset(verbose)
        dataset.load_data(data_path)
        return dataset.convert_data(batch_size, shuffle, train_set_size)

    def _create_dataloaders(self, dataset, batch_size: int, shuffle: bool, train_set_size: float):
        """
        Méthode utilitaire pour créer les dataloaders
        """
        train_size = int(train_set_size * len(dataset))
        
        train_dataset = torch.utils.data.Subset(dataset, range(train_size))
        val_dataset = torch.utils.data.Subset(dataset, range(train_size, len(dataset)))
        
        return (
            torch.utils.data.DataLoader(train_dataset, batch_size=batch_size, shuffle=shuffle),
            torch.utils.data.DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
        )

    def save(self, path: str, source_type: SourceType = SourceType.CSV, elements: Optional[List[Sample]] = None):
        """
        Save the dataset or specific elements to a file in the specified format.
        Converts Sample objects back to dictionaries for storage.

        Args:
            path: Path where to save the file
            source_type: Type of file format to save (CSV, JSONL, or PICKLE)
            elements: Optional list of Sample objects to save. If None, saves entire dataset
        """
        self.path = path
        data_to_save = elements if elements is not None else self.data

        # Convert Samples to dictionaries for saving
        dict_data = []
        for sample in data_to_save:
            sample_dict = {}
            for i, input_value in enumerate(sample.input):
                sample_dict[f'input_{i}'] = input_value
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

        else:
            raise ValueError(f"Unsupported source type: {source_type}")

    def convert_files(self, path: str, source_type: Optional[SourceType] = None,):
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
            else:
                raise ValueError(f"Please specify the source type for the file: {path}")

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
                    self.data.append(Sample(processed_row))

        elif source_type == SourceType.JSONL:
            with open(path, 'r') as f:
                for line in f:
                    record = json.loads(line)
                    if not isinstance(record, dict):
                        record = {'input_0': record}
                    self.data.append(Sample(record))

        else:
            raise ValueError(f"Unsupported source type: {source_type}")
        return self.data

    def convert_list(self, data: list):
        """
        Create a dataset from a list.

        Args:
            data: List of dictionaries or tuples/lists representing Sample input and output.
                  Each item should either be:
                  - a dict with keys for input (e.g., 'input_0', 'input_1', ...) and optional 'output', or
                  - a tuple/list where the first part is input(s) and the last item is output (optional).

        Returns:
            HostaDataset instance
        """

        for entry in data:
            if isinstance(entry, dict):
                # If the entry is already a dictionary, let's assume it has the keys in the right structure
                self.add(Sample(entry))
            elif isinstance(entry, (list, tuple)):
                # If it's a list or tuple, we assume it's structured as (inputs..., [output])
                inputs = list(entry[:-1])  # All but last element are inputs
                output = entry[-1] if len(entry) > 1 else None  # Last element could be output if present
                sample_dict = {f'input_{i}': input_value for i, input_value in enumerate(inputs)}
                if output is not None:
                    sample_dict['output'] = output
                self.add(Sample(sample_dict))
            else:
                raise ValueError(f"Unsupported data format in list entry: {entry}")


    @staticmethod
    def from_input(inference: dict, memory, verbose: int) -> 'HostaDataset':
        """
        Get a Sample object from a dictionary of input values.
        """
        dataset = HostaDataset(verbose)
        dataset.inference = Sample(inference)
        return dataset

    @staticmethod
    def from_files(path: str, source_type: SourceType, verbose: int) -> 'HostaDataset':
        """
        Load a dataset from a file.
        """
        dataset = HostaDataset(verbose)
        dataset.convert_files(path, source_type)
        return dataset
    
    @staticmethod
    def from_list(data: list, verbose: int) -> 'HostaDataset':
        """
        Create a dataset from a list.
        """
        dataset = HostaDataset(verbose)
        dataset.convert_list(data)
        return dataset


    @staticmethod
    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)


# #TODO important
# # Ajouter un self.verbose dans chaque init de classe pour le debug
# # A chaque fois ça change le self.data du coup ?, 

# # Générateur de dataset
# HostaDataset.from_files("path.data.csv", SourceType.CSV) #from_source -> from_file
# HostaDataset.from_files("path.data.jsonl", SourceType.JSONL)
# HostaDataset.from_list([{"input_0": 1, "input_1": 2, "output": 3}, {"input_0": 4, "input_1": 5, "output": 6}])
# HostaDataset.from_input({"a": 1, "b": 2, "c": 3}) # predict commence par ça et donc pas bien on init hosta_dataset à l'endroit ou l'on en à besoin
# # Les from sont des staticmethod des func convert_files, convert_list, convert_input commme ça on peut les utiliser dans le process 


# HostaDataset.save("path.data.csv", SourceType.CSV) # permet de save le dataset en dur si besoin
# # peut être le déplacer dans le generator de data du coup 

# #TODO
# train_set, val_set = HostaDataset.from_process_data("path_to_data_ready") # uque en static method lui

# HostaDataset.encode(encoder=SimpleEncoder(), tokenizer=None, max_tokens=100, architecture=Architecure) # peut être hardcode le simpleencoder au début
# HostaDataset.normalize(min=0, max=1)
# HostaDataset.tensorise(dtype="float32")
# train_set, val_set = HostaDataset.to_data(batch_size=32, shuffle=True, test_size=0.8) # test_size = 1 par défaut
# # from_data aussi alors
# HostaDataset.prepare_input(inference_data={"a": 1, "b": 2, "c": 3}) # permet de préparer l'inférence
#     #convert_input
#     #encode
#     #normalize
#     #tensorise

# #Later
# HostaDataset.from_dict({{"input_0": 1, "input_1": 2, "output": 3}, {"input_0": 4, "input_1": 5, "output": 6}})