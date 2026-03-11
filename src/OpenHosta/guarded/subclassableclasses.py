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
        if isinstance(value, str):
            cleaned_val = value.strip().strip('<>').strip("'").strip('"')
            
            # Format "EnumName.MEMBER" ou ".MEMBER" (comme repr())
            member_candidate = cleaned_val
            if '.' in cleaned_val:
                parts = cleaned_val.split('.')
                # On prend le dernier élément comme candidat de membre
                member_candidate = parts[-1]
            
            # 1. Recherche exacte (case-insensitive) par nom
            for name in cls._members:
                if name.lower() == member_candidate.lower():
                    return UncertaintyLevel(Tolerance.PRECISE), name, None
            
            # 2. Recherche par suffixe (ex: PUSH matche GIT_PUSH)
            # Utile car les LLM abrègent souvent les préfixes techniques
            for name in cls._members:
                if name.lower().endswith(member_candidate.lower()):
                    return UncertaintyLevel(Tolerance.FLEXIBLE), name, None

            # 3. Recherche case-insensitive par nom complet original (si pas de point)
            if member_candidate == cleaned_val:
                for name in cls._members:
                    if name.lower() == cleaned_val.lower():
                        return UncertaintyLevel(Tolerance.PRECISE), name, None
        
        # 4. Recherche par valeur
        for name, member_value in cls._members.items():
            if str(member_value).lower() == str(value).lower():
                return UncertaintyLevel(Tolerance.PRECISE), name, None
        
        # 5. Fallback for models returning JSON (as dict or string)
        if isinstance(value, str) and value.strip().startswith("{") and value.strip().endswith("}"):
            try:
                import json
                parsed = json.loads(value)
                return cls._parse_heuristic(parsed)
            except:
                pass

        if isinstance(value, dict) and len(value) == 1:
            dict_val = list(value.values())[0]
            # Recursive call with the dict value
            return cls._parse_heuristic(dict_val)

        return UncertaintyLevel(Tolerance.ANYTHING), value, "Invalid enum value"
    
    def __eq__(self, other):
        """Compaire le membre par nom ou par valeur."""
        if isinstance(other, ProxyWrapper):
            return self._python_value == other._python_value
        
        if isinstance(other, Enum):
            return self._python_value == other.name or self.value == other.value
            
        return self._python_value == other or self.value == other

    def __repr__(self):
        """Représentation compatible Enum: <ClassName.MEMBER: value>."""
        # On essaie d'enlever le préfixe 'Guarded_' pour la lisibilité
        display_name = self.__class__.__name__
        if display_name.startswith('Guarded_'):
            display_name = display_name[8:]
        return f"<{display_name}.{self._python_value}: {self.value!r}>"
    
    @property
    def name(self):
        """Nom du membre (compatible avec enum.Enum)."""
        return self._python_value
    
    @property
    def value(self):
        """Valeur du membre (compatible avec enum.Enum)."""
        return self._members.get(self._python_value)

def guarded_enum(enum_cls: Type[Enum]) -> Type[GuardedEnum]:
    """
    Factory pour transformer une Enum standard en GuardedEnum.
    """
    if issubclass(enum_cls, GuardedEnum):
        return enum_cls
    
    # Créer les attributs pour la nouvelle classe
    attrs = {}
    for name, member in enum_cls.__members__.items():
        attrs[name] = member.value
        
    # Créer dynamiquement la sous-classe avec les membres déjà présents
    # pour que __init_subclass__ les capture.
    new_name = f"Guarded_{enum_cls.__name__}"
    WrappedEnum = type(new_name, (GuardedEnum,), attrs)
    
    WrappedEnum.__doc__ = enum_cls.__doc__
    
    return WrappedEnum
