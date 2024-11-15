from __future__ import annotations

from typing import Tuple, Callable, Optional, Dict, Any, Union
from types import FrameType, CodeType, MethodType
import inspect

from ..utils.errors import FrameError

all = (
    "HostaInspector"
)


class HostaInspector:
    """
    This class is the parent class for a lot of OpenHosta functionnality.
    It provides methods which are used in many cases.
    """

    def __init__(self):
        pass

    @staticmethod
    def _extend(*, back_level: int = 3) -> Tuple[Union[Callable, MethodType], FrameType]:
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
            func: Union[Callable, MethodType]

            obj = caller.f_locals["self"]
            func = getattr(obj, caller_name, None)
            return inspect.unwrap(func) if func else None

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
            func: Union[Callable, MethodType]
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
            func = caller.f_globals.get(name)
            return inspect.unwrap(func) if func else None

        func: Union[Callable, MethodType]
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
            func = _get_obj_from_class(caller)
        else:
            func = _get_obj_from_func(caller, caller_code, caller_name)

        if func is not None and not callable(func):
            raise FrameError(
                "[HostaInspector._extend] The foud object isn't a callable.")

        return (func, caller)

    @staticmethod
    def _attach(obj: Callable, attr: Dict[str, Any]) -> Optional[bool]:
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
