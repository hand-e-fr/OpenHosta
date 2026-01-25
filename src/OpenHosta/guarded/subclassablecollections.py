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


