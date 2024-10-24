from typing import List

from . import base

class IntEncoder(base.BaseEncoder):
    def encode(self, data: int) -> List[int]:
        return [int(data)]
