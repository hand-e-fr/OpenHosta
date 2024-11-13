from abc import ABC, abstractmethod
from typing import List, Any, Dict, Union

from ..dataset.sample_type import Sample


# from ..dataset.sample_type import Sample  # Ensure that the Sample class is correctly defined in this module

class BaseEncoder(ABC):
    @abstractmethod
    def encode(self, data: Any) -> Union[int, float]:
        """Encode a single value"""
        pass

    @abstractmethod
    def decode(self, encoded_value: Any) -> Any:
        """Decode a prediction back to its original type"""
        pass

class StringEncoder(BaseEncoder):
    def __init__(self, existing_dict: Dict[str, int] = None):
        """
        Initialize with optional existing dictionary
        """
        self.word_to_id = {'<UNK>': 0} if existing_dict is None else existing_dict
        self.id_to_word = {v: k for k, v in self.word_to_id.items()}
        self.next_id = max(self.word_to_id.values()) + 1 if self.word_to_id else 1

    def encode(self, value: str) -> int:
        """
        Encode a string value to integer
        """
        value = str(value).lower().strip()
        if value not in self.word_to_id:
            self.word_to_id[value] = self.next_id
            self.id_to_word[self.next_id] = value
            self.next_id += 1
        return self.word_to_id[value]

    def decode(self, encoded_value: int) -> str:
        """
        Decode an integer back to string
        """
        return self.id_to_word.get(encoded_value, '<UNK>')

    def limit_vocab(self, max_tokens: int):
        """
        Limit vocabulary size to max_tokens
        """
        if len(self.word_to_id) > max_tokens:
            sorted_tokens = sorted(
                self.word_to_id.items(),
                key=lambda x: x[1]
            )[:max_tokens]
            
            self.word_to_id = {'<UNK>': 0}
            self.id_to_word = {0: '<UNK>'}
            
            for idx, (token, _) in enumerate(sorted_tokens[1:], start=1):
                self.word_to_id[token] = idx
                self.id_to_word[idx] = token
            
            self.next_id = max_tokens

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

class EnhancedEncoder:
    def __init__(self, existing_dict: Dict[int, Dict[str, int]] = None):
        """
        Initialize with optional existing dictionary for each feature position
        """
        self.encoders = {}
        self.feature_types = {}
        self.string_encoders = {}
        if existing_dict:
            for pos, vocab in existing_dict.items():
                self.string_encoders[int(pos)] = StringEncoder(vocab)

    def _get_encoder(self, value: Any, position: int) -> BaseEncoder:
        """
        Get or create appropriate encoder for a value type
        """
        if isinstance(value, str):
            if position not in self.string_encoders:
                self.string_encoders[position] = StringEncoder()
            return self.string_encoders[position]
        elif isinstance(value, bool):
            return BooleanEncoder()
        elif isinstance(value, (int, float)):
            return NumericEncoder()
        else:
            raise ValueError(f"Unsupported type: {type(value)}")

    def encode(self, samples: List[Sample], max_tokens: int) -> List[Sample]:
        """
        Encode a list of samples
        
        Args:
            samples: List of Sample objects
            max_tokens: Maximum vocabulary size for string features
            
        Returns:
            List of encoded Sample objects
        """
        encoded_samples = []
        # print("in samples")
        # First pass: encode all values and build vocabularies
        for sample in samples:
            encoded_input = []
            for idx, value in enumerate(sample.input):
                encoder = self._get_encoder(value, idx)
                self.feature_types[idx] = type(value)
                encoded_input.append(encoder.encode(value))

            encoded_output = None
            if sample.output is not None:
                output_idx = len(sample.input)
                encoder = self._get_encoder(sample.output, output_idx)
                self.feature_types[output_idx] = type(sample.output)
                encoded_output = encoder.encode(sample.output)

            encoded_samples.append(Sample({
                'input': encoded_input,
                'output': encoded_output
            }))

        # Limit vocabulary sizes for string features
        for encoder in self.string_encoders.values():
            encoder.limit_vocab(max_tokens)
        print("finish encoding here yes")
        return encoded_samples

    def decode_prediction(self, prediction: Any, position: int) -> Any:
        """
        Decode a single prediction
        
        Args:
            prediction: The value to decode
            position: Feature position for proper decoder selection
            
        Returns:
            Decoded value in original type
        """
        if position not in self.feature_types:
            raise ValueError(f"Unknown feature position: {position}")

        encoder = self._get_encoder(self.feature_types[position](), position)
        return encoder.decode(prediction)

    @property
    def dictionary(self) -> Dict[int, Dict[str, int]]:
        """
        Get the current string encoding dictionary
        """
        return {pos: encoder.word_to_id 
                for pos, encoder in self.string_encoders.items()}
    


# # Initialisation avec dictionnaire existant optionnel
# existing_dict = {0: {'chat': 1, 'chien': 2}}
# encoder = EnhancedEncoder(existing_dict)
# your_samples = Sample({'input': 'chat', 'output': 'chien'})
# # Encodage des samples
# encoded_samples = encoder.encode(samples=your_samples, max_tokens=1000)

# # Décodage d'une prédiction
# decoded_value = encoder.decode_prediction(prediction=1, position=0)  # 'chat'

# # Accès au dictionnaire final
# final_dict = encoder.dictionary