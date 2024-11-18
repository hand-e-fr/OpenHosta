from typing import List, Any, Dict, Union
import json

from .base_encoder import BaseEncoder
from ..dataset.sample_type import Sample


class NumericEncoder(BaseEncoder):
    def __init__(self) -> None:
        super().__init__()
    
    def encode(self, value: Union[int, float]) -> float:
        return float(value)

    def decode(self, encoded_value: float) -> Union[int, float]:
        return encoded_value

class BooleanEncoder(BaseEncoder):
    def __init__(self) -> None:
        super().__init__()

    def encode(self, value: bool) -> int:
        return int(value)

    def decode(self, encoded_value: int) -> bool:
        return bool(encoded_value)

class StringEncoder(BaseEncoder):
    def __init__(self, dictionary : Dict[int, str], max_tokens : int, inference : bool) -> None:
        super().__init__()
        self.dictionary = dictionary
        self.max_tokens = max_tokens
        self.inference = inference
        self.next_id = max(self.dictionary.keys()) + 1 if self.dictionary else 1

    def encode(self, data: str) -> int:
        words = data.lower().strip().split()

        encoded = []
        for word in words:
            if self.inference:
                encoded.append(self.dictionary.get(word, 0))                

            elif not self.inference and word not in self.dictionary:
                self.dictionary[self.next_id] = word
                encoded.append(self.next_id)
                self.next_id += 1
            elif not self.inference and word in self.dictionary:
                encoded.append(self.dictionary[word])

        if len(encoded) > self.max_tokens:
            return encoded[:self.max_tokens]
        
        return encoded + [0] * (self.max_tokens - len(encoded))
    
    def decode(self, encoded_value: int) -> str:
        return self.dictionary.get(encoded_value, '<UNK>')
    
    @property
    def get_dictionnary(self) -> Dict[int, str]:
        return self.dictionary
                
  

class MappingEncoder(BaseEncoder):
    def __init__(self, mapping_dict: Dict[int, Any]) -> None:
        self.mapping_dict = mapping_dict

    def encode(self, value: Any) -> int:
        return self.mapping_dict[value]

    def decode(self, encoded_value: int) -> Any:
        for key, value in self.mapping_dict.items():
            if value == encoded_value:
                return key
        raise ValueError(f"Unknown value: {encoded_value}")

class SimpleEncoder:
    def __init__(self, max_tokens: int, dictionary: Dict[int, str], dictionary_path : str ,mapping_dict: Dict[int, Any], inference : bool) -> None:
        self.encoders = {
            str: StringEncoder(dictionary, max_tokens, inference),
            int: NumericEncoder(),
            float: NumericEncoder(),
            bool: BooleanEncoder()
        }
        self.mapping_dict = mapping_dict
        self.dictionary_path = dictionary_path

    @staticmethod
    def init_encoder(max_tokens: int, dictionary : Dict[str, int] ,dictionary_path : str, mapping_dict: str, inference : bool) -> 'SimpleEncoder':

        encoder = SimpleEncoder(max_tokens, dictionary, dictionary_path ,mapping_dict, inference)
        return encoder
    
    def save_dictionary(self, dictionary: Dict[int, str]) -> None:
        with open(self.dictionary_path, 'w') as f:
            json.dump(dictionary, f, indent=2, sort_keys=True)


    def encode(self, samples: List[Sample]) -> List[Sample]:

        encoded_samples = []
        for sample in samples:
            encoded_input = []
            for idx, value in enumerate(sample.input):
                encoder_in = self.encoders[type(value)]
                encoded_value_in = encoder_in.encode(value)
                if isinstance(encoded_value_in, list):
                    encoded_input.extend(encoded_value_in)
                else:
                    encoded_input.append(encoded_value_in)

            encoded_output = None
            if sample.output is not None:
                if self.mapping_dict is None:
                    encoder_out = self.encoders[type(sample.output)]
                    encoded_value_out = encoder_out.encode(sample.output)
                else:
                    encoder_out = MappingEncoder(self.mapping_dict)
                    encoded_value_out = encoder_out.encode(sample.output)
                # if isinstance(encoded_value_out, list):
                #     encoded_output = encoded_value_out[0] # Like multiple str _outputs not supported only use the first str outputs
                # else:
                #     encoded_output = encoded_value_out
                encoded_output = encoded_value_out
            
            encoded_samples.append(Sample({
                '_inputs': encoded_input,
                '_outputs': encoded_output
            }))

        self.save_dictionary(self.encoders[str].get_dictionnary) # Save the dictionary
        return encoded_samples

