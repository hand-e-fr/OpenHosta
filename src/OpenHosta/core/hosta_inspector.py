from __future__ import annotations

from typing import List, Optional
from typing import Tuple, Callable, Optional, Dict, Any, Union
from types import FrameType, CodeType, MethodType

import hashlib
import inspect

from .analizer import FuncAnalizer
from .pydantic_usage import FunctionMetadata
from ..utils.errors import InvalidStructureError
from ..utils.hosta_type import MemoryNode, MemKey, MemValue, ExampleType, CotType
from ..utils.errors import FrameError

all = (
    "HostaInspector"
)

class HostaInspector:
    """
    HostaInspector is a class that provides functionality for analyzing
    and storing information about the calling function.

    This class uses introspection to gather details
    about the callable that called the function that instantiated it.

    If many function instantiate it for the same callable, the first function will create
    an instance and attach it to the callable so that the next function can retrieve it.
    """

    def __new__(cls, *args, **kwargs) -> HostaInspector:
        """
        Create a new instance of Hosta or return the existing one if already created.

        This method implements the singleton pattern, ensuring only one instance of Hosta exists.
        It also handles the initialization of the instance when first created.

        Returns:
            Hosta: The single instance of the Hosta class.
        """
        caller_function, caller_frame = cls._find_caller_function()
        
        if caller_function is None:
            raise InvalidStructureError(
                "[HostaInspector.__new__] The function {} must be called in a function/method."
                .format(cls._find_caller_function(back_level=2)[0].__name__)
            )
        
        if hasattr(caller_function, "hosta_data"):
            hosta_inspection, = caller_function.hosta_inspection
            hosta_inspection._update_call()
        else:
            hosta_inspection = super(HostaInspector, cls).__new__(cls)
            hosta_inspection.caller_function = caller_function
            hosta_inspection.caller_frame = caller_frame
            cls.attach(caller_function, {"hosta_inspection": hosta_inspection})

        return hosta_inspection

    def __init__(self, caller_function=None, caller_frame=None):
        """
        Initialize the Hosta instance.

        This method is called after __new__ and sets up the instance attributes.
        It also triggers the function analysis if caller_analysis is True.

        Args:
            caller_analysis (bool): If True, analyze the calling function. Defaults to True.
        """
        # Set by __new__()
        # print("caller_function: ",self.caller_function)
        # print("caller_frame: ",self.caller_frame)

        self._infos = FunctionMetadata()
        self._get_infos_func()

    def _get_infos_func(self) -> None:
        """
        Analyze and store information about the calling function.

        This method uses FuncAnalizer to extract various details about the function
        that called the Hosta instance, including its name, definition, call signature,
        arguments, types, and local variables. This informations are useful in all OpenHosta's function.

        The extracted information is stored in the _infos attribute of the instance.
        """
        analizer = FuncAnalizer(self.caller_function, self.caller_frame)
        self._infos.f_obj  = self.caller_function
        self._infos.f_name = self.caller_function.__name__
        self._infos.f_doc  = self.caller_function.__doc__
        self._infos.f_def                        = analizer.func_def
        self._infos.f_call, self._infos.f_args   = analizer.func_call
        self._infos.f_type                       = analizer.func_type
        self._infos.f_locals, self._infos.f_self = analizer.func_locals
        self._infos.f_schema                     = analizer.func_schema
        self._infos.f_sig                        = analizer.sig
        
    def _update_call(self):
        analizer = FuncAnalizer(self.caller_function, self.caller_frame)
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
    
    def set_logging_object(self, logging_object: object) -> None:
        self.attach(self._infos.f_obj, logging_object)

    @property
    def example(self) -> Optional[List[ExampleType]]:
        """
        Retrieve all example nodes from the function's memory.

        This property method uses _bdy_get to fetch all memory nodes with the 'ex' key.

        Returns:
            Optional[List[ExampleType]]: A list of example nodes, or None if no examples are found.
        """
        nodes = self._bdy_get(key="ex")
        return [node.value for node in nodes] if nodes else []

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
    def hash_func(function_metadata: FunctionMetadata) -> str:
        """
        Generate a hash value for a function without use builtin python hash function.

        This method generates a hash value for a function using a custom algorithm
        Hashed by function_metadata.f_doc, function_metadata.f_def, function_metadata.f_call, function_metadata.f_args, function_metadata.f_type, function_metadata.f_schema, function_metadata.f_locals, function_metadata.f_self

        Args:
            function_metadata (object): The function to hash.

        Returns:
            str: The hash value of the function.
        """
        return hashlib.md5(
            str(function_metadata.f_def).encode() +
            str(function_metadata.f_type).encode()
        ).hexdigest()
    
    @staticmethod
    def _find_caller_function(*, back_level: int = 3) -> Tuple[Union[Callable, MethodType], FrameType]:
        """
        Retrieves the callable object and the frame from which this method is called.

        This method navigates up the call stack to find the function or method that called it.
        It can retrieve the callable object from both class methods and standalone functions.

        This method uses introspection to examine the call stack and local variables.
        It may not work correctly in all execution environments or with all types of callable objects.

        Args:
            - back_level (int, optional): The number of frames to go back in the call stack. 
                Defaults to 2. Must be a non-zero positive integer.

        Returns:
            Tuple[Callable, FrameType]: A tuple containing:
                - The callable object (function or method) that called this method.
                - The frame object of the caller.
        """
        if back_level <= 0 or not isinstance(back_level, int):
            raise ValueError(
                f"[HostaInspector._extend] back_level must a non-zero positive integers.")

        def _get_obj_from_class(caller: FrameType) -> Optional[Callable]:
            """
            Search for the callable object when it is called within a class method.

            This function attempts to retrieve the method from the 'self' object
            in the caller's local variables. It's designed for internal use only, 
            within the _extend method.

            Args:
                caller (FrameType): The frame object of the calling method.

            Returns:
                Callable: The unwrapped method object if found, otherwise None.
            """
            function_pointer: Union[Callable, MethodType]

            obj = caller.f_locals["self"]
            function_pointer = getattr(obj, caller_name, None)
            return inspect.unwrap(function_pointer) if function_pointer else None

        def _get_obj_from_func(
            caller: FrameType,
            code: CodeType,
            name: str
        ) -> Optional[Callable]:
            """
            Search for the callable object when it is called within a function.

            This function traverses the call stack, examining local and global variables
            to find the function that matches the given code object. It's designed for
            internal use only, within the _extend method.

            Args:
                - caller (FrameType): The frame object of the calling function.
                - code (CodeType): The code object of the calling function.
                - name (str): The name of the calling function.

            Returns:
                Callable: The unwrapped function object if found, otherwise None.
            """
            function_pointer: Union[Callable, MethodType]
            l_caller: FrameType = caller

            while not l_caller.f_back is None:
                for obj in l_caller.f_back.f_locals.values():
                    try:
                        if hasattr(obj, "__code__"):
                            if obj.__code__ == code:
                                return obj
                    except:
                        continue
                l_caller = l_caller.f_back
            function_pointer = caller.f_globals.get(name)
            return inspect.unwrap(function_pointer) if function_pointer else None

        function_pointer: Union[Callable, MethodType]
        current: Optional[FrameType] = inspect.currentframe()

        if current is None:
            raise FrameError(
                f"[HostaInspector._extend] Current frame can't be found")
        for k in range(back_level):
            current = current.f_back
            if current is None:
                raise FrameError(
                    f"[HostaInspector._extend] Frame can't be found (level: {k})")

        caller = current
        caller_name = caller.f_code.co_name
        caller_code = caller.f_code
        caller_args = inspect.getargvalues(caller)

        is_likely_method = "self" in caller.f_locals or\
            'cls' in caller.f_locals or\
            (caller_args.args and caller_args.args[0] in ['self', 'cls'])
        if is_likely_method:
            function_pointer = _get_obj_from_class(caller)
        else:
            function_pointer = _get_obj_from_func(caller, caller_code, caller_name)

        if function_pointer is not None and not callable(function_pointer):
            raise FrameError(
                "[HostaInspector._extend] The foud object isn't a callable.")

        return function_pointer, caller

    @staticmethod
    def attach(obj: Callable, attr: Dict[str, Any]) -> Optional[bool]:
        """
        Attaches attributes to a function or method.

        This method attempts to add new attributes to a callable object (function or method).
        For methods, it attaches the attributes to the underlying function object.
        Only supports attaching to functions and methods. Other callable types will raise an AttributeError.

        Args:
            - obj (Callable): The function or method to which the attribute will be attached.
            - attr (Dict[str, Any]): The dictionary of the attributes to attach.

        Return:
            Optional[bool]: Returns True if the attribute was successfully attached, raise an Exception otherwise. 
        """
        if not callable(obj) or not isinstance(attr, dict):
            raise ValueError("[HostaInspector._attach] Invalid arguments")

        def attr_parser(obj: Callable, attr: Dict[str, Any]) -> None:
            for key, value in attr.items():
                setattr(obj, key, value)

        if inspect.ismethod(obj):
            if hasattr(obj, "__func__"):
                attr_parser(obj.__func__, attr)
                return True
            raise AttributeError(
                f"[HostaInspector._attach] Failed to attach attributs. \"__func__\" attribut is missing.")
        
        elif inspect.isfunction(obj):
            attr_parser(obj, attr)
            return True
        
        raise AttributeError(
            f"[HostaInspector._attach] Failed to attach attributs. Object's type not supported: {type(obj)}.")



all = (
    "FuncAnalizer",
    "UseType",
    "MemKey",
    "MemValue",
    "MemoryNode"
)

