"""OpenHosta Guarded Types - Types with tolerance and metadata."""

from .api import guard, unguard
from .constants import Tolerance
from .primitives import GuardConfig, GuardedPrimitive, ProxyWrapper, UncertaintyLevel
from .resolver import TypeResolver, type_returned_data
from .subclassablecallables import GuardedCode as GuardedCallable
from .subclassableclasses import GuardedEnum
from .subclassablecollections import GuardedDict, GuardedList, GuardedSet, GuardedTuple, guarded_dataclass
from .subclassableliterals import GuardedLiteral, guarded_literal
from .subclassablescalars import GuardedByteArray, GuardedBytes, GuardedComplex, GuardedFloat, GuardedInt, GuardedUtf8
from .subclassableunions import GuardedUnion, guarded_union
from .subclassablewithproxy import GuardedAny, GuardedBool, GuardedMemoryView, GuardedNone, GuardedRange

__all__ = [
    # Constants
    'Tolerance',

    # Base classes
    'GuardedPrimitive',
    'ProxyWrapper',
    'UncertaintyLevel',
    'GuardConfig',

    # Scalars
    'GuardedInt',
    'GuardedFloat',
    'GuardedUtf8',
    'GuardedComplex',
    'GuardedBytes',
    'GuardedByteArray',

    # Proxy types
    'GuardedBool',
    'GuardedNone',
    'GuardedAny',
    'GuardedMemoryView',
    'GuardedRange',

    # Collections
    'GuardedList',
    'GuardedDict',
    'GuardedSet',
    'GuardedTuple',

    # Classes
    'GuardedEnum',
    'GuardedLiteral',
    'GuardedUnion',
    'GuardedCallable',
    'guarded_dataclass',
    'guarded_literal',
    'guarded_union',

    # Resolver
    'TypeResolver',
    'type_returned_data',

    # Public API
    'guard',
    'unguard',
]
