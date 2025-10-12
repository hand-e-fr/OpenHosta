from typing import Callable
import platform

IS_UNIX = platform.system() != "Windows"

def print_last_prompt(function_pointer:Callable):
    """
    Print the last prompt sent to the LLM when using function `function_pointer`.
    """
    if hasattr(function_pointer, "hosta_inspection") and 'model' in function_pointer.hosta_inspection:
        print("Model\n-----------------\nname="+function_pointer.hosta_inspection['model'].model_name+"\nbasse_url="+function_pointer.hosta_inspection['model'].base_url+"\n")
        function_pointer.hosta_inspection['model'].print_last_prompt(function_pointer.hosta_inspection)
    else:
        print("No prompt found for this function.")


def print_last_decoding(function_pointer:Callable):
    """
    Print the steps of the last decoding when using function `function_pointer`.
    """
    if hasattr(function_pointer, "hosta_inspection") and 'model' in function_pointer.hosta_inspection:
        function_pointer.hosta_inspection['pipeline'].print_last_decoding(function_pointer.hosta_inspection)
    else:
        print("No prompt found for this function.")
