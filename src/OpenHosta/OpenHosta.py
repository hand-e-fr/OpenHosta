from emulate import _exec_emulate, thought
import config
from exec import HostaInjector


emulate = HostaInjector(_exec_emulate)

__all__ = emulate, thought, config