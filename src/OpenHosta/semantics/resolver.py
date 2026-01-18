# src/OpenHosta/semantics/resolver.py
import typing
from typing import Any, Type, List, Dict, Union, Optional, get_origin, get_args

# Imports des primitives OpenHosta
from .primitives import GuardedPrimitive
from .scalars import SemanticInt, SemanticStr, SemanticBool, SemanticFloat
# On importe les collections (qui contiennent la logique __class_getitem__)
from .collections import SemanticList, SemanticDict

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
        list: SemanticList, # Liste générique (sans type interne)
        dict: SemanticDict, # Dict générique
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

        # 3. Cas : Types Génériques (via module typing ou builtins python 3.9+)
        origin = get_origin(annotation)
        args = get_args(annotation)

        if origin is not None:
            # --- GESTION DES LISTES (List[T], Iterable[T]...) ---
            if origin in (list, List, typing.Sequence, typing.Iterable):
                inner_type = args[0] if args else str
                resolved_inner = cls.resolve(inner_type)
                
                # On utilise la syntaxe [] qui déclenche la factory interne de SemanticList
                return SemanticList[resolved_inner]

            # --- GESTION DES DICTIONNAIRES (Dict[K, V], Mapping[K, V]...) ---
            if origin in (dict, Dict, typing.Mapping):
                key_type = args[0] if len(args) > 0 else str
                val_type = args[1] if len(args) > 1 else str
                
                resolved_key = cls.resolve(key_type)
                resolved_val = cls.resolve(val_type)
                
                # On déclenche la factory interne de SemanticDict
                return SemanticDict[resolved_key, resolved_val]

            # --- GESTION DES OPTIONALS / UNIONS (Optional[T], Union[T, None]) ---
            if origin is Union:
                # Simplification pour OpenHosta : On prend le premier type "non-None"
                # Car le SemanticType gère déjà l'incertitude et le None via le casting
                non_none_args = [arg for arg in args if arg is not type(None)]
                if non_none_args:
                    return cls.resolve(non_none_args[0])

        # 4. Fallback : Si on ne comprend pas, on suppose que c'est du texte
        # (Ou on pourrait lever une erreur selon la rigueur souhaitée)
        return SemanticStr