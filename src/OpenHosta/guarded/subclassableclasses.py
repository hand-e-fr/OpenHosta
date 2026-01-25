# ==============================================================================
# ENUM, DATACLASS, CLASS, INTERFACE 
# ==============================================================================

from typing import Any, Tuple, Optional, Type

from enum import Enum

# Assurez-vous d'avoir importé GuardedPrimitive
from .primitives import GuardedPrimitive, UncertaintyLevel, Tolerance, ProxyWrapper

class GuardedEnum(GuardedPrimitive, ProxyWrapper):
    """
    Classe de base pour créer des enums validées sémantiquement.
    
    Remplace `enum.Enum` pour permettre la validation flexible.
    
    Usage:
        from OpenHosta.guarded import GuardedEnum
        
        class Status(GuardedEnum):
            PENDING = "pending"
            ACTIVE = "active"
            DONE = "done"
        
        # Accepte plusieurs formats
        s1 = Status("active")        # ✅ Par nom
        s2 = Status("ACTIVE")        # ✅ Case-insensitive
        s3 = Status("pending")       # ✅ Par valeur
        
        # Récupération de la valeur
        s1.unwrap()  # → "active"
        str(s1)      # → "ACTIVE"
    
    Note: isinstance(s1, Status) → True, mais isinstance(s1, str) → False
          Utilisez .unwrap() si vous avez besoin de la valeur native.
    """
    
    _members: dict = {}  # Sera rempli par __init_subclass__
    
    def __init_subclass__(cls, **kwargs):
        """Appelé automatiquement quand on crée une sous-classe."""
        super().__init_subclass__(**kwargs)
        
        # Collecter les membres de l'enum
        cls._members = {}
        for name, value in cls.__dict__.items():
            if not name.startswith('_') and not callable(value):
                cls._members[name] = value
        
        # Configuration pour GuardedPrimitive
        cls._type_en = f"a value from {cls.__name__} enum"
        cls._type_py = cls
        cls._type_json = {
            "type": "string",
            "enum": list(cls._members.keys())
        }
    
    @classmethod
    def _parse_native(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        """Vérifie si la valeur est déjà un membre de l'enum."""
        if isinstance(value, cls):
            return UncertaintyLevel(Tolerance.STRICT), value._python_value, None
        
        # Si c'est un nom de membre
        if value in cls._members:
            return UncertaintyLevel(Tolerance.STRICT), value, None
        
        return UncertaintyLevel(Tolerance.ANYTHING), value, None
    
    @classmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        """Recherche case-insensitive par nom ou par valeur."""
        # Recherche case-insensitive par nom
        if isinstance(value, str):
            for name in cls._members:
                if name.lower() == value.lower():
                    return UncertaintyLevel(Tolerance.PRECISE), name, None
        
        # Recherche par valeur
        for name, member_value in cls._members.items():
            if member_value == value:
                return UncertaintyLevel(Tolerance.PRECISE), name, None
        
        return UncertaintyLevel(Tolerance.ANYTHING), value, "Invalid enum value"
    
    def __repr__(self):
        """Représentation comme Enum.MEMBER."""
        return f"{self.__class__.__name__}.{self._python_value}"
    
    @property
    def name(self):
        """Nom du membre (compatible avec enum.Enum)."""
        return self._python_value
    
    @property
    def value(self):
        """Valeur du membre (compatible avec enum.Enum)."""
        return self._members.get(self._python_value)
