from config import Model, DefaultManager
import config
from emulate import _exec_emulate, thought
from example import example, load_examples, save_examples
from exec import HostaInjector

DefaultManager.set_default_model(Model(
    model="gpt-4o",
    base_url="https://api.openai.com/v1/chat/completions"
))

emulate = HostaInjector(_exec_emulate)

__all__ = "emulate", "thought",
"example", "load_examples", "save_examples",
"config", "Model", "DefaultManager"
