HOSTAPATH = "./"
PROMPTPATH = "src/prompt.json"

from .config import Model, DefaultManager

DefaultManager.set_default_model(
    Model(model="gpt-4o", base_url="https://api.openai.com/v1/chat/completions")
)
