from typing import List, Any, Dict, Union, Tuple

from .base_encoder import BaseEncoder


class StringEncoder(BaseEncoder):
    """
    Encoder for string values. Create a Optimized little w2v fo each words present in the dataset.
    Example:
        - 'hello' -> 1
        - 'world' -> 2
        - 'hello' -> 1 (same as first time) 
    """

    def __init__(self) -> None:
        self.word_to_id: Dict[str, int] = {'<UNK>': 0}
        self.id_to_word: Dict[int, str] = {0: '<UNK>'}
        self.next_word_id: int = 1

    def encode(self, value: str) -> int:
        value = value.lower().strip()
        if value not in self.word_to_id:
            self.word_to_id[value] = self.next_word_id
            self.id_to_word[self.next_word_id] = value
            self.next_word_id += 1
        return self.word_to_id[value]

    def decode(self, encoded_value: List[int]) -> str:
        return self.id_to_word.get(encoded_value, '<UNK>')

    def vocabulary(self, word: str) -> List[int]:
        return [self.word_to_id.get(word, 0)]

    @property
    def get_vocabulary(self) -> Dict[str, int]:
        return self.word_to_id


class IntEncoder(BaseEncoder):
    """
    Encoder for integer values. No encoding is done, the value is returned as is.
    """

    def encode(self, value: int) -> int:
        return value

    def decode(self, encoded_value: float) -> int:
        return int(encoded_value)


class FloatEncoder(BaseEncoder):
    def encode(self, value: float) -> float:
        return value

    def decode(self, encoded_value: float) -> float:
        return encoded_value


class BoolEncoder(BaseEncoder):
    def encode(self, value: bool) -> int:
        return 1 if value else 0

    def decode(self, encoded_value: int) -> bool:
        return bool(encoded_value)


class SimpleEncoder:
    def __init__(self):
        self._encoders = {
            str: StringEncoder(),
            int: IntEncoder(),
            float: FloatEncoder(),
            bool: BoolEncoder()
        }

    def encode_dataset(self, data: List[List[Any]]) -> Tuple[List[List[Union[int, float]]], List[int]]:
        if not data:
            return [], []

        features_list = []
        targets_list = []

        for sample in data:
            features, target = sample[:-1], sample[-1]
            encoded_features = []

            for value in features:
                encoder = self._encoders[type(value)]
                encoded_features.append(encoder.encode(value))

            features_list.append(encoded_features)

            target_encoder = self._encoders[type(target)]
            targets_list.append(target_encoder.encode(target))

        return features_list, targets_list

    def decode_dataset(self, features_list: List[List[Union[int, float]]], targets_list: List[int],
                       feature_types: List[type], target_type: type) -> List[List[Any]]:
        decoded_data = []

        for features, target in zip(features_list, targets_list):
            decoded_features = []
            for value, dtype in zip(features, feature_types):
                encoder = self._encoders[dtype]
                decoded_features.append(encoder.decode(value))

            target_encoder = self._encoders[target_type]
            decoded_target = target_encoder.decode(target)

            decoded_data.append(decoded_features + [decoded_target])

        return decoded_data

# Exemple d'utilisation
# if __name__ == "__main__":
#     encoders = SimpleEncoder()

#     data = [
#         ['hello', 10, 10.5, True, 'world'],
#         ['world', 20, 20.5, False, 'hello']
#     ]

#     data_2 = [
#         [['hello', 10, 10.5, True], ['world']],
#         [['world', 20, 20.5], ['hello']]
#     ]

#     # Encodage
#     features_list, targets_list = encoders.encode_dataset(data)
#     print("Features de base:", data[0][:-1], data[1][:-1])
#     print("Features encodées:", features_list)
#     print("Target de base:", [data[0][-1]], [data[1][-1]])
#     print("Targets encodées:", targets_list)

#     # Pour voir le vocabulaire des strings
#     string_encoder = encoders._encoders[str]
#     print("Vocabulaire:", string_encoder.word_to_id)

#     # Décodage (si nécessaire)
#     feature_types = [str, int, float, bool]
#     target_type = str
#     decoded_data = encoders.decode_dataset(features_list, targets_list, feature_types, target_type)
#     print("Données décodées:", decoded_data)
