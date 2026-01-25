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
    _item_type = None

    def __class_getitem__(cls, item):
        class ParameterizedGuardedList(cls):
            _item_type = item
            _type_en = f"a list of {item._type_en if hasattr(item, '_type_en') else str(item)}"
        return ParameterizedGuardedList
    
    @classmethod
    def _parse_native(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        if isinstance(value, list):
            if cls._item_type:
                try:
                    # Convert items if needed
                    converted = [cls._item_type(item) for item in value]
                    # If conversion happened (or types were checked), we return them
                    return UncertaintyLevel(Tolerance.STRICT), converted, None
                except Exception as e:
                    return UncertaintyLevel(Tolerance.ANYTHING), value, f"Item conversion failed: {e}"
            return UncertaintyLevel(Tolerance.STRICT), value, None
        return UncertaintyLevel(Tolerance.ANYTHING), value, None
    
    @classmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        items = None
        # Accepter les tuples, sets, et autres itérables
        if isinstance(value, (tuple, set, frozenset)):
            items = list(value)
        
        # Accepter les strings représentant des listes
        elif isinstance(value, str):
            value_s = value.strip()
            
            # Format "[1, 2, 3]"
            if value_s.startswith('[') and value_s.endswith(']'):
                try:
                    import ast
                    parsed = ast.literal_eval(value_s)
                    if isinstance(parsed, list):
                        items = parsed
                except (ValueError, SyntaxError) as e:
                    pass
            
            # Format "1,2,3" (CSV)
            if items is None and ',' in value_s:
                items = [item.strip() for item in value_s.split(',')]
        
        # Tenter de convertir en liste
        if items is None:
            try:
                items = list(value)
            except (TypeError, ValueError):
                return UncertaintyLevel(Tolerance.ANYTHING), value, "Could not convert to list"

        # Content validation
        if cls._item_type:
            try:
                converted = [cls._item_type(item) for item in items]
                return UncertaintyLevel(Tolerance.PRECISE), converted, None
            except Exception as e:
                return UncertaintyLevel(Tolerance.ANYTHING), value, f"Item conversion failed: {e}"
        
        return UncertaintyLevel(Tolerance.PRECISE), items, None

class GuardedSet(GuardedPrimitive, set):
    """
    Ensemble sémantique.
    Accepte : {1, 2, 3}, "{1, 2, 3}", "1,2,3", ou toute itérable.
    """
    _type_en = "a set of unique items"
    _type_py = set
    _type_json = {"type": "array", "uniqueItems": True}
    _item_type = None

    def __class_getitem__(cls, item):
        class ParameterizedGuardedSet(cls):
            _item_type = item
            _type_en = f"a set of {item._type_en if hasattr(item, '_type_en') else str(item)}"
        return ParameterizedGuardedSet
    
    @classmethod
    def _parse_native(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        if isinstance(value, (set, frozenset)):
            if cls._item_type:
                try:
                    converted = {cls._item_type(item) for item in value}
                    return UncertaintyLevel(Tolerance.STRICT), converted, None
                except Exception as e:
                    return UncertaintyLevel(Tolerance.ANYTHING), value, f"Item conversion failed: {e}"
            return UncertaintyLevel(Tolerance.STRICT), set(value), None
        return UncertaintyLevel(Tolerance.ANYTHING), value, None
    
    @classmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        items = None
        # Accepter les listes et tuples
        if isinstance(value, (list, tuple)):
            items = set(value)
        
        # Accepter les strings représentant des sets
        elif isinstance(value, str):
            value_s = value.strip()
            
            # Format "{1, 2, 3}"
            if value_s.startswith('{') and value_s.endswith('}'):
                try:
                    import ast
                    parsed = ast.literal_eval(value_s)
                    if isinstance(parsed, (set, list, tuple)):
                        items = set(parsed)
                except (ValueError, SyntaxError):
                    pass
            
            # Format "1,2,3" (CSV)
            if items is None and ',' in value_s:
                items = {item.strip() for item in value_s.split(',')}
        
        # Tenter de convertir en set
        if items is None:
            try:
                items = set(value)
            except (TypeError, ValueError):
                return UncertaintyLevel(Tolerance.ANYTHING), value, "Could not convert to set"

        # Content validation
        if cls._item_type:
            try:
                converted = {cls._item_type(item) for item in items}
                return UncertaintyLevel(Tolerance.PRECISE), converted, None
            except Exception as e:
                return UncertaintyLevel(Tolerance.ANYTHING), value, f"Item conversion failed: {e}"
        
        return UncertaintyLevel(Tolerance.PRECISE), items, None

class GuardedDict(GuardedPrimitive, dict):
    """
    Dictionnaire sémantique.
    Accepte : {"a": 1}, '{"a": 1}', ou tout mapping.
    """
    _type_en = "a dictionary mapping keys to values"
    _type_py = dict
    _type_json = {"type": "object"}
    _key_type = None
    _value_type = None

    def __class_getitem__(cls, item):
        if not isinstance(item, tuple) or len(item) != 2:
            return cls
        class ParameterizedGuardedDict(cls):
            _key_type = item[0]
            _value_type = item[1]
            _type_en = f"a dictionary mapping {item[0]._type_en if hasattr(item[0], '_type_en') else str(item[0])} to {item[1]._type_en if hasattr(item[1], '_type_en') else str(item[1])}"
        return ParameterizedGuardedDict
    
    @classmethod
    def _parse_native(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        if isinstance(value, dict):
            if cls._key_type or cls._value_type:
                try:
                    converted = {}
                    for k, v in value.items():
                        new_k = cls._key_type(k) if cls._key_type else k
                        new_v = cls._value_type(v) if cls._value_type else v
                        converted[new_k] = new_v
                    return UncertaintyLevel(Tolerance.STRICT), converted, None
                except Exception as e:
                    return UncertaintyLevel(Tolerance.ANYTHING), value, f"Item conversion failed: {e}"
            return UncertaintyLevel(Tolerance.STRICT), value, None
        return UncertaintyLevel(Tolerance.ANYTHING), value, None
    
    @classmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        items = None
        # Accepter les strings représentant des dicts
        if isinstance(value, str):
            value_s = value.strip()
            
            # Format JSON
            if value_s.startswith('{') and value_s.endswith('}'):
                try:
                    import json
                    parsed = json.loads(value_s)
                    if isinstance(parsed, dict):
                        items = parsed
                except (json.JSONDecodeError, ValueError):
                    # Essayer avec ast.literal_eval
                    try:
                        import ast
                        parsed = ast.literal_eval(value_s)
                        if isinstance(parsed, dict):
                            items = parsed
                    except (ValueError, SyntaxError):
                        pass
        
        # Tenter de convertir en dict
        if items is None:
            try:
                items = dict(value)
            except (TypeError, ValueError):
                return UncertaintyLevel(Tolerance.ANYTHING), value, "Could not convert to dict"

        # Content validation
        if cls._key_type or cls._value_type:
            try:
                converted = {}
                for k, v in items.items():
                    new_k = cls._key_type(k) if cls._key_type else k
                    new_v = cls._value_type(v) if cls._value_type else v
                    converted[new_k] = new_v
                return UncertaintyLevel(Tolerance.PRECISE), converted, None
            except Exception as e:
                return UncertaintyLevel(Tolerance.ANYTHING), value, f"Item conversion failed: {e}"
        
        return UncertaintyLevel(Tolerance.PRECISE), items, None

class GuardedTuple(GuardedPrimitive, tuple):
    """
    Tuple sémantique.
    Accepte : (1, 2, 3), "(1, 2, 3)", "1,2,3", ou toute itérable.
    """
    _type_en = "a tuple of items"
    _type_py = tuple
    _type_json = {"type": "array"}
    _item_types = None # None or tuple of types

    def __class_getitem__(cls, items):
        if not isinstance(items, tuple):
            items = (items,)
        
        class ParameterizedGuardedTuple(cls):
            _item_types = items
            _type_en = f"a tuple of ({', '.join(t._type_en if hasattr(t, '_type_en') else str(t) for t in items)})"
        return ParameterizedGuardedTuple
    
    @classmethod
    def _parse_native(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        if isinstance(value, tuple):
            if cls._item_types:
                # Variable length if ... (not supported yet) or fixed length
                if len(value) != len(cls._item_types):
                    return UncertaintyLevel(Tolerance.ANYTHING), value, f"Tuple length mismatch: expected {len(cls._item_types)}, got {len(value)}"
                try:
                    converted = tuple(cls._item_types[i](value[i]) for i in range(len(value)))
                    return UncertaintyLevel(Tolerance.STRICT), converted, None
                except Exception as e:
                    return UncertaintyLevel(Tolerance.ANYTHING), value, f"Item conversion failed: {e}"
            return UncertaintyLevel(Tolerance.STRICT), value, None
        return UncertaintyLevel(Tolerance.ANYTHING), value, None
    
    @classmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        items = None
        # Accepter les listes et sets
        if isinstance(value, (list, set, frozenset)):
            items = tuple(value)
        
        # Accepter les strings représentant des tuples
        elif isinstance(value, str):
            value_s = value.strip()
            
            # Format "(1, 2, 3)"
            if value_s.startswith('(') and value_s.endswith(')'):
                try:
                    import ast
                    parsed = ast.literal_eval(value_s)
                    if isinstance(parsed, tuple):
                        items = parsed
                except (ValueError, SyntaxError):
                    pass
            
            # Format "1,2,3" (CSV)
            if items is None and ',' in value_s:
                items = tuple(item.strip() for item in value_s.split(','))
        
        if items is None:
            try:
                items = tuple(value)
            except (TypeError, ValueError):
                return UncertaintyLevel(Tolerance.ANYTHING), value, "Could not convert to tuple"

        # Content validation
        if cls._item_types:
             # Fixed length
            if len(items) != len(cls._item_types):
                return UncertaintyLevel(Tolerance.ANYTHING), value, f"Tuple length mismatch: expected {len(cls._item_types)}, got {len(items)}"
            try:
                converted = tuple(cls._item_types[i](items[i]) for i in range(len(items)))
                return UncertaintyLevel(Tolerance.PRECISE), converted, None
            except Exception as e:
                return UncertaintyLevel(Tolerance.ANYTHING), value, f"Item conversion failed: {e}"
        
        return UncertaintyLevel(Tolerance.PRECISE), items, None

def guarded_tuple(*item_types):
    """Factory for parameterized tuples."""
    return GuardedTuple[item_types]

def guarded_dataclass(cls=None, **dataclass_kwargs):
    """
    Decorator qui transforme une classe en GuardedDataclass.
    
    Applique automatiquement @dataclass si la classe n'est pas déjà une dataclass.
    
    Usage simple (recommandé) :
        from OpenHosta.guarded import guarded_dataclass
        
        @guarded_dataclass
        class Person:
            name: str
            age: int
        
        p = Person({"name": "Alice", "age": "25"})  # ✅ Accepte dict
        p = Person(name="Bob", age=30)              # ✅ Accepte kwargs
    
    Usage avec options dataclass :
        @guarded_dataclass(frozen=True, order=True)
        class Point:
            x: int
            y: int
    
    Usage avec @dataclass explicite (legacy) :
        from dataclasses import dataclass
        
        @guarded_dataclass
        @dataclass
        class Person:
            name: str
            age: int
    """
    from dataclasses import dataclass, fields, is_dataclass
    
    def decorator(cls):
        # Si ce n'est pas déjà une dataclass, on l'applique
        if not is_dataclass(cls):
            cls = dataclass(cls, **dataclass_kwargs)
        
        # Sauvegarder le __init__ original de la dataclass
        original_init = cls.__init__
        
        class GuardedDataclassWrapper(cls):
            """Wrapper qui ajoute les capacités Guarded à une dataclass."""
            
            _type_en = f"an instance of {cls.__name__} dataclass"
            _type_py = cls
            _type_json = {"type": "object"}
            _tolerance = Tolerance.TYPE_COMPLIANT
            
            def __init__(self, *args, **kwargs):
                """
                Gère deux modes d'instanciation :
                1. Mode dict : GuardedDataclass({"field": value})
                2. Mode kwargs : GuardedDataclass(field=value)
                """
                # Mode dict : un seul argument qui est un dict
                if len(args) == 1 and len(kwargs) == 0 and isinstance(args[0], dict):
                    data = args[0]
                    # Extraire et convertir les champs du dict
                    field_values = {}
                    for field in fields(cls):
                        if field.name in data:
                            value = data[field.name]
                            # Essayer de convertir la valeur au bon type
                            if field.type and value is not None:
                                try:
                                    # Import local pour éviter cycle
                                    from .resolver import TypeResolver
                                    guarded_type = TypeResolver.resolve(field.type)
                                    # Si c'est un type Guarded, l'utiliser pour convertir
                                    if hasattr(guarded_type, '__new__'):
                                        value = guarded_type(value)
                                except Exception as e:
                                    # Log l'erreur mais continuer
                                    import warnings
                                    warnings.warn(f"Failed to convert {field.name}={value!r} to {field.type}: {e}")
                            field_values[field.name] = value
                    
                    # Appeler le __init__ parent avec les kwargs
                    super(GuardedDataclassWrapper, self).__init__(**field_values)
                    
                    # Ajouter les métadonnées Guarded
                    self._uncertainty = UncertaintyLevel(Tolerance.FLEXIBLE)
                    self._abstraction_level = 'heuristic'
                    self._input = data
                else:
                    # Mode normal : kwargs ou args positionnels
                    super(GuardedDataclassWrapper, self).__init__(*args, **kwargs)
                    
                    # Ajouter les métadonnées Guarded
                    self._uncertainty = UncertaintyLevel(Tolerance.STRICT)
                    self._abstraction_level = 'native'
                    self._input = (args, kwargs)
            
            @property
            def uncertainty(self):
                """Niveau d'incertitude de la conversion."""
                return getattr(self, '_uncertainty', UncertaintyLevel(Tolerance.STRICT))
            
            @property
            def abstraction_level(self):
                """Niveau d'abstraction utilisé pour la conversion."""
                return getattr(self, '_abstraction_level', 'native')
            
            def unwrap(self):
                """Retourne l'instance elle-même (déjà un objet natif)."""
                return self
        
        GuardedDataclassWrapper.__name__ = cls.__name__
        GuardedDataclassWrapper.__module__ = cls.__module__
        GuardedDataclassWrapper.__qualname__ = cls.__qualname__
        GuardedDataclassWrapper.__doc__ = cls.__doc__
        
        return GuardedDataclassWrapper
    
    # Support pour @guarded_dataclass et @guarded_dataclass()
    if cls is None:
        # Appelé avec arguments : @guarded_dataclass(frozen=True)
        return decorator
    else:
        # Appelé sans arguments : @guarded_dataclass
        return decorator(cls)


