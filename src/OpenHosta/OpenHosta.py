from emulate import _exec_emulate, thought
import config
from config import Model
from exec import HostaInjector

# TODO make the if else for data cache here !
emulate = HostaInjector(_exec_emulate)

__all__ = "emulate", "thought", "config", "Model"