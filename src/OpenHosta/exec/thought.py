from __future__ import annotations

from ..core.hosta_inspector import HostaInspector, CotType


def thought(task: str) -> None:
    x = HostaInspector()
    x._bdy_add('cot', CotType(task=task))
