import types
import typing

from enum import Enum
from typing import Any, Type, List, Dict, Union, Callable, get_origin, get_args
from dataclasses import is_dataclass

# Imports des primitives OpenHosta
from .primitives import GuardedPrimitive

from .scalars import (
    GuardedInt, GuardedUtf8, GuardedBool, GuardedFloat,
    GuardedComplex, GuardedBytes, GuardedByteArray, 
    GuardedMemoryView, GuardedRange,    
    create_semantic_enum
)

from .collections import GuardedDict, GuardedSet, GuardedList, GuardedTuple

from .code import GuardedCode

# Note: GuardedModel is imported locally in resolve() to avoid circular import
try:
    from pydantic import BaseModel
    HAS_PYDANTIC = True
except ImportError:
    class BaseModel: pass
    HAS_PYDANTIC = False

class TypeResolver:
    """
    Service de résolution de types.
    Transforme les annotations Python standards (int, List[str], typing.Dict...)
    en classes Guarded exécutables.
    """

    # Mapping statique des types primitifs Python
    _PRIMITIVE_MAP = {
        int: GuardedInt,
        str: GuardedUtf8,
        bool: GuardedBool,
        float: GuardedFloat,
        complex: GuardedComplex,
        tuple: GuardedTuple,
        list: GuardedList,
        set: GuardedSet,
        frozenset: GuardedSet, # On mappe frozenset sur GuardedSet pour l'extraction
        dict: GuardedDict,
        bytes: GuardedBytes,
        bytearray: GuardedByteArray,
        memoryview: GuardedMemoryView,
        range: GuardedRange,
        Callable: GuardedCode,
        typing.Callable: GuardedCode,
        types.FunctionType: GuardedCode,        
    }

    @classmethod
    def resolve(cls, annotation: Any) -> Type[GuardedPrimitive]:
        """
        Convertit récursivement une annotation en GuardedType.
        
        Exemples:
        - int -> GuardedInt
        - List[int] -> GuardedList[GuardedInt]
        - Dict[str, float] -> GuardedDict[GuardedUtf8, GuardedFloat]
        - GuardedInt -> GuardedInt (Idempotence)
        """
        
        # 1. Cas : C'est déjà une classe Guarded (ou une sous-classe)
        # Ex: L'utilisateur passe directement GuardedInt ou CorporateEmail
        if isinstance(annotation, type) and issubclass(annotation, GuardedPrimitive):
            return annotation

        # 2. Cas : Types primitifs natifs (int, str, bool...)
        if annotation in cls._PRIMITIVE_MAP:
            return cls._PRIMITIVE_MAP[annotation]

        # 3. Enums Python
        if isinstance(annotation, type) and issubclass(annotation, Enum):
            return create_semantic_enum(annotation)

        # # 4. Pydantic Models & Dataclasses (On les convertit en GuardedModel à la volée)
        # if (isinstance(annotation, type) and 
        #    ((HAS_PYDANTIC and issubclass(annotation, BaseModel)) or is_dataclass(annotation))):
        #     # Import local pour éviter le cycle avec models.py
        #     from ..semantics.models import GuardedModel
        #     # Création dynamique d'un GuardedModel qui hérite du modèle original
        #     # Cela permet de préserver les validateurs Pydantic existants
        #     class WrappedModel(GuardedModel, annotation):
        #         pass
        #     WrappedModel.__name__ = f"Guarded_{annotation.__name__}"
        #     WrappedModel.__doc__ = annotation.__doc__
        #     return WrappedModel

        # # 5. Types Génériques (Typing)
        # origin = get_origin(annotation)
        # args = get_args(annotation)

        # if origin is not None:
        #     # List, Iterable, Sequence -> GuardedList
        #     if origin in (list, List, typing.Sequence, typing.Iterable):
        #         inner = cls.resolve(args[0]) if args else GuardedUtf8
        #         return GuardedList[inner]

        #     # Set, Frozenset -> GuardedSet
        #     if origin in (set, frozenset, typing.Set, typing.AbstractSet):
        #         inner = cls.resolve(args[0]) if args else GuardedUtf8
        #         return create_semantic_set(inner)

        #     # Tuple -> GuardedTuple
        #     if origin in (tuple, typing.Tuple):
        #         if not args:
        #             return GuardedTuple
        #         # Tuple[int, ...] (Variable)
        #         if len(args) == 2 and args[1] is Ellipsis:
        #             return create_semantic_tuple([cls.resolve(args[0])], variable_length=True)
        #         # Tuple[int, str] (Fixe)
        #         else:
        #             return create_semantic_tuple([cls.resolve(arg) for arg in args], variable_length=False)

        #     # Dict, Mapping -> GuardedDict
        #     if origin in (dict, Dict, typing.Mapping, typing.MutableMapping):
        #         k = cls.resolve(args[0]) if len(args) > 0 else GuardedUtf8
        #         v = cls.resolve(args[1]) if len(args) > 1 else GuardedUtf8
        #         return GuardedDict[k, v]

        #     # Literal -> GuardedLiteral
        #     if origin is typing.Literal:
        #         return create_semantic_literal(args)

        #     # Union / Optional
        #     if origin is Union:
        #         # On filtre NoneType
        #         non_none = [a for a in args if a is not type(None)]
        #         if len(non_none) == 1:
        #             return cls.resolve(non_none[0])
        #         # TODO: Support Union complexe (Union[int, str]) ?
        #         # Pour l'instant on fallback sur le premier ou str
        #         return cls.resolve(non_none[0]) if non_none else GuardedUtf8

        #     # Annotated (souvent utilisé avec Pydantic)
        #     if origin is typing.Annotated:
        #         return cls.resolve(args[0])

        # 6. Fallback
        return GuardedUtf8
    
    
    
def type_returned_data(untyped_response: str, expected_type: type) -> Any:
    """
    Convert the untyped response to the expected type.
    """
    
    semantic_type = TypeResolver.resolve(expected_type)
    convertion_report = semantic_type.attempt(untyped_response)
    return convertion_report.unwrap()
    
def describe_type_as_python(arg_type):

    semantic_type = TypeResolver.resolve(arg_type)
    return semantic_type._type_py
