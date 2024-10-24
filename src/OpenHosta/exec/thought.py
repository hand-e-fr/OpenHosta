from __future__ import annotations

from ..core.hosta import Hosta, CotType

def thought(task:str)->None:
    x =  Hosta()
    x._bdy_add('cot', CotType(task=task))