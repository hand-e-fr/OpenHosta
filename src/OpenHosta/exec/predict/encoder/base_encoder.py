from abc import ABC, abstractmethod
from typing import List, Union,Any

class BaseEncoder(ABC):
    @abstractmethod
    def encode(self, data: Any) -> Union[int, float]:
        """Encode a single value"""
        pass

    @abstractmethod
    def decode(self, encoded_value: Any) -> Any:
        """Decode a prediction back to its original type"""
        pass
