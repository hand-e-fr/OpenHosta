from abc import ABC, abstractmethod
from typing import Any, List, Union

class BaseEncoder(ABC):
    @abstractmethod
    def encode(self, data: Any) -> List[Union[int, float, bool, str]]:
        pass

    @abstractmethod
    def decode(self, data: List[Union[int, float, bool, str]]) -> Any:
        pass
