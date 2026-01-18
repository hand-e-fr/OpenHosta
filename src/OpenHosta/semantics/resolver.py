import types
import typing

from enum import Enum
from typing import Any, Type, List, Dict, Union, Callable, get_origin, get_args
from dataclasses import is_dataclass

# Imports des primitives OpenHosta
from .primitives import GuardedPrimitive

from .scalars import (
    SemanticInt, SemanticStr, SemanticBool, SemanticFloat,
    SemanticComplex, SemanticBytes, SemanticByteArray, 
    SemanticMemoryView, SemanticRange,    
    create_semantic_enum, create_semantic_literal
)

from .code import SemanticCode

from .collections import (
    SemanticList, SemanticDict, SemanticSet, SemanticTuple,
    create_semantic_set, create_semantic_tuple
)

# Note: SemanticModel is imported locally in resolve() to avoid circular import
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
    en classes Semantic exécutables.
    """

    # Mapping statique des types primitifs Python
    _PRIMITIVE_MAP = {
        int: SemanticInt,
        str: SemanticStr,
        bool: SemanticBool,
        float: SemanticFloat,
        complex: SemanticComplex,
        tuple: SemanticTuple,
        list: SemanticList,
        set: SemanticSet,
        frozenset: SemanticSet, # On mappe frozenset sur SemanticSet pour l'extraction
        dict: SemanticDict,
        bytes: SemanticBytes,
        bytearray: SemanticByteArray,
        memoryview: SemanticMemoryView,
        range: SemanticRange,
        Callable: SemanticCode,
        typing.Callable: SemanticCode,
        types.FunctionType: SemanticCode,        
    }

    @classmethod
    def resolve(cls, annotation: Any) -> Type[GuardedPrimitive]:
        """
        Convertit récursivement une annotation en SemanticType.
        
        Exemples:
        - int -> SemanticInt
        - List[int] -> SemanticList[SemanticInt]
        - Dict[str, float] -> SemanticDict[SemanticStr, SemanticFloat]
        - SemanticInt -> SemanticInt (Idempotence)
        """
        
        # 1. Cas : C'est déjà une classe Semantic (ou une sous-classe)
        # Ex: L'utilisateur passe directement SemanticInt ou CorporateEmail
        if isinstance(annotation, type) and issubclass(annotation, GuardedPrimitive):
            return annotation

        # 2. Cas : Types primitifs natifs (int, str, bool...)
        if annotation in cls._PRIMITIVE_MAP:
            return cls._PRIMITIVE_MAP[annotation]

        # 3. Enums Python
        if isinstance(annotation, type) and issubclass(annotation, Enum):
            return create_semantic_enum(annotation)

        # 4. Pydantic Models & Dataclasses (On les convertit en SemanticModel à la volée)
        if (isinstance(annotation, type) and 
           ((HAS_PYDANTIC and issubclass(annotation, BaseModel)) or is_dataclass(annotation))):
            # Import local pour éviter le cycle avec models.py
            from .models import SemanticModel
            # Création dynamique d'un SemanticModel qui hérite du modèle original
            # Cela permet de préserver les validateurs Pydantic existants
            class WrappedModel(SemanticModel, annotation):
                pass
            WrappedModel.__name__ = f"Semantic_{annotation.__name__}"
            WrappedModel.__doc__ = annotation.__doc__
            return WrappedModel

        # 5. Types Génériques (Typing)
        origin = get_origin(annotation)
        args = get_args(annotation)

        if origin is not None:
            # List, Iterable, Sequence -> SemanticList
            if origin in (list, List, typing.Sequence, typing.Iterable):
                inner = cls.resolve(args[0]) if args else SemanticStr
                return SemanticList[inner]

            # Set, Frozenset -> SemanticSet
            if origin in (set, frozenset, typing.Set, typing.AbstractSet):
                inner = cls.resolve(args[0]) if args else SemanticStr
                return create_semantic_set(inner)

            # Tuple -> SemanticTuple
            if origin in (tuple, typing.Tuple):
                if not args:
                    return SemanticTuple
                # Tuple[int, ...] (Variable)
                if len(args) == 2 and args[1] is Ellipsis:
                    return create_semantic_tuple([cls.resolve(args[0])], variable_length=True)
                # Tuple[int, str] (Fixe)
                else:
                    return create_semantic_tuple([cls.resolve(arg) for arg in args], variable_length=False)

            # Dict, Mapping -> SemanticDict
            if origin in (dict, Dict, typing.Mapping, typing.MutableMapping):
                k = cls.resolve(args[0]) if len(args) > 0 else SemanticStr
                v = cls.resolve(args[1]) if len(args) > 1 else SemanticStr
                return SemanticDict[k, v]

            # Literal -> SemanticLiteral
            if origin is typing.Literal:
                return create_semantic_literal(args)

            # Union / Optional
            if origin is Union:
                # On filtre NoneType
                non_none = [a for a in args if a is not type(None)]
                if len(non_none) == 1:
                    return cls.resolve(non_none[0])
                # TODO: Support Union complexe (Union[int, str]) ?
                # Pour l'instant on fallback sur le premier ou str
                return cls.resolve(non_none[0]) if non_none else SemanticStr

            # Annotated (souvent utilisé avec Pydantic)
            if origin is typing.Annotated:
                return cls.resolve(args[0])

        # 6. Fallback
        return SemanticStr