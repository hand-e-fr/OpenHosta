import sys
from .OpenHosta import Models

_g_model = ""
_g_apiKey = ""

def model_config(model: Models, api_key: str) -> int:
    global _g_model, _g_apiKey

    try:
        if not type(model) is Models:
            raise ValueError("ValueError -> model")
        if not type(api_key) is str:
            raise ValueError("ValueError -> api_key")
    except ValueError as v:
        sys.stderr.write(f"[CONFIG_ERROR] {v}")   
        return -1
    finally:
        _g_model = model.value
        _g_apiKey = api_key
    return 0