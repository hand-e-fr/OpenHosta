from __future__ import annotations

from sys import version_info
from typing import Type, Any, Dict, Optional, Callable, TypeVar

from .hosta_inspector import FunctionMetadata
from ..utils.import_handler import is_pydantic_enabled

T = TypeVar('T')

if version_info.major == 3 and version_info.minor > 9:
    from types import NoneType
else:
    NoneType = type(None)

class TypeConverter:
    """
    A class used to check and convert the outputs of a Language Model (LLM) to the type specified in a function's annotation.

    Args:
        function_metadata (FunctionMetadata): A function object that contains the type annotations for the LLM outputs.
        data (dict): A dictionary containing the LLM outputs data to be checked and converted.

    Attributes:
        function_metadata (FunctionMetadata): The function object containing the type annotations for the LLM outputs.
        data (dict): The LLM outputs data to be checked and converted.
        checked (Any): The checked and converted data. If `data` contains a "return" key, its value is used as the checked data. Otherwise, `data` is used as the checked data.
        is_passed (bool): A flag indicating whether the checked data should be converted or not. It is set to True if `data` contains a "return" key.
    """

    def __init__(self, function_metadata: FunctionMetadata, data: dict):
        self.function_metadata = function_metadata
        self.data = data
        try:
            self.checked = self.data["return"]
            self.is_passed = True
        except KeyError:
            self.checked = self.data
            self.is_passed = False

    def _default(x: Any) -> Any:
        """
        A default conversion function that returns the _inputs as is.

        Args:
            x (Any): The _inputs data to be converted.

        Returns:
            Any: The _inputs data as is.
        """
        return x

    def convert(self, typ: Type[T]) -> Callable[[Any], T]:
        """
        A method to create a conversion function for a given type.

        Args:
            typ (Type[T]): The type for which a conversion function needs to be created.

        Returns:
            Callable[[Any], T]: A conversion function for the given type.
        """
        convert_map = {
            NoneType: lambda x: None,
            str: str,
            int: int,
            float: float,
            list: list,
            set: set,
            frozenset: frozenset,
            tuple: tuple,
            bool: bool,
            dict: dict,
            complex: complex,
            bytes: lambda x: bytes(x, encoding='utf-8') if isinstance(x, str) else bytes(x),
        }
        return convert_map.get(typ, self._default.__func__)

    def check(self) -> Any:
        """
        A method to check and convert the _inputs data based on the function's type annotations and Pydantic model annotations.

            Returns:
                Any: The checked and converted data. If `data` contains a "return" key, its value is used as the checked data. Otherwise, `data` is used as the checked data.
        """
        if self.checked == "None" or self.checked is None:
            return None
        if self.is_passed:
            self.checked = self.convert(self.function_metadata.f_type[1])(self.checked)
            if is_pydantic_enabled:
                from .pydantic_usage import convert_pydantic

                self.checked = convert_pydantic(self.function_metadata.f_type[1], self.checked)
        return self.checked
