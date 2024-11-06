from OpenHosta import config, emulate

config.set_default_apiKey("")

def multiply(a:int, b:int):
    """
    This function multiplies two integers in parameter.
    """
    return emulate()

res = multiply(5, 6)
print(res)
print(type(res))
print(multiply._last_request)