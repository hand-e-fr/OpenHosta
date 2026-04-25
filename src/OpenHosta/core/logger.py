from typing import Callable, cast, Any, Optional, Union
from .inspection import HostaInjectedFunction, Inspection
import platform
import json

IS_UNIX = platform.system() != "Windows"


def _get_inspection(target: Any) -> Optional[Inspection]:
    """Helper to extract Inspection from either a function or a Guarded value."""
    if hasattr(target, "hosta_inspection"):
        return target.hosta_inspection
    if hasattr(target, "_hosta_inspection"):
        return target._hosta_inspection
    return None


def conversation(target: Any):
    """Alias for print_last_prompt."""
    print_last_prompt(target)


def readable(target: Any) -> str:
    """
    Returns a clean, stable string representation of a Guarded value.
    Guaranteed to be parseable back into the same type.
    """
    from ..guarded.primitives import GuardedPrimitive, ProxyWrapper
    
    val = target
    if isinstance(target, (GuardedPrimitive, ProxyWrapper)):
        val = target.unwrap()
    
    if isinstance(val, (list, dict, set, tuple)):
        try:
            return json.dumps(val, indent=2, ensure_ascii=False)
        except (TypeError, ValueError):
            return str(val)
    
    return str(val)


def markdown(target: Any) -> str:
    """
    Returns a markdown-formatted version of the value.
    """
    text = readable(target)
    if "\n" in text or text.startswith(("[", "{")):
        return f"```python\n{text}\n```"
    return text


def print_last_prompt(target: Union[Callable, Any]):
    """
    Print the last prompt sent to the LLM when using function or value `target`.
    """
    inspection = _get_inspection(target)
    
    if inspection and inspection.model is not None:
        print(f"Model\n-----------------\nname={inspection.model.model_name}\nbase_url={inspection.model.base_url}\n")
        inspection.model.print_last_prompt(inspection)
    
        if "enum_normalized_probs" in inspection.logs:
            print("-----------------")
            print_last_uncertainty(target)        
    else:
        print("No prompt found for this target.")


def print_last_decoding(target: Union[Callable, Any]):
    """
    Print the steps of the last decoding when using function or value `target`.
    """
    inspection = _get_inspection(target)

    if inspection and inspection.model is not None:
        inspection.pipeline.print_last_decoding(inspection)
    else:
        print("No decoding logs found for this target.")


def print_last_probability_distribution(target: Union[Callable, Any]):
    """
    Print the last probability distribution log when using function or value `target`.
    """
    inspection = _get_inspection(target)
    if inspection and "enum_normalized_probs" in inspection.logs:
        nomalized_probs = inspection.logs["enum_normalized_probs"]
        for k, v in nomalized_probs.items():
            print(f"Value: {k:<10}, Probability: {v:.4f}")


def print_last_uncertainty(target: Union[Callable, Any]):
    """
    Print the last uncertainty log when using function or value `target`.
    """
    inspection = _get_inspection(target)
    if inspection and "enum_normalized_probs" in inspection.logs:
        nomalized_probs = inspection.logs["enum_normalized_probs"]

        for k, v in nomalized_probs.items():
            print(f"Value: {k:<10}, Certainty: {v}")
                
        if "uncertainty_counters" in inspection.logs:
                counters = inspection.logs["uncertainty_counters"]
                print("------")
                for k, v in counters.items():
                    print(f"{k:<20}: {v}")
            
    else:
        print("No uncertainty logs found.")
