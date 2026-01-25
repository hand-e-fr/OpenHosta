from typing import Any, Tuple, Optional
from .primitives import GuardedPrimitive, UncertaintyLevel, Tolerance, ProxyWrapper

class GuardedList(GuardedPrimitive, list):
    """
    Liste sémantique.
    Accepte : [1, 2, 3], "[1, 2, 3]", "1,2,3", ou toute itérable.
    """
    _type_en = "a list of items"
    _type_py = list
    _type_json = {"type": "array"}
    
    @classmethod
    def _parse_native(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        if isinstance(value, list):
            return UncertaintyLevel(Tolerance.STRICT), value, None
        return UncertaintyLevel(Tolerance.ANYTHING), value, None
    
    @classmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        # Accepter les tuples, sets, et autres itérables
        if isinstance(value, (tuple, set, frozenset)):
            return UncertaintyLevel(Tolerance.PRECISE), list(value), None
        
        # Accepter les strings représentant des listes
        if isinstance(value, str):
            value = value.strip()
            
            # Format "[1, 2, 3]"
            if value.startswith('[') and value.endswith(']'):
                try:
                    import ast
                    parsed = ast.literal_eval(value)
                    if isinstance(parsed, list):
                        return UncertaintyLevel(Tolerance.FLEXIBLE), parsed, None
                except (ValueError, SyntaxError) as e:
                    pass
            
            # Format "1,2,3" (CSV)
            if ',' in value:
                items = [item.strip() for item in value.split(',')]
                return UncertaintyLevel(Tolerance.FLEXIBLE), items, None
        
        # Tenter de convertir en liste
        try:
            return UncertaintyLevel(Tolerance.TYPE_COMPLIANT), list(value), None
        except (TypeError, ValueError) as e:
            return UncertaintyLevel(Tolerance.ANYTHING), value, str(e)

class GuardedSet(GuardedPrimitive, set):
    """
    Ensemble sémantique.
    Accepte : {1, 2, 3}, "{1, 2, 3}", "1,2,3", ou toute itérable.
    """
    _type_en = "a set of unique items"
    _type_py = set
    _type_json = {"type": "array", "uniqueItems": True}
    
    @classmethod
    def _parse_native(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        if isinstance(value, (set, frozenset)):
            return UncertaintyLevel(Tolerance.STRICT), set(value), None
        return UncertaintyLevel(Tolerance.ANYTHING), value, None
    
    @classmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        # Accepter les listes et tuples
        if isinstance(value, (list, tuple)):
            return UncertaintyLevel(Tolerance.PRECISE), set(value), None
        
        # Accepter les strings représentant des sets
        if isinstance(value, str):
            value = value.strip()
            
            # Format "{1, 2, 3}"
            if value.startswith('{') and value.endswith('}'):
                try:
                    import ast
                    parsed = ast.literal_eval(value)
                    if isinstance(parsed, set):
                        return UncertaintyLevel(Tolerance.FLEXIBLE), parsed, None
                except (ValueError, SyntaxError):
                    pass
            
            # Format "1,2,3" (CSV)
            if ',' in value:
                items = {item.strip() for item in value.split(',')}
                return UncertaintyLevel(Tolerance.FLEXIBLE), items, None
        
        # Tenter de convertir en set
        try:
            return UncertaintyLevel(Tolerance.TYPE_COMPLIANT), set(value), None
        except (TypeError, ValueError) as e:
            return UncertaintyLevel(Tolerance.ANYTHING), value, str(e)

class GuardedDict(GuardedPrimitive, dict):
    """
    Dictionnaire sémantique.
    Accepte : {"a": 1}, '{"a": 1}', ou tout mapping.
    """
    _type_en = "a dictionary mapping keys to values"
    _type_py = dict
    _type_json = {"type": "object"}
    
    @classmethod
    def _parse_native(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        if isinstance(value, dict):
            return UncertaintyLevel(Tolerance.STRICT), value, None
        return UncertaintyLevel(Tolerance.ANYTHING), value, None
    
    @classmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        # Accepter les strings représentant des dicts
        if isinstance(value, str):
            value = value.strip()
            
            # Format JSON
            if value.startswith('{') and value.endswith('}'):
                try:
                    import json
                    parsed = json.loads(value)
                    if isinstance(parsed, dict):
                        return UncertaintyLevel(Tolerance.FLEXIBLE), parsed, None
                except (json.JSONDecodeError, ValueError):
                    # Essayer avec ast.literal_eval
                    try:
                        import ast
                        parsed = ast.literal_eval(value)
                        if isinstance(parsed, dict):
                            return UncertaintyLevel(Tolerance.FLEXIBLE), parsed, None
                    except (ValueError, SyntaxError):
                        pass
        
        # Tenter de convertir en dict
        try:
            return UncertaintyLevel(Tolerance.TYPE_COMPLIANT), dict(value), None
        except (TypeError, ValueError) as e:
            return UncertaintyLevel(Tolerance.ANYTHING), value, str(e)

class GuardedTuple(GuardedPrimitive, tuple):
    """
    Tuple sémantique.
    Accepte : (1, 2, 3), "(1, 2, 3)", "1,2,3", ou toute itérable.
    """
    _type_en = "a tuple of items"
    _type_py = tuple
    _type_json = {"type": "array"}
    
    @classmethod
    def _parse_native(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        if isinstance(value, tuple):
            return UncertaintyLevel(Tolerance.STRICT), value, None
        return UncertaintyLevel(Tolerance.ANYTHING), value, None
    
    @classmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        # Accepter les listes et sets
        if isinstance(value, (list, set, frozenset)):
            return UncertaintyLevel(Tolerance.PRECISE), tuple(value), None
        
        # Accepter les strings représentant des tuples
        if isinstance(value, str):
            value = value.strip()
            
            # Format "(1, 2, 3)"
            if value.startswith('(') and value.endswith(')'):
                try:
                    import ast
                    parsed = ast.literal_eval(value)
                    if isinstance(parsed, tuple):
                        return UncertaintyLevel(Tolerance.FLEXIBLE), parsed, None
                except (ValueError, SyntaxError):
                    pass
            
            # Format "1,2,3" (CSV)
            if ',' in value:
                items = tuple(item.strip() for item in value.split(','))
                return UncertaintyLevel(Tolerance.FLEXIBLE), items, None
        
        # Tenter de convertir en tuple
        try:
            return UncertaintyLevel(Tolerance.TYPE_COMPLIANT), tuple(value), None
        except (TypeError, ValueError) as e:
            return UncertaintyLevel(Tolerance.ANYTHING), value, str(e)

def guarded_dataclass(cls):
    """
    Decorator qui transforme une dataclass en GuardedDataclass.
    
    Usage:
        from dataclasses import dataclass
        from OpenHosta.guarded import guarded_dataclass
        
        @guarded_dataclass
        @dataclass
        class Person:
            name: str
            age: int
        
        p = Person({"name": "Alice", "age": "25"})  # ✅ Accepte dict
        p = Person(name="Bob", age=30)              # ✅ Accepte kwargs
    """
    from dataclasses import fields, is_dataclass
    
    if not is_dataclass(cls):
        raise TypeError(f"{cls.__name__} must be a dataclass")
    
    class GuardedDataclassWrapper(GuardedPrimitive, cls):
        _type_en = f"an instance of {cls.__name__} dataclass"
        _type_py = cls
        _type_json = {"type": "object"}
        
        @classmethod
        def _parse_native(cls_inner, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
            if isinstance(value, cls):
                return UncertaintyLevel(Tolerance.STRICT), value, None
            return UncertaintyLevel(Tolerance.ANYTHING), value, None
        
        @classmethod
        def _parse_heuristic(cls_inner, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
            # Accepter un dict
            if isinstance(value, dict):
                try:
                    # Créer l'instance avec les champs du dict
                    field_values = {}
                    for field in fields(cls):
                        if field.name in value:
                            field_values[field.name] = value[field.name]
                    
                    instance = cls(**field_values)
                    return UncertaintyLevel(Tolerance.FLEXIBLE), instance, None
                except Exception as e:
                    return UncertaintyLevel(Tolerance.ANYTHING), value, str(e)
            
            return UncertaintyLevel(Tolerance.ANYTHING), value, None
    
    GuardedDataclassWrapper.__name__ = cls.__name__
    GuardedDataclassWrapper.__module__ = cls.__module__
    GuardedDataclassWrapper.__qualname__ = cls.__qualname__
    
    return GuardedDataclassWrapper
