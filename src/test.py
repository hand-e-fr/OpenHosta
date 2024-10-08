from OpenHosta import config, emulate

config.set_default_apiKey("")

def multiply(a:int, b:int)->int:
    """
    This function multiplies two integers in parameter.
    """
    return emulate()

print(multiply(5, 6))
print(multiply._last_request)