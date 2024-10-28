from typing import List

from . import base

class IntEncoder(base.BaseEncoder):
    def encode(self, data: int) -> List[int]:
        return [int(data)]

    def decode(self, data: List[int]) -> int:
        if len(data) == 0:
            raise ValueError("Data is empty")
        return data[0]
