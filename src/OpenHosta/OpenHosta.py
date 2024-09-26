from .config import Model, DefaultManager

DefaultManager.set_default_model(
    Model(model="gpt-4o", base_url="https://api.openai.com/v1/chat/completions")
)


from .emulate import _exec_emulate
from .predict import _exec_predict
from . import config
from .thought import thought
from .exec import HostaInjector
from .example import example, load_examples, save_examples

emulate = HostaInjector(_exec_emulate)
predict = HostaInjector(_exec_predict)

__all__ = (
    "emulate",
    "thought",
    "example", 
    "load_examples", 
    "save_examples",
    "config", 
    "Model", 
    "DefaultManager",
    "predict"
)

