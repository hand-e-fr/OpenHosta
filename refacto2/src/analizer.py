from typing import Callable, Tuple, List, Dict, Any
import inspect
from types import FrameType

class _FuncInspector:
    def __init__(self, func: Callable):
        self.func = func
        self.sig = inspect.signature(func)


    def _get_function_signature(self):
        func_name = self.func.__name__
        func_params = ", ".join(
            [
                (
                    f"{param_name}: {param.annotation.__name__}"
                    if param.annotation != inspect.Parameter.empty and hasattr(param.annotation, '__name__')
                    else param_name
                )
                for param_name, param in self.sig.parameters.items()
            ]
        )
        func_return = (
            f" -> {self.sig.return_annotation.__name__}"
            if self.sig.return_annotation != inspect.Signature.empty and hasattr(self.sig.return_annotation, '__name__')
            else ""
        )
        return func_name, func_params, func_return


    def _get_function_definition(self):
        func_name, func_params, func_return = self._get_function_signature()
        definition = (
            f"```python\ndef {func_name}({func_params}):{func_return}\n"
            f"    \"\"\"\n    {self.func.__doc__}\n    \"\"\"\n```"
        )
        prototype = f"def {func_name}({func_params}):{func_return}"
        return definition, prototype


    def _get_call_info(self, caller_frame):
        _, _, _, values = inspect.getargvalues(caller_frame)

        values_args = {k: v for k, v in values.items() if k in self.sig.parameters}
        values_locals = {k: v for k, v in values.items() if k not in self.sig.parameters}

        values_locals.pop('self', None)

        bound_args = self.sig.bind_partial(**values_args)
        bound_args.apply_defaults()

        return bound_args.arguments, values_locals or None


    def _build_call_string(self, bound_arguments):
        args_str = ", ".join(
            f"{k}={v!r}" for k, v in bound_arguments.items()
        )
        call_str = f"{self.func.__name__}({args_str})"
        return call_str

    def _get_function_type(self):
        input_types = [param.annotation for param in self.sig.parameters.values()]
        output_type = self.sig.return_annotation if self.sig.return_annotation != inspect.Signature.empty else None
        return input_types, output_type
    


class FuncAnalizer(_FuncInspector):
    def __init__(self, func: Callable, caller_frame: FrameType):
        super().__init__(func)
        self.caller_frame = caller_frame

    @property
    def func_def(self) -> str:
        """
        This method returns the function definition and his prototype as a string
        """
        try:
            return self._get_function_definition()
        except:
            raise AttributeError("Function definition not found")

    @property
    def func_call(self) -> str:
        """
        This method returns the function call as a string
        """
        try:
            bound_args, _ = self._get_call_info(self.caller_frame)
            return self._build_call_string(bound_args)
        except:
            raise AttributeError("Function call not found")

    @property
    def func_args(self) -> Dict[str, object]:
        """
        This method returns the function arguments as a dictionary
        """
        try:
            bound_args, _ = self._get_call_info(self.caller_frame)
            return bound_args
        except:
            raise AttributeError("Function arguments not found")

    @property 
    def func_type(self) -> Tuple[List[type], type]:
        """
        This method returns the function input and output types as a tuple
        """
        try:
            return self._get_function_type()
        except:
            raise AttributeError("Function types not found")

    @property
    def func_locals(self) -> dict:
        """
        This method returns the function local variables as a dictionary
        """
        try:
            _, values_locals = self._get_call_info(self.caller_frame)
            return values_locals
        except:
            raise AttributeError("Function local variables not found")


#                   test                  #
###########################################



# def _get_infos_func(infos, func, current_frame) -> None:
#     """
#     parse a function to handle some infos
#     """
#     analizer = FuncAnalizer(func, current_frame)
#     infos.f_name   = func.__name__
#     infos.f_def, _ = analizer.func_def # car defintion + proto !
#     infos.f_call   = analizer.func_call
#     infos.f_args   = analizer.func_args
#     infos.f_type   = analizer.func_type
#     infos.f_locals = analizer.func_locals
#     print(infos.f_def)
#     print("*"*50)
#     print(infos.f_call)
#     print("*"*50)
#     print(infos.f_args)
#     print("*"*50)
#     print(infos.f_type)
#     print("*"*50)
#     print(infos.f_locals)


# class Func(BaseModel):
#     """
#     Func is a Pydantic model representing a function's metadata.
#     Useful for the executive functions and the post-processing.

#     Attributes:
#         f_def (str): Simple definition of the function, e.g., 'def func(a:int, b:str)->int:'
#         f_name (str): Name of the function, e.g., 'func'
#         f_call (str): Actual call of the function, e.g., 'func(1, 'salut')'
#         f_args (dict): Arguments of the function, e.g., {'a': 1, 'b': 'salut'}
#         f_type (object): desired type of the input and output of the function
#         f_locals (dict): Local variables within the function's scope
#     """
#     f_def: str
#     f_name: str
#     f_call: str
#     f_args: Dict[str, Any]
#     f_type: Tuple[List[Any], Any]
#     f_locals: Dict[str, Any]
# def test_my_hosta_injector(a: int, b: str) -> int:
#     """ A simple function for testing the HostaInjector class """
#     return a + int(b)

# if __name__ == "__main__":
#     infos = Func(
#         f_def="",
#         f_name="",
#         f_call="",
#         f_args={},
#         f_type=([], None),
#         f_locals={}
#     )
#     print("Début")
#     print("*" * 50)
#     _get_infos_func(infos, test_my_hosta_injector, inspect.currentframe())