from config import Model, DefaultManager

DefaultManager.set_default_model(Model(
    model="gpt-4o",
    base_url="https://api.openai.com/v1/chat/completions"
))

from emulate import _exec_emulate
import config
from thought import thought

from exec import HostaInjector

# TODO make the if else for data cache here !
emulate = HostaInjector(_exec_emulate)

__all__ = "emulate", "thought", "config", "Model", "DefaultManager"