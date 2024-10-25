from OpenHosta.OpenHosta import ask, config

config.set_default_apiKey("")

res = ask(
    system="You are an helpful assistant. Speak in french and answer with long text",
    user="Hello, how are you ?",
    max_tokens=50
)
print(res)
print(ask._last_tokens)