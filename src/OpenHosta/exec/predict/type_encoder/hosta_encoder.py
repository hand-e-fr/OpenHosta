from typing import Any, List, Union

from .int_encoder import IntEncoder
from .float_encoder import FloatEncoder
from .bool_encoder import BoolEncoder

class HostaEncoder:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(HostaEncoder, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self.encoders = {
            int: IntEncoder(),
            float: FloatEncoder(),
            str: FloatEncoder(),  # Attempt to convert string to float
            bool: BoolEncoder(),
        }
        self._initialized = True

    def encode(self, value: Union[int, float, bool, str]) -> List[Union[int, float, bool, str]]:
        value_type = type(value)
        if value_type in self.encoders:
            return self.encoders[value_type].encode(value)
        else:
            raise ValueError(f"Type {value_type} not supported")

    def decode(self, data: List[Union[int, float, bool, str]]) -> Union[int, float, bool, str]:
        if len(data) == 0:
            raise ValueError("Data is empty")
        value_type = type(data[0])
        if value_type in self.encoders:
            return self.encoders[value_type].decode(data)
        else:
            raise ValueError(f"Type {value_type} not supported")
