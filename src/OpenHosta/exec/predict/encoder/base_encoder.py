from abc import ABC, abstractmethod
from typing import List, Union

class BaseEncoder(ABC):
    @abstractmethod
    def encode(self, data: Union[int, float, bool, str]) -> List[Union[int, float]]:
        pass

    @abstractmethod
    def decode(self, data: List[float]) -> Union[int, float, bool, str]:
        pass
