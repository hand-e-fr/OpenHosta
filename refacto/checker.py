from __future__ import annotations

from .inspector import HostaInspector

class HostaChecker(HostaInspector):
    """
    Post processing in the execution chain. 
    Detect errors in the output to reduce uncertainty.
    Manage all the typing process
    """
    def __init__(self):
        """ Initialize the HostaInjector instance """
        super().__init__()

    def _type(self):
        """ Checks output typing """
        pass