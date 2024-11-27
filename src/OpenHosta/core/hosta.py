from __future__ import annotations

from typing import List, Optional

from .analizer import FuncAnalizer
from .inspector import HostaInspector
from .pydantic_usage import Func
from ..utils.errors import InvalidStructureError
from ..utils.hosta_type import MemoryNode, MemKey, MemValue, ExampleType, CotType
import hashlib

all = (
    "Hosta",
    "Func",
    "UseType",
    "MemKey",
    "MemValue",
    "MemoryNode"
)


class Hosta(HostaInspector):
    """
    Hosta is a class that extends HostaInspector and provides functionality for analyzing
    and storing information about the calling function.

    This class implements a singleton pattern and uses introspection to gather details
    about the callable that called the function that instantiated it.

    If many function instantiated it in the same callable, the first function will create
    an instance and attach it to the callable so that the next function can retrieve it.

    Attributes:
        _initialized (bool): Flag to track if the instance has been initialized.
        _obj (tuple): Stores the result of the _extend method call.
        _infos (Func): Stores detailed information about the analyzed function.
    """
    _initialized = False
    _obj = None

    def __new__(cls, *args, **kwargs) -> 'Hosta':
        """
        Create a new instance of Hosta or return the existing one if already created.

        This method implements the singleton pattern, ensuring only one instance of Hosta exists.
        It also handles the initialization of the instance when first created.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
            > it's the arguments passed to __init__()

        Returns:
            Hosta: The single instance of the Hosta class.
        """
        cls._obj = cls._extend()
        if cls._obj[0] is None:
            raise InvalidStructureError(
                "[Hosta.__new__] The function {} must be called in a function/method."
                .format(cls._extend(back_level=2)[0].__name__)
            )
        if hasattr(cls._obj[0], "Hosta"):
            return cls._obj[0].Hosta
        instance = super().__new__(cls)
        cls.attach(cls._obj[0], {"Hosta": instance})
        return instance

    def __init__(self, *, caller_analysis: bool = True):
        """
        Initialize the Hosta instance.

        This method is called after __new__ and sets up the instance attributes.
        It also triggers the function analysis if caller_analysis is True.

        Args:
            caller_analysis (bool): If True, analyze the calling function. Defaults to True.
        """
        if not self._initialized:
            super().__init__()
            self._initialized = True
            self._infos = Func()
            if caller_analysis:
                self._get_infos_func()

    def _get_infos_func(self) -> None:
        """
        Analyze and store information about the calling function.

        This method uses FuncAnalizer to extract various details about the function
        that called the Hosta instance, including its name, definition, call signature,
        arguments, types, and local variables. This informations are useful in all OpenHosta's function.

        The extracted information is stored in the _infos attribute of the instance.
        """
        analizer = FuncAnalizer(self._obj[0], self._obj[1])
        self._infos.f_obj = self._obj[0]
        self._infos.f_name = self._obj[0].__name__
        self._infos.f_doc = self._obj[0].__doc__
        self._infos.f_def = analizer.func_def
        self._infos.f_call, self._infos.f_args = analizer.func_call
        self._infos.f_type = analizer.func_type
        self._infos.f_locals, self._infos.f_self = analizer.func_locals
        self._infos.f_schema = analizer.func_schema
        self._infos.f_sig = analizer.sig
        
    def _update_call(self):
        analizer = FuncAnalizer(self._obj[0], self._obj[1])
        self._infos.f_call, self._infos.f_args = analizer.func_call
        return self
        

    def _bdy_add(self, key: MemKey, value: MemValue) -> None:
        """
        Add a new memory node to the function's memory.

        This method creates a new MemoryNode with the given key and value,
        and appends it to the function's memory list. If the memory list
        doesn't exist, it initializes it.

        Args:
            key (MemKey): The type of memory node ('ex', 'cot', or 'use').
            value (MemValue): The value to be stored in the memory node.
        """
        seen: List[MemKey] = []

        if self._infos.f_mem is None:
            self._infos.f_mem = []
            mem_id = 0
        else:
            mem_id = 0
            for node in self._infos.f_mem:
                if node.key == key:
                    mem_id += 1
        new = MemoryNode(key=key, id=mem_id, value=value)
        self._infos.f_mem.append(new)
        previous = new
        for node in self._infos.f_mem:
            if node.key not in seen:
                seen.append(node.key)
                previous = node
            elif node.key in seen and node.key == previous.key:
                previous = node
            else:
                raise InvalidStructureError(
                    "[Hosta._bdy_add] Inconsistent function structure. Place your OpenHosta functions per block.")

    def _bdy_get(self, key: MemKey) -> List[MemoryNode]:
        """
        Retrieve memory nodes of a specific type from the function's memory.

        This method searches through the function's memory list and returns
        all nodes that match the given key.

        Args:
            key (MemKey): The type of memory node to retrieve ('ex', 'cot', or 'use').

        Returns:
            List[MemoryNode]: A list of memory nodes matching the key, or None if no matches are found.
        """
        l_list: List[MemoryNode] = []

        if self._infos.f_mem is None:
            return None
        for node in self._infos.f_mem:
            if node.key == key:
                l_list.append(node)
        return l_list if l_list != [] else None

    @property
    def example(self) -> Optional[List[ExampleType]]:
        """
        Retrieve all example nodes from the function's memory.

        This property method uses _bdy_get to fetch all memory nodes with the 'ex' key.

        Returns:
            Optional[List[ExampleType]]: A list of example nodes, or None if no examples are found.
        """
        nodes = self._bdy_get(key="ex")
        return [node.value for node in nodes] if nodes else None

    @property
    def cot(self) -> Optional[List[CotType]]:
        """
        Retrieve all chain-of-thought (cot) nodes from the function's memory.

        This property method uses _bdy_get to fetch all memory nodes with the 'cot' key.

        Returns:
            Optional[List[CotType]]: A list of chain-of-thought nodes, or None if no cot nodes are found.
        """
        nodes = self._bdy_get(key="cot")
        return [node.value for node in nodes] if nodes else None

    @property
    def infos(self):
        return self._infos

    @staticmethod
    def hash_func(func: Func) -> str:
        """
        Generate a hash value for a function without use builtin python hash function.

        This method generates a hash value for a function using a custom algorithm
        Hashed by func.f_doc, func.f_def, func.f_call, func.f_args, func.f_type, func.f_schema, func.f_locals, func.f_self

        Args:
            func (object): The function to hash.

        Returns:
            str: The hash value of the function.
        """
        return hashlib.md5(
            str(func.f_def).encode() +
            str(func.f_type).encode()
        ).hexdigest()
