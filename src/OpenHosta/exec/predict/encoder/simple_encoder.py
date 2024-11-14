from typing import List, Any, Dict, Union

from .base_encoder import BaseEncoder
from ..dataset.sample_type import Sample


class NumericEncoder(BaseEncoder):
    def encode(self, value: Union[int, float]) -> float:
        return float(value)

    def decode(self, encoded_value: float) -> Union[int, float]:
        return encoded_value

class BooleanEncoder(BaseEncoder):
    def encode(self, value: bool) -> int:
        return int(value)

    def decode(self, encoded_value: int) -> bool:
        return bool(encoded_value)

class StringEncoder(BaseEncoder):
    def __init__(self, existing_dict: Dict[str, int] = None):
        """
        Initialize with optional existing dictionary.
        If existing_dict is provided, we're in inference mode.
        """
        self.inference_mode = existing_dict is not None
        self.word_to_id = {'<UNK>': 0} if existing_dict is None else existing_dict
        self.id_to_word = {v: k for k, v in self.word_to_id.items()}
        self.next_id = max(self.word_to_id.values()) + 1 if self.word_to_id else 1
        self.max_tokens = None

    def set_max_tokens(self, max_tokens: int):
        """Set maximum length for encoded sequences"""
        self.max_tokens = max_tokens

    def encode(self, value: str) -> List[int]:
        """
        Encode a string into a list of integers.
        For classification (_outputs), returns a single integer.
        For _inputs features, returns a list of integers of length max_tokens.
        """
        if self.max_tokens is None:
            raise ValueError("max_tokens must be set before encoding")

        words = str(value).lower().strip().split()
        encoded = []

        for word in words:
            if not self.inference_mode and word not in self.word_to_id:
                self.word_to_id[word] = self.next_id
                self.id_to_word[self.next_id] = word
                self.next_id += 1
            encoded.append(self.word_to_id.get(word, 0))

        if len(encoded) > self.max_tokens:
            return encoded[:self.max_tokens]
        return encoded + [0] * (self.max_tokens - len(encoded))

    def decode(self, encoded_value: Union[int, List[int]]) -> str:
        """
        Decode either a single integer (classification) or list of integers (features)
        """
        if isinstance(encoded_value, (int, float)):
            return self.id_to_word.get(int(encoded_value), '<UNK>')

        words = []
        for idx in encoded_value:
            if idx != 0:  # Skip padding
                words.append(self.id_to_word.get(idx, '<UNK>'))
        return ' '.join(words)

class SimpleEncoder:
    def __init__(self, existing_dict: Dict[str, int] = None):
        self.string_encoder = StringEncoder(existing_dict)
        self.feature_types = {}
        self.encoders = {
            str: self.string_encoder,
            int: NumericEncoder(),
            float: NumericEncoder(),
            bool: BooleanEncoder()
        }

    def encode(self, samples: List[Sample], max_tokens: int) -> List[Sample]:
        self.string_encoder.set_max_tokens(max_tokens)
        
        encoded_samples = []
        for sample in samples:
            encoded_input = []
            for idx, value in enumerate(sample.input):
                encoder = self.encoders[type(value)]
                self.feature_types[idx] = type(value)
                encoded_value = encoder.encode(value)
                if isinstance(encoded_value, list):
                    encoded_input.extend(encoded_value)
                else:
                    encoded_input.append(encoded_value)

            encoded_output = None
            if sample.output is not None:
                if isinstance(sample.output, str):
                    print("\033[93mWarning: Multiple string _outputs not supported, only using the first word will be used for _outputs\033[0m")
                output_idx = len(sample.input)
                encoder = self.encoders[type(sample.output)]
                self.feature_types[output_idx] = type(sample.output)
                encoded_output = encoder.encode(sample.output)
                # Like multiple str _outputs not supported only use the first str _outputs
                if isinstance(encoded_output, list):
                    encoded_output = encoded_output[0]

            encoded_samples.append(Sample({
                '_inputs': encoded_input,
                '_outputs': encoded_output
            }))

        return encoded_samples

    def decode_prediction(self, prediction: Any, position: int) -> Any:
        if position not in self.feature_types:
            raise ValueError(f"Unknown feature position: {position}")

        return self.encoders[self.feature_types[position]].decode(prediction)

    @property
    def dictionary(self) -> Dict[str, int]:
        return self.string_encoder.word_to_id


