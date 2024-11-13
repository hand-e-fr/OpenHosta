import csv
import json
import os
from enum import Enum
from typing import List, Optional

from .sample_type import Sample

class SourceType(Enum):
    """
    Enum for different types of sources for the dataset.
    """
    CSV = "csv"
    JSONL = "jsonl"
    JSON = "json"
class HostaDataset:
    def __init__(self, verbose: int = 0):
        self.path = None # Path to the file
        self.data : List[Sample] = [] # List of Sample objects
        self.dictionnary = {} # Dictionnary for mapping str to id
        self.inference : Sample = None # Inference data for understanding the data
        self.verbose = verbose # Verbose level for debugging

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

    @staticmethod
    def convert_list(data: list):
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
        dataset = HostaDataset()

        for entry in data:
            if isinstance(entry, dict):
                # If the entry is already a dictionary, let's assume it has the keys in the right structure
                dataset.add(Sample(entry))
            elif isinstance(entry, (list, tuple)):
                # If it's a list or tuple, we assume it's structured as (inputs..., [output])
                inputs = list(entry[:-1])  # All but last element are inputs
                output = entry[-1] if len(entry) > 1 else None  # Last element could be output if present
                sample_dict = {f'input_{i}': input_value for i, input_value in enumerate(inputs)}
                if output is not None:
                    sample_dict['output'] = output
                dataset.add(Sample(sample_dict))
            else:
                raise ValueError(f"Unsupported data format in list entry: {entry}")

        return dataset

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


#TODO important
# Ajouter un self.verbose dans chaque init de classe pour le debug
# A chaque fois ça change le self.data du coup ?, 

# Générateur de dataset
HostaDataset.from_files("path.data.csv", SourceType.CSV) #from_source -> from_file
HostaDataset.from_files("path.data.jsonl", SourceType.JSONL)
HostaDataset.from_list([{"input_0": 1, "input_1": 2, "output": 3}, {"input_0": 4, "input_1": 5, "output": 6}])
HostaDataset.from_input({"a": 1, "b": 2, "c": 3}) # predict commence par ça et donc pas bien on init hosta_dataset à l'endroit ou l'on en à besoin
# Les from sont des staticmethod des func convert_files, convert_list, convert_input commme ça on peut les utiliser dans le process 


HostaDataset.save("path.data.csv", SourceType.CSV) # permet de save le dataset en dur si besoin
# peut être le déplacer dans le generator de data du coup 

#TODO
train_set, val_set = HostaDataset.from_process_data("path_to_data_ready") # uque en static method lui

HostaDataset.encode(encoder=SimpleEncoder(), tokenizer=None, max_tokens=100, architecture=Architecure) # peut être hardcode le simpleencoder au début
HostaDataset.normalize(min=0, max=1)
HostaDataset.tensorise(dtype="float32")
train_set, val_set = HostaDataset.to_data(batch_size=32, shuffle=True, test_size=0.8) # test_size = 1 par défaut
# from_data aussi alors
HostaDataset.prepare_input(inference_data={"a": 1, "b": 2, "c": 3}) # permet de préparer l'inférence
    #convert_input
    #encode
    #normalize
    #tensorise

#Later
HostaDataset.from_dict({{"input_0": 1, "input_1": 2, "output": 3}, {"input_0": 4, "input_1": 5, "output": 6}})