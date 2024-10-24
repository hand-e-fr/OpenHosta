HOSTAPATH = "./"
PROMPTPATH = "src/prompt.json"
CACHE_PATH = "./__hostacache__"

from .core.config import Model, DefaultManager

DefaultManager.set_default_model(
    Model(model="gpt-4o", base_url="https://api.openai.com/v1/chat/completions")
)

from .core import config
from .exec.emulate import emulate
from .exec.example import example
from .exec.thinkof import thinkof
from .utils.prompt import PromptManager

all = (
    "config",
    "emulate",
    "example",
    "thinkof",
    "PromptManager",
    "predict",
)