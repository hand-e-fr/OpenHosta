from OpenHosta import config, emulate
import os

config.set_default_apiKey(os.environ['OPENAI_KEY'])

def multiply(a:int, b:int):
    """
    This function multiplies two integers in parameter.
    """
    return emulate()

res = multiply(5, 6)
print(res)
print(type(res))
print(multiply._last_request)