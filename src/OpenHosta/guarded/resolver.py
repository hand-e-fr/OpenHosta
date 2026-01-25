r"""
| **Catégorie**     | **Style Ancien (Toujours valide)** | **Style Moderne (3.9+)**               | **Module requis**        |
|-------------------|------------------------------------|----------------------------------------|--------------------------|
| **Collections**   | `typing.List[int]`                | `list[int]`                            | Aucun (natif)            |
| **Dictionnaires** | `typing.Dict[str, int]`           | `dict[str, int]`                       | Aucun (natif)            |
| **Valeurs fixes** | `typing.Literal[1, 2]`            | **(Pas d'équivalent)**                 | `typing`                 |
| **Optionnel**     | `typing.Optional[int]`            | `int | None` (Python 3.10+)           | Aucun                    |
| **Union**         | `typing.Union[int, str]`          | `int | str` (Python 3.10+)            | Aucun                    |
| **Callables**     | `typing.Callable`                 | `collections.abc.Callable`             | `collections.abc`        |
"""

import types
import typing

from enum import Enum
from typing import Any, Type, List, Dict, Tuple, Set, Union, Callable, Literal, get_origin, get_args
from dataclasses import is_dataclass

# Imports des primitives OpenHosta
from .primitives import GuardedPrimitive

from .subclassablescalars import (
    GuardedInt, GuardedUtf8, GuardedFloat,
    GuardedComplex, GuardedBytes, GuardedByteArray
)

from .subclassablewithproxy import (
    GuardedAny, GuardedBool, GuardedNone, GuardedMemoryView, GuardedRange
)

from .subclassablecollections import GuardedDict, GuardedSet, GuardedList, GuardedTuple, guarded_dataclass

from .subclassablecallables import GuardedCode

# Note: GuardedModel is imported locally in resolve() to avoid circular import
try:
    from pydantic import BaseModel
    HAS_PYDANTIC = True
except ImportError:
    class BaseModel: pass
    HAS_PYDANTIC = False


def type_returned_data(response: Any, expected_type: Type) -> Any:
    """
    Convertit une réponse (généralement une string) vers le type attendu.
    
    Cette fonction est utilisée par le pipeline pour typer les données retournées
    par le LLM selon le type annoté de la fonction.
    
    Args:
        response: La réponse brute (généralement une string)
        expected_type: Le type Python attendu
    
    Returns:
        La valeur convertie au bon type
    
    Raises:
        ValueError: Si la conversion échoue
    """
    # Si pas de type spécifié, retourner tel quel
    if expected_type is None:
        return response
    
    # Résoudre le type en GuardedType
    guarded_type = TypeResolver.resolve(expected_type)
    
    # Utiliser le constructeur Guarded pour convertir
    try:
        return guarded_type(response)
    except Exception as e:
        # Fallback: essayer de convertir directement
        if isinstance(expected_type, type):
            try:
                return expected_type(response)
            except:
                pass
        raise ValueError(f"Cannot convert '{response}' to type {expected_type}: {e}")


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
        Tuple: GuardedTuple,
        list: GuardedList,
        List: GuardedList,
        set: GuardedSet,
        Set: GuardedSet,
        frozenset: GuardedSet, # On mappe frozenset sur GuardedSet pour l'extraction
        dict: GuardedDict,
        bytes: GuardedBytes,
        bytearray: GuardedByteArray,
        memoryview: GuardedMemoryView,
        range: GuardedRange,
        Callable: GuardedCode,
        typing.Callable: GuardedCode,
        types.FunctionType: GuardedCode,
        types.MethodType: GuardedCode,
        types.NoneType: GuardedNone,        
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
        
        # 1. Cas : Types primitifs natifs (int, str, bool...)
        if annotation in cls._PRIMITIVE_MAP:
            return cls._PRIMITIVE_MAP[annotation]

        # 1. Cas : C'est déjà une classe Guarded (ou une sous-classe)
        # Ex: L'utilisateur passe directement GuardedInt ou CorporateEmail
        if isinstance(annotation, type) and issubclass(annotation, GuardedPrimitive):
            return annotation

        # 3. Enums Python
        if isinstance(annotation, type) and issubclass(annotation, Enum):
            # TODO: Implémenter guarded_enum factory
            # Pour l'instant, on retourne GuardedUtf8
            return GuardedUtf8

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

        # 5. Types Génériques (Typing)
        origin = get_origin(annotation)
        args = get_args(annotation)

        if origin is not None:
            # List, Iterable, Sequence -> GuardedList
            if origin in (list, List, typing.Sequence, typing.Iterable):
                inner = cls.resolve(args[0]) if args else GuardedUtf8
                return GuardedList[inner]

            # Set, Frozenset -> GuardedSet
            if origin in (set, frozenset, typing.Set, typing.AbstractSet):
                inner = cls.resolve(args[0]) if args else GuardedUtf8
                return GuardedSet[inner]

            # Tuple -> GuardedTuple
            if origin in (tuple, typing.Tuple):
                # Pour l'instant, on retourne GuardedTuple simple
                # TODO: Support des tuples typés (Tuple[int, str])
                return GuardedTuple

            # Dict, Mapping -> GuardedDict
            if origin in (dict, Dict, typing.Mapping, typing.MutableMapping):
                k = cls.resolve(args[0]) if len(args) > 0 else GuardedUtf8
                v = cls.resolve(args[1]) if len(args) > 1 else GuardedUtf8
                return GuardedDict[k, v]

            # Literal -> GuardedLiteral
            if origin is typing.Literal:
                # TODO: Implémenter guarded_literal
                # Pour l'instant, on retourne GuardedUtf8
                return GuardedUtf8

            # Union / Optional
            if origin is Union:
                # On filtre NoneType
                non_none = [a for a in args if a is not type(None)]
                if len(non_none) == 1:
                    return cls.resolve(non_none[0])
                # TODO: Support Union complexe (Union[int, str]) ?
                # Pour l'instant on fallback sur le premier ou str
                return cls.resolve(non_none[0]) if non_none else GuardedUtf8

            # Annotated (souvent utilisé avec Pydantic)
            if origin is typing.Annotated:
                return cls.resolve(args[0])

        # 6. Fallback
        return GuardedUtf8
    