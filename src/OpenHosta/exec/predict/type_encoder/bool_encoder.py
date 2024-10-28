from typing import List

from . import base

class BoolEncoder(base.BaseEncoder):
    def encode(self, data: bool) -> List[int]:
        return [1 if data else 0]

    def decode(self, data: List[int]) -> bool:
        if len(data) == 0:
            raise ValueError("Data is empty")
        return bool(data[0])
