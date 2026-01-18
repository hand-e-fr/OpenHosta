import json

from typing import Any, Tuple, Type, Dict, List, Union
from .primitives import GuardedPrimitive
from .scalars import SemanticStr # Type par défaut

# ==============================================================================
# 1. SEMANTIC LIST (La Liste Intelligente)
# ==============================================================================

def create_semantic_list(inner_type: Type[GuardedPrimitive]) -> Type['SemanticList']:
    """
    Factory qui génère une classe de Liste typée sémantiquement.
    Ex: create_semantic_list(SemanticInt) -> Classe qui valide [1, 2, 3]
    """

    class ConcreteSemanticList(SemanticList):
        _inner_semantic_type = inner_type
        
        # --- Configuration Dynamique ---
        # Le LLM reçoit une description récursive : "une liste de [description de l'entier]"
        _type_en = f"a list of {inner_type._type_en}s"
        _type_py = f"List[{inner_type._type_py}]"
        
        # Schema JSON pour forcer la structure ARRAY
        _type_json = {
            "type": "array",
            "items": inner_type._type_json
        }

        @classmethod
        def _parse_native(cls, value: Any) -> Tuple[bool, Any]:
            # Pour être valide nativement, ça doit être un itérable (list, tuple)
            if not isinstance(value, (list, tuple)):
                return False, None
            
            validated_items = []
            for item in value:
                # Validation récursive : on demande au type interne de vérifier l'item
                # Note: On utilise _parse_native du type enfant pour éviter de re-déclencher le LLM
                # sur chaque item si la liste est déjà partiellement propre.
                is_valid, val = inner_type._parse_native(item)
                
                if not is_valid:
                    # Si un seul item est invalide, la liste entière est rejetée "nativement"
                    # Cela forcera le pipeline à passer en mode Heuristique ou LLM global
                    return False, None
                
                validated_items.append(val)
                
            return True, validated_items

        def __init__(self, value: Any, description: str = ""):
            # value est ici la liste brute validée (ex: [1, 2, 3])
            # On transforme chaque élément en Instance Sémantique (ex: SemanticInt(1))
            # pour qu'il porte ses propres métadonnées.
            semantic_items = [self._inner_semantic_type(item) for item in value]
            super().__init__(semantic_items)
            self._description = description

    # Nommage pour le debug (ex: SemanticList_SemanticInt)
    ConcreteSemanticList.__name__ = f"SemanticList_{inner_type.__name__}"
    return ConcreteSemanticList


class SemanticList(list, GuardedPrimitive):
    """
    Classe de base pour les listes.
    Permet la syntaxe: MyList = SemanticList[SemanticInt]
    """
    
    # Par défaut (si utilisé sans crochets), c'est une liste de String
    _inner_semantic_type = SemanticStr
    
    _type_en = "a list of text items"
    _type_py = "List[str]"
    _type_json = {"type": "array", "items": {"type": "string"}}

    @classmethod
    def __class_getitem__(cls, item_type):
        """Intercepte SemanticList[Type]"""
        # Import local pour éviter cycle avec resolver.py
        from .resolver import TypeResolver
        
        resolved_type = TypeResolver.resolve(item_type)
        return create_semantic_list(resolved_type)

    @classmethod
    def _parse_native(cls, value: Any) -> Tuple[bool, Any]:
        # Implémentation par défaut (List[str])
        if isinstance(value, list):
            return True, [str(v) for v in value]
        return False, None

    @classmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[bool, Any]:
        """Tente de parser une string JSON '[...]'."""
        if isinstance(value, str):
            value = value.strip()
            if value.startswith("[") and value.endswith("]"):
                try:
                    data = json.loads(value)
                    if isinstance(data, list):
                        # On repasse par parse_native pour valider le contenu typé
                        return cls._parse_native(data)
                except json.JSONDecodeError:
                    pass
        return False, None


# ==============================================================================
# 2. SEMANTIC DICT (Le Dictionnaire Flou)
# ==============================================================================

def create_semantic_dict(key_type: Type[GuardedPrimitive], val_type: Type[GuardedPrimitive]) -> Type['SemanticDict']:
    
    class ConcreteSemanticDict(SemanticDict):
        _key_semantic_type = key_type
        _val_semantic_type = val_type
        
        _type_en = f"a dictionary where keys are {key_type._type_en} and values are {val_type._type_en}"
        _type_py = f"Dict[{key_type._type_py}, {val_type._type_py}]"
        
        _type_json = {
            "type": "object",
            "additionalProperties": val_type._type_json
        }

        @classmethod
        def _parse_native(cls, value: Any) -> Tuple[bool, Any]:
            if not isinstance(value, dict):
                return False, None
            
            validated_dict = {}
            for k, v in value.items():
                # Validation Clé
                k_ok, k_val = key_type._parse_native(k)
                if not k_ok: return False, None
                
                # Validation Valeur
                v_ok, v_val = val_type._parse_native(v)
                if not v_ok: return False, None
                
                validated_dict[k_val] = v_val
                
            return True, validated_dict

        def __init__(self, value: Any, description: str = ""):
            # Instanciation sémantique des clés et valeurs
            # Note: On stocke des objets sémantiques. 
            # Si key_type est SemanticType, attention au hashage !
            # SemanticDict gère ça via sa propre logique de lookup.
            super().__init__()
            for k, v in value.items():
                sem_k = self._key_semantic_type(k)
                sem_v = self._val_semantic_type(v)
                self[sem_k] = sem_v
            
            self._description = description

    ConcreteSemanticDict.__name__ = f"SemanticDict_{key_type.__name__}_{val_type.__name__}"
    return ConcreteSemanticDict


class SemanticDict(dict, GuardedPrimitive):
    """
    Dictionnaire sémantique.
    Syntaxe: SemanticDict[SemanticStr, SemanticInt]
    
    Feature Clé: Recherche sémantique.
    Si d["cle"] échoue, on cherche une clé k telle que k == "cle" (égalité sémantique).
    """
    
    _key_semantic_type = SemanticStr
    _val_semantic_type = SemanticStr
    
    _type_en = "a dictionary (key-value pairs)"
    _type_py = "Dict[str, str]"
    _type_json = {"type": "object"}

    @classmethod
    def __class_getitem__(cls, params):
        from .resolver import TypeResolver
        
        # Gestion SemanticDict[KeyType, ValType] vs SemanticDict[ValType] (implied Str key)
        if not isinstance(params, tuple):
            params = (SemanticStr, params)
            
        K, V = params
        return create_semantic_dict(TypeResolver.resolve(K), TypeResolver.resolve(V))

    @classmethod
    def _parse_native(cls, value: Any) -> Tuple[bool, Any]:
        if isinstance(value, dict):
            return True, value
        return False, None

    @classmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[bool, Any]:
        """Tente de parser du JSON '{...}'."""
        if isinstance(value, str):
            value = value.strip()
            if value.startswith("{") and value.endswith("}"):
                try:
                    data = json.loads(value)
                    if isinstance(data, dict):
                        return cls._parse_native(data)
                except json.JSONDecodeError:
                    pass
        return False, None

    def __getitem__(self, key):
        """
        Recherche intelligente (Semantic Lookup).
        1. Essaie le hash exact (O(1)).
        2. Si échec, itère sur les clés pour trouver une égalité sémantique (O(N)).
        """
        # 1. Tentative Standard (Rapide)
        try:
            return super().__getitem__(key)
        except (KeyError, TypeError):
            pass

        # 2. Tentative Sémantique (Lente mais puissante)
        # On ne le fait que si la clé passée est compatible (str ou SemanticType)
        found_key = None
        
        # On parcourt toutes les clés existantes
        for existing_key in self.keys():
            # L'opérateur == déclenche la logique hybride (Vecteurs ou LLM)
            # définie dans SemanticType.__eq__
            if existing_key == key:
                found_key = existing_key
                break
        
        if found_key is not None:
            return super().__getitem__(found_key)
            
        raise KeyError(f"Key '{key}' not found (even semantically).")
    
# ==============================================================================
# 3. SEMANTIC SET (L'Ensemble Unique)
# ==============================================================================

def create_semantic_set(inner_type: Type[GuardedPrimitive]) -> Type['SemanticSet']:
    class ConcreteSemanticSet(SemanticSet):
        _inner_semantic_type = inner_type
        _type_en = f"a set (unique items) of {inner_type._type_en}s"
        _type_py = f"Set[{inner_type._type_py}]"
        _type_json = {"type": "array", "items": inner_type._type_json, "uniqueItems": True}

        @classmethod
        def _parse_native(cls, value: Any) -> Tuple[bool, Any]:
            if not isinstance(value, (set, frozenset, list, tuple)):
                return False, None
            
            validated_set = set()
            for item in value:
                is_valid, val = inner_type._parse_native(item)
                if not is_valid: return False, None
                validated_set.add(val)
            return True, validated_set
            
        def __init__(self, value: Any, description: str = ""):
            # Conversion des items
            semantic_items = {self._inner_semantic_type(item) for item in value}
            super().__init__(semantic_items) # SemanticSet hérite de set
            self._description = description

    ConcreteSemanticSet.__name__ = f"SemanticSet_{inner_type.__name__}"
    return ConcreteSemanticSet

class SemanticSet(set, GuardedPrimitive):
    _inner_semantic_type = SemanticStr
    _type_en = "a set of unique items"
    _type_py = "Set[str]"
    _type_json = {"type": "array", "uniqueItems": True}

    @classmethod
    def __class_getitem__(cls, item_type):
        from .resolver import TypeResolver
        return create_semantic_set(TypeResolver.resolve(item_type))
    
    @classmethod
    def _parse_native(cls, value: Any) -> Tuple[bool, Any]:
        if isinstance(value, (set, frozenset)):
            return True, set(value)
        return False, None
        
    @classmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[bool, Any]:
        # Support de l'évaluation littérale des sets "{1, 2}"
        if isinstance(value, str) and value.strip().startswith("{"):
            try:
                import ast
                val = ast.literal_eval(value)
                if isinstance(val, (set, list, tuple)):
                    return cls._parse_native(val)
            except: pass
        return False, None


# ==============================================================================
# 4. SEMANTIC TUPLE (Le Tuple Structuré)
# ==============================================================================

def create_semantic_tuple(item_types: List[Type[GuardedPrimitive]], variable_length: bool = False) -> Type['SemanticTuple']:
    """
    Gère Tuple[int, str] (Fixed) ET Tuple[int, ...] (Variable)
    """
    
    class ConcreteSemanticTuple(SemanticTuple):
        _item_types = item_types
        _is_variable = variable_length
        
        # Construction de la documentation dynamique
        if variable_length:
            _type_en = f"a tuple of variable length containing {item_types[0]._type_en}s"
            _type_py = f"Tuple[{item_types[0]._type_py}, ...]"
            _type_json = {"type": "array", "items": item_types[0]._type_json}
        else:
            names = [t._type_py for t in item_types]
            _type_en = f"a fixed tuple of elements: {', '.join(names)}"
            _type_py = f"Tuple[{', '.join(names)}]"
            _type_json = {
                "type": "array", 
                "prefixItems": [t._type_json for t in item_types],
                "minItems": len(item_types),
                "maxItems": len(item_types)
            }

        @classmethod
        def _parse_native(cls, value: Any) -> Tuple[bool, Any]:
            if not isinstance(value, (list, tuple)): return False, None
            
            # Cas Tuple Variable: Tuple[int, ...]
            if cls._is_variable:
                target_type = cls._item_types[0]
                validated = []
                for item in value:
                    ok, val = target_type._parse_native(item)
                    if not ok: return False, None
                    validated.append(val)
                return True, tuple(validated)
            
            # Cas Tuple Fixe: Tuple[int, str]
            if len(value) != len(cls._item_types): return False, None
            
            validated = []
            for item, target_type in zip(value, cls._item_types):
                ok, val = target_type._parse_native(item)
                if not ok: return False, None
                validated.append(val)
            return True, tuple(validated)

        def __init__(self, value: Any, description: str = ""):
            final_list = []
            if self._is_variable:
                 # Variable logic
                 target_t = self._item_types[0]
                 final_list = [target_t(v) for v in value]
            else:
                # Fixed logic
                for v, target_t in zip(value, self._item_types):
                    final_list.append(target_t(v))
            
            super().__init__(tuple(final_list)) # Init du tuple natif
            self._description = description

    ConcreteSemanticTuple.__name__ = f"SemanticTuple_Fixed" if not variable_length else f"SemanticTuple_Var_{item_types[0].__name__}"
    return ConcreteSemanticTuple

class SemanticTuple(tuple, GuardedPrimitive):
    _type_en = "a tuple"
    _type_py = "tuple"
    _type_json = {"type": "array"}
    
    @classmethod
    def _parse_native(cls, v): return (True, tuple(v)) if isinstance(v, (list, tuple)) else (False, None)
    
    @classmethod
    def _parse_heuristic(cls, v):
         if isinstance(v, str) and v.startswith("("):
            try:
                import ast
                val = ast.literal_eval(v)
                if isinstance(val, tuple): return cls._parse_native(val)
            except: pass
         return False, None