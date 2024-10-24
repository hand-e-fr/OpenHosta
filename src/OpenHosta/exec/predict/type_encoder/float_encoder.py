from typing import List, Union

from . import base

class FloatEncoder(base.BaseEncoder):
    def encode(self, data: Union[float, str]) -> List[float]:
        try:
            return [float(data)]
        except ValueError:
            raise ValueError("Provided value cannot be converted to float")
