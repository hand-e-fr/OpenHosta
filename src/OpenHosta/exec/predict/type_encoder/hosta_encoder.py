from typing import Any, List, Union

from .int_encoder import IntEncoder
from .float_encoder import FloatEncoder
from .bool_encoder import BoolEncoder

class HostaEncoder:
    def __init__(self) -> None:
        self.encoders = {
            int: IntEncoder(),
            float: FloatEncoder(),
            str: FloatEncoder(),  # Attempt to convert string to float
            bool: BoolEncoder(),
        }

    def encode(self, value: Any) -> List[Union[int, float, bool, str]]:
        value_type = type(value)
        if value_type in self.encoders:
            return self.encoders[value_type].encode(value)
        else:
            raise ValueError(f"Type {value_type} not supported")
