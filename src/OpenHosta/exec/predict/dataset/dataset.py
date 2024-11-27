from typing import Any, Dict, List, Optional, Tuple, Union, get_origin, get_args
from typing_extensions import Literal

import os
import csv, json
import torch
from torch.utils.data import DataLoader, TensorDataset, random_split

from enum import Enum

from .sample_type import Sample
from ..encoder.simple_encoder import SimpleEncoder
from ..predict_memory import File
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
    def __init__(self, log: Logger):
        self.path: Optional[str] = None  # Path to the file
        self.data: List[Sample] = []  # List of Sample objects
        self.dictionary: Dict[str, int] = {}  # Dictionary for mapping str to id for encoding (for simple encoder -> Mini word2vec)
        self.inference: Optional[Sample] = None  # Inference data for understanding the data
        self.log = log # Logger for logging the data
        self.encoder: Optional[SimpleEncoder] = None  # Encoder for encoding the data

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
        mapping_dict: Optional[Dict[str, int]] = None


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


    def decode(self, predictions: Optional[Union[List[torch.Tensor], torch.Tensor]], func_f_type: Any) -> Tuple[Any, Any]:
        """
        Decode the model predictions based on the function's return type.
        """
        output_type = func_f_type[1]
        output = self.encoder.decode(predictions, output_type)
        return output, predictions


    def tensorize(self, value: Optional[Union[List[Sample], Sample]] = None, dtype: torch.dtype = None) -> List[Sample]:
        """
        Convert data to tensors for training.
        
        Args:
            value: Optional data to tensorize (defaults to self.data)
            dtype: Tensor dtype (defaults to torch.float32)
        
        Returns:
            List of tensorized Samples
        """
        dtype = dtype if dtype is not None else torch.float32

        if value is None:
            value = self.data
        elif isinstance(value, Sample):
            value = [value]

        for sample in value:
            sample._inputs = torch.tensor(sample.input, dtype=dtype)

            if sample.output is not None:
                if isinstance(sample.output, (int, float)):
                    sample._outputs = torch.tensor(sample.output, dtype=dtype)
                else:
                    sample._outputs = torch.tensor(sample.output, dtype=torch.long)
        
        if value[0].output is None:
            self.inference = value[0]  # TODO: fix the error here
        else:
            self.data = value

        return value

    def to_dataloaders(self,  batch_size: int, data: Optional[List[Sample]] = None,
                    train_ratio: float = 0.8, shuffle: bool = True) -> Tuple[DataLoader, DataLoader]:
        """
        Process the data into DataLoader objects.
        """
        assert 0 < train_ratio < 1, "Train ratio must be between 0 and 1"
        assert batch_size > 0, "Batch size must be greater than 0"

        data = data if data is not None else self.data

        # Tensorize if needed
        if not isinstance(data[0]._inputs, torch.Tensor):
            data = self.tensorize(data)

        # Stack tensors
        inputs = torch.stack([sample._inputs for sample in data])

        if all(sample._outputs is not None for sample in data):
            outputs = torch.stack([sample._outputs for sample in data])
        else:
            raise ValueError("Output data is missing in the dataset at least for one sample")

        dataset = TensorDataset(inputs, outputs)

        train_size = int(train_ratio * len(dataset))
        val_size = len(dataset) - train_size
        # print("Train size : ", train_size)
        # print("Val size : ", val_size)
        train_set, val_set = random_split(dataset, [train_size, val_size])

        train_loader = DataLoader(train_set, batch_size=batch_size, shuffle=shuffle)
        val_loader = DataLoader(val_set, batch_size=batch_size, shuffle=shuffle)
        # print("Train loader len : ", len(train_loader))
        # print("Val loader len : ", len(val_loader))
        return train_loader, val_loader

    def normalize_data(self, normalization_file: File, data: Optional[Union[List[Sample], Sample]] = None) -> List[Sample]:
        """
        Normalize the input and output data column-wise to the range [-1, 1].

        Args:
            normalization_file (File): Path to the file where the normalization stats will be saved.
            data (Optional[Union[List[Sample], Sample]]): Data to normalize. If None, normalizes self.data.

        Returns:
            List[Sample]: Normalized samples.
        """
        if data is None:
            data = self.data
        elif isinstance(data, Sample):
            data = [data]

        if len(data) == 0:
            raise ValueError("No data to normalize.")

        num_columns = len(data[0].input)
        min_values = [float('inf')] * num_columns
        max_values = [float('-inf')] * num_columns

        min_output = float('inf')
        max_output = float('-inf')

        for sample in data:
            for col_idx, value in enumerate(sample.input):
                if value < min_values[col_idx]:
                    min_values[col_idx] = value
                if value > max_values[col_idx]:
                    max_values[col_idx] = value
            if sample.output is not None:
                if sample.output < min_output:
                    min_output = sample.output
                if sample.output > max_output:
                    max_output = sample.output

        normalization_data = {
            'inputs': {'min': min_values, 'max': max_values},
            'output': {'min': min_output, 'max': max_output}
        }

        for sample in data:
            for col_idx, value in enumerate(sample.input):
                if max_values[col_idx] == min_values[col_idx]:
                    sample.input[col_idx] = 0
                else:
                    sample.input[col_idx] = 2 * (value - min_values[col_idx]) / (max_values[col_idx] - min_values[col_idx]) - 1
            if sample.output is not None:
                if max_output == min_output:
                    sample.output = 0
                else:
                    sample.output = 2 * (sample.output - min_output) / (max_output - min_output) - 1

        with open(normalization_file.path, 'w', encoding='utf-8') as f:
            json.dump(normalization_data, f, indent=2, sort_keys=True)  # type: ignore

        self.data = data
        return self.data

    def normalize_input_inference(self, normalization_file: File):
        """
        Normalize the input data column-wise to the range [-1, 1].

        Args:
            normalization_file (File): Path to the file where the normalization stats are stored.

        Returns:
            Sample: Normalized input sample.
        """
        if self.inference is None:
            raise ValueError("No data to normalize.")

        with open(normalization_file.path, 'r', encoding='utf-8') as f:
            normalization_data = json.load(f)

        input_min = normalization_data['inputs']['min']
        input_max = normalization_data['inputs']['max']

        for col_idx, value in enumerate(self.inference.input):
            if input_max[col_idx] != input_min[col_idx]:
                self.inference.input[col_idx] = 2 * (value - input_min[col_idx]) / (input_max[col_idx] - input_min[col_idx]) - 1
            else:
                self.inference.input[col_idx] = 0

        return self.inference


    def denormalize_output_inference(self, output: float, normalization_file: File):
        """
        Denormalize the output data using the normalization stats stored in the given file.
        The file must contain the min and max for the output.

        Args:
            output (float): Output data to denormalize.
            normalization_file (File): Path to the normalization metadata file.

        Returns:
            float: Denormalized output.
        """
        with open(normalization_file.path, 'r', encoding='utf-8') as f:
            normalization_data = json.load(f)

        output_min = normalization_data['output']['min']
        output_max = normalization_data['output']['max']

        if output_max != output_min:
            output = ((output + 1) / 2) * (output_max - output_min) + output_min
        else:
            output = output_min

        return output

    @staticmethod
    def denormalize_output(output: Sample, normalization_file: File):
        """
        Denormalize the output data using the normalization stats stored in the given file.
        The file must contain the min and max for the output.

        Args:
            output (Sample): Output data to denormalize.
            normalization_file (File): Path to the normalization metadata file.

        Returns:
            Sample: Denormalized output sample.
        """
        with open(normalization_file.path, 'r', encoding='utf-8') as f:
            normalization_data = json.load(f)

        output_min = normalization_data['output']['min']
        output_max = normalization_data['output']['max']

        if output_max != output_min:
            output.output = ((output.output + 1) / 2) * (output_max - output_min) + output_min
        else:
            output.output = output_min

        return output

    def manage_example(self):
        pass

    def examples_to_eval(self):
        pass


    ########################################################
    ### Internal function process ###
    @staticmethod
    def _generate_mapping_dict(literal) -> dict[str, int]:
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
            with open(dictionary_path, 'r', encoding='utf-8') as f:
                loaded_dict = json.load(f)
                self.dictionary = loaded_dict if loaded_dict else {}

    def save_dictionary(self, dictionary_path: str) -> None:
        """
        Save the tokenizer dictionary of mapping to a file
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(dictionary_path), exist_ok=True)

        with open(dictionary_path, 'w', encoding='utf-8') as f:
            json.dump(self.dictionary, f, indent=2, sort_keys=True) # type: ignore

    def prepare_inference(self, inference_data: dict, max_tokens :int, func : Func, dictionary_path :str) -> None:
            """
            Prepare the inference data for the model.
            """
            self.inference = Sample(inference_data)
            self.encode(max_tokens=max_tokens, inference_data=self.inference, func=func, dictionary_path=dictionary_path, inference=True)
            self.tensorize(self.inference)

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
                    sample_dict['outputs'] = sample.output
                dict_data.append(sample_dict)

            if source_type == SourceType.CSV:
                with open(path, 'w', newline='', encoding='utf-8') as f:
                    if not dict_data:
                        return
                    writer = csv.DictWriter(f, fieldnames=dict_data[0].keys()) # type: ignore
                    writer.writeheader()
                    writer.writerows(dict_data)

            elif source_type == SourceType.JSONL:
                with open(path, 'w', encoding='utf-8') as f:
                    for row in dict_data:
                        json.dump(row, f) # type: ignore
                        f.write('\n')

            else:
                raise ValueError(f"Unsupported source type: {source_type}")
            
    def save_data(self, file_path: str):
        """
        Sauvegarde le dataset au format JSON
        """
        data_to_save = {
            'data': [
                {
                    'inputs': sample.input.tolist() if isinstance(sample.input, torch.Tensor) else sample.input,
                    'outputs': sample.output.tolist() if isinstance(sample.output, torch.Tensor) else sample.output
                }
                for sample in self.data
            ]
        }
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f) # type: ignore

    def load_data(self, file_path: str):
        with open(file_path, 'r', encoding='utf-8') as f:
            data_dict = json.load(f)
        
        for sample_dict in data_dict['data']:
            self.add(sample_dict)

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
            with open(path, 'r', encoding='utf-8') as f:
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
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    record = json.loads(line)
                    if not isinstance(record, dict):
                        record = {'input_0': record}
                    self.data.append(Sample(record))

        elif source_type == SourceType.JSON:
            with open(path, 'r', encoding='utf-8') as f:
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
                # If it's a list or tuple, we assume it's structured as (inputs..., [outputs])
                inputs = list(entry[:-1])  # All but last element are inputs
                output = entry[-1] if len(entry) > 1 else None  # Last element could be outputs if present
                sample_dict = {f'input_{i}': input_value for i, input_value in enumerate(inputs)}
                if output is not None:
                    sample_dict['outputs'] = output
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
                value = {'outputs': value}
            value['outputs'] = value.pop(key, None)
            output_data.append(Sample(value))
        self.data = output_data
        return self.data


    ########################################################
    ### Class Generator ###
    @staticmethod
    def from_files(path: str, source_type: Optional[SourceType], log: Logger) -> 'HostaDataset':
        """
        Load a dataset from a file.
        """
        dataset = HostaDataset(log)
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
    def from_data(data_path: str, logger: Logger,) -> 'HostaDataset':
        """
        Load a dataset from a file and convert it into dataloader for training.
        """
        dataset = HostaDataset(logger)
        dataset.load_data(data_path)

        return dataset
        # if config.batch_size is None:
        #     config.batch_size = max(1, min(16384, int(0.05 * len(dataset.data))))

        # return dataset.to_dataloaders(batch_size=config.batch_size, shuffle=shuffle, train_ratio=train_ratio)

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)
    




if __name__ == "__main__":
    logger = Logger()
    dataset = HostaDataset(logger)

    dataset.convert_files("data.csv", SourceType.CSV)

    dataset.encode(...)
    dataset.tensorize()
    train, val = dataset.to_dataloaders(32)
