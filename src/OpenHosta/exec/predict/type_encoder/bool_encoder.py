from typing import List

from . import base

class BoolEncoder(base.BaseEncoder):
    def encode(self, data: bool) -> List[int]:
        return [1 if data else 0]
