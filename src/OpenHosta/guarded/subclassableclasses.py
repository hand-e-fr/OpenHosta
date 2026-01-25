
# ==============================================================================
# ENUM, DATACLASS, CLASS, INTERFACE 
# ==============================================================================

from typing import Any, Tuple, Type

from enum import Enum

# Assurez-vous d'avoir importé GuardedPrimitive
from .primitives import GuardedPrimitive, UncertaintyLevel, Tolerance, SubclassableWithProxy

class GuardedEnum(GuardedPrimitive, SubclassableWithProxy):
    # TODO: How to implement this ? maybe with de decorator @guarded_enum
    pass
