from .primitives import GuardedPrimitive, UncertaintyLevel, Tolerance, SubclassImpossible

class GuardedList(GuardedPrimitive, list):
    # TODO: implement using scalars.py as example
    pass

class GuardedSet(GuardedPrimitive, set):
    # TODO: implement using scalars.py as example
    pass

class GuardedDict(GuardedPrimitive, dict):
    # TODO: implement using scalars.py as example
    pass

class GuardedTuple(GuardedPrimitive, tuple):
    # TODO: implement using scalars.py as example
    pass

def guarded_dataclass(cls):
    # TODO: implement using scalars.py as example
    pass

