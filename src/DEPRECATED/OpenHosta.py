from .core.config import Model, DefaultManager

DefaultManager.set_default_model(
    Model(model="gpt-4o", base_url="https://api.openai.com/v1/chat/completions")
)

from .core.emulate import _exec_emulate
from .predict.predict import _exec_predict
from .predict.trainset import TrainingSet
from .core import config
from .body.thought import thought
from .core.exec import HostaInjector
from .body.example import example, save_examples, load_training_example
from .body.enhancer import suggest

emulate = HostaInjector(_exec_emulate)
predict = HostaInjector(_exec_predict)

__all__ = (
    "emulate",
    "thought",
    "example", 
    "save_examples",
    "load_training_example",
    "TrainingSet",
    "config", 
    "Model", 
    "DefaultManager",
    "suggest",
    "predict"
)

