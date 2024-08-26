import sys
from analytics import Models
from emulate import set_api_key, set_model

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
        set_model(model.value)
        set_api_key(api_key)
    return 0