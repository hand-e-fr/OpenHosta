from config import Model, DefaultManager
from emulate import _exec_emulate, thought
import config
from example import example
from exec import HostaInjector

DefaultManager.set_default_model(Model(
    model="gpt-4o",
    base_url="https://api.openai.com/v1/chat/completions"
))


# TODO make the if else for data cache here !
emulate = HostaInjector(_exec_emulate)

__all__ = "emulate", "thought", "example", "config", "Model", "DefaultManager"
