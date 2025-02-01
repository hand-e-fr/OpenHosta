from typing import Callable, Optional, Union, Literal

_doctype_predict="""
    This function is not available.
    To install it run:
    pip install OpenHosta[predict]
"""

_predict_error = NotImplementedError("This function is not available. To install it run: pip install OpenHosta[predict]")

def generate_data(
        function_pointer: Callable,
        ammount: int,
        oracle = None,
        verbose: Union[Literal[0, 1, 2], bool] = 2
):
    f"""{_doctype_predict}"""
    raise _predict_error

def generate_data_async(
        function_pointer: Callable,
        ammount: int,
        oracle = None,
        verbose: Union[Literal[0, 1, 2], bool] = 2
):
    f"""{_doctype_predict}"""
    raise _predict_error

def predict(
    config = None,
    oracle = None,
    verbose: Union[Literal[0, 1, 2], bool] = 0
) -> Union[int, float, bool, str]:
    f"""{_doctype_predict}"""
    raise _predict_error

def predict_async(
    config = None,
    oracle = None,
    verbose: Union[Literal[0, 1, 2], bool] = 0
) -> Union[int, float, bool, str]:
    f"""{_doctype_predict}"""
    raise _predict_error

class HostaDataset:
    def __init__(self, log):
        f"""{_doctype_predict}"""
        raise _predict_error

class SourceType:
    def __init__(self):    
        f"""{_doctype_predict}"""
        raise _predict_error

class PredictConfig:
    def __init__(self,
                name: str = None,
                path: str = None,
                complexity: int = 5,
                growth_rate: float = 1.5,
                coef_layers : int = 100,
                normalize: bool = False,
                epochs: Optional[int] = None,
                batch_size: Optional[int] = None,
                max_tokens: int = 1,
                dataset_path: Optional[str] = None,
                generated_data: Optional[int] = 100,
            ):
        f"""{_doctype_predict}"""
        raise _predict_error
