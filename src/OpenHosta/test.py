from OpenHosta import config, emulate

gptmini = config.Model(
    model="gpt-4o-mini",
    base_url="https://api.openai.com/v1/chat/completions",
    api_key=""
)

config.set_default_model(gptmini)

def reverse_str(a:str)->str:
    """
    This function reverse a string in parameter.
    """
    return emulate()

print(reverse_str("Hello World!"))