from OpenHosta.OpenHosta import config, emulate
from typing import Optional, Union, List, Set, TypeVar

config.set_default_apiKey("")

T = TypeVar
def multiply(a:int, b:int)->Optional[int]:
    """
    This function multiplies two integers in parameters
    """
    return emulate()

print(multiply("hi", 6))