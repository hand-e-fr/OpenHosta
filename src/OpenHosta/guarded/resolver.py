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
import collections.abc

from enum import Enum
from typing import Any, Type, List, Dict, Tuple, Set, Union, Callable, Literal, get_origin, get_args

try:
    from typing import is_typeddict
except ImportError:
    def is_typeddict(t): return False

from dataclasses import is_dataclass

# Imports des primitives OpenHosta
from .primitives import GuardedPrimitive, Guarded

from .subclassablescalars import (
    GuardedInt, GuardedUtf8, GuardedFloat,
    GuardedComplex, GuardedBytes, GuardedByteArray
)

from .subclassablewithproxy import (
    GuardedAny, GuardedBool, GuardedNone, GuardedMemoryView, GuardedRange
)

from .subclassablecollections import GuardedDict, GuardedSet, GuardedList, GuardedTuple, guarded_dataclass, guarded_typeddict

from .subclassablecallables import GuardedCode

try:
    from pydantic import BaseModel
    HAS_PYDANTIC = True
except ImportError:
    class BaseModel: pass
    HAS_PYDANTIC = False


def type_returned_data(response: Any, expected_type: type|None) -> Any:
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
    if expected_type == None:
        return None
    
    # Résoudre le type en GuardedType
    guarded_type = TypeResolver.resolve(expected_type)
    
    # Utiliser le constructeur Guarded pour convertir
    res = guarded_type.attempt(response)
    if res.success:
        # Prefer guarded data if available, pull_type_data_section will unwrap if needed
        return res.guarded_data if res.guarded_data is not None else res.data
    
    error_msg = f"Impossible de convertir la réponse du LLM vers le type {expected_type}.\n\n"
    error_msg += f"=== Réponse du LLM ===\n{response}\n======================\n\n"
    error_msg += f"=== Détail de l'erreur ===\n"
    
    if res.error_message and "→" in res.error_message:
        error_msg += res.error_message
    else:
        error_msg += f"Type global invalide ou non parsable.\nRaison: {res.error_message}"

    raise ValueError(error_msg)
    

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
        collections.abc.Callable: GuardedCode, # Support modern style (3.9+)
        types.FunctionType: GuardedCode,
        types.MethodType: GuardedCode,
        types.NoneType: GuardedNone,
        Any: GuardedAny,
        typing.Any: GuardedAny,
    }

    _RESOLVE_CACHE: Dict[Any, Type[GuardedPrimitive]] = {}

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
        if annotation in cls._RESOLVE_CACHE:
            return cls._RESOLVE_CACHE[annotation]
        
        result = cls._do_resolve(annotation)
        cls._RESOLVE_CACHE[annotation] = result
        return result

    @classmethod
    def _do_resolve(cls, annotation: Any) -> Type[GuardedPrimitive]:
        # 0. Safety net: Stringified annotations (from __future__ import annotations)
        # NOTE: This should rarely trigger now that analizer.py resolves strings via _resolve_annotation.
        # TODO(Phase 3): Remove this once all get_type_hints call sites are centralized.
        if isinstance(annotation, str):
            import warnings
            warnings.warn(
                f"[OpenHosta] TypeResolver received a string annotation '{annotation}'. "
                f"This indicates a gap in upstream type resolution.",
                stacklevel=2
            )
            # Simple heuristic for common types when they appear as strings
            str_map = {
                "int": int, "str": str, "bool": bool, "float": float, "complex": complex,
                "list": list, "List": List, "dict": dict, "Dict": Dict,
                "set": set, "Set": Set, "tuple": tuple, "Tuple": Tuple,
                "Callable": Callable, "Any": Any, "None": None, "NoneType": type(None),
                "bytes": bytes, "bytearray": bytearray
            }
            if annotation in str_map:
                annotation = str_map[annotation]
            elif "[" in annotation:
                # Handle subscripted types as strings: "List[int]", "Callable[...]"
                base_type = annotation.split("[")[0].split(".")[-1]
                if base_type in str_map:
                    annotation = str_map[base_type]
            elif "." in annotation:
                # Handle qualified names: "typing.List", "collections.abc.Callable"
                base_type = annotation.split(".")[-1]
                if base_type in str_map:
                    annotation = str_map[base_type]

        # 1. Cas : Types primitifs natifs (int, str, bool...)
        if annotation in cls._PRIMITIVE_MAP:
            return cls._PRIMITIVE_MAP[annotation]

        # C'est déjà une classe Guarded (ou une sous-classe)
        # Ex: L'utilisateur passe directement GuardedInt ou CorporateEmail
        if isinstance(annotation, type) and issubclass(annotation, GuardedPrimitive):
            return annotation
            
        # None literal (common alias for NoneType in annotations)
        if annotation is None:
            return GuardedNone

        # Python 3.12 TypeAliasType
        if hasattr(annotation, "__name__") and type(annotation).__name__ == "TypeAliasType":
            return cls.resolve(annotation.__value__)

        # Enums Python
        if isinstance(annotation, type) and issubclass(annotation, Enum):
            # Import GuardedEnum pour wrapper les enums standards
            from .subclassableclasses import GuardedEnum, guarded_enum
            
            # Si c'est déjà un GuardedEnum, retourner tel quel
            if issubclass(annotation, GuardedEnum):
                return annotation
            
            # Créer dynamiquement un GuardedEnum wrapper
            return guarded_enum(annotation)

        # TypedDict
        if is_typeddict(annotation):
            return guarded_typeddict(annotation)


        if isinstance(annotation, type) and issubclass(annotation, tuple) and annotation is not tuple:
             return GuardedTuple

        # Dataclasses (On les convertit en GuardedDataclassWrapper à la volée)
        if (isinstance(annotation, type) and is_dataclass(annotation)):
            from .subclassablecollections import guarded_dataclass
            return guarded_dataclass(annotation)

        # Pydantic Models
        if (isinstance(annotation, type) and HAS_PYDANTIC and issubclass(annotation, BaseModel) ):
            from .subclassablepydantic import guarded_pydantic_model
            return guarded_pydantic_model(annotation)

        # Types Génériques (Typing)
        origin = get_origin(annotation)
        args = get_args(annotation)

        if origin is Guarded:
            return cls.resolve(args[0])

        if origin is not None:
            # Callable origin check (handles subscripted Callable[[...], ...])
            if origin in (Callable, typing.Callable, collections.abc.Callable):
                from .subclassablecallables import guarded_callable, GuardedCode
                from .type_hints import extract_callable_args
                
                extracted_args = extract_callable_args(annotation)
                if not extracted_args:
                    return GuardedCode
                    
                resolved_args = [cls.resolve(a) for a in extracted_args]
                return guarded_callable(*resolved_args)

            # List, Iterable, Sequence -> GuardedList
            if origin in (list, List, typing.Sequence, typing.Iterable, collections.abc.Sequence, collections.abc.Iterable):
                inner = cls.resolve(args[0]) if args else GuardedUtf8
                return GuardedList[inner]

            # Set, Frozenset -> GuardedSet
            if origin in (set, frozenset, typing.Set, typing.AbstractSet, collections.abc.Set):
                inner = cls.resolve(args[0]) if args else GuardedUtf8
                return GuardedSet[inner]

            # Tuple -> GuardedTuple
            if origin in (tuple, typing.Tuple):
                from .subclassablecollections import guarded_tuple
                if args:
                    # Support for fixed-length tuples: Tuple[int, str]
                    # We Filter out Ellipsis (...) for now as it indicates variable length
                    if Ellipsis in args:
                        return GuardedTuple
                    
                    # Resolve each item type
                    resolved_args = tuple(cls.resolve(arg) for arg in args)
                    return guarded_tuple(*resolved_args)
                return GuardedTuple

            # Dict, Mapping -> GuardedDict
            if origin in (dict, Dict, typing.Mapping, typing.MutableMapping, collections.abc.Mapping, collections.abc.MutableMapping):
                k = cls.resolve(args[0]) if len(args) > 0 else GuardedUtf8
                v = cls.resolve(args[1]) if len(args) > 1 else GuardedUtf8
                return GuardedDict[k, v]

            # Literal -> GuardedLiteral
            if origin is typing.Literal:
                from .subclassableliterals import guarded_literal
                
                # Créer un GuardedLiteral avec les valeurs spécifiées
                if args:
                    return guarded_literal(*args)
                
                # Pas de valeurs spécifiées, fallback
                return GuardedUtf8

            # Union / Optional
            if origin is Union or (hasattr(typing, '_UnionGenericAlias') and isinstance(annotation, typing._UnionGenericAlias)) or (hasattr(types, "UnionType") and origin is types.UnionType):
                # Support Union complexe (Union[int, str, None])
                from .subclassableunions import guarded_union
                
                # On ne filtre PAS NoneType, on le mappe vers GuardedNone
                resolved_args = []
                for a in args:
                    if a is type(None):
                        resolved_args.append(GuardedNone)
                    else:
                        resolved_args.append(cls.resolve(a))
                
                # S'assurer que GuardedNone est testé en premier pour éviter que GuardedStr intercepte "None"
                resolved_args.sort(key=lambda t: 0 if getattr(t, "__name__", "") == "GuardedNone" else 1)
                
                # Optimisation: Si Optional[T] (Union[T, None]), on utilise GuardedUnion
                return guarded_union(*resolved_args)

            # Annotated (souvent utilisé avec Pydantic)
            if origin is typing.Annotated:
                return cls.resolve(args[0])

        # 6. Fallback
        raise TypeError(f"Type {annotation} (origin: {origin}) is not supported by OpenHosta TypeResolver. "
                        f"Consider using a supported primitive or wrapping your custom type.")