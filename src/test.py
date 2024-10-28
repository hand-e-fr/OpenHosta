from OpenHosta.OpenHosta import ask, config, emulate

config.set_default_apiKey("")
# res = ask(
#     system="You are an helpful assistant. Speak in french and answer with long text",
#     user="Hello, how are you ?",
#     max_tokens=50
# )
# print(res)
# print(ask._last_tokens)

def multiply(a:int, b:int)->int:
    """
    This function multiplies two integers in paramter.
    """
    return emulate()

print(multiply(5, 6))