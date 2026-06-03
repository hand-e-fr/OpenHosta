# mypy: ignore-errors
# ==============================================================================
# ENUM, DATACLASS, CLASS, INTERFACE
# ==============================================================================

from dataclasses import fields, is_dataclass
from enum import Enum
from typing import Any

from .primitives import GuardedPrimitive, ProxyWrapper, Tolerance, UncertaintyLevel


class GuardedEnum(GuardedPrimitive, ProxyWrapper):
    """
    Classe de base pour créer des enums validées sémantiquement.

    Remplace `enum.Enum` pour permettre la validation flexible.

    Usage:
        from openhosta.guarded import GuardedEnum

        class Status(GuardedEnum):
            PENDING = "pending"
            ACTIVE = "active"
            DONE = "done"

        # Accepte plusieurs formats
        s1 = Status("active")        # ✅ Par valeur
        s2 = Status("ACTIVE")        # ✅ Par nom
        s3 = Status("pending")       # ✅ Par valeur

        # Récupération de la valeur
        s1.unwrap()  # → "active"
        str(s1)      # → "active"

    Note: isinstance(s1, Status) → True, mais isinstance(s1, str) → False
          Utilisez .unwrap() si vous avez besoin de la valeur native.
    """

    _members: dict = {}
    _native_class: type[Enum] | None = None
    _type_en: str = "an enum value"
    _type_py: type = str
    _type_json: dict = {"type": "string"}
    _tolerance = Tolerance.TYPE_COMPLIANT

    def __init_subclass__(cls, **kwargs):
        """Appelé automatiquement quand on crée une sous-classe."""
        super().__init_subclass__(**kwargs)

        cls._members = {}
        for name, value in cls.__dict__.items():
            if not name.startswith('_') and not callable(value):
                cls._members[name] = value

        cls._type_en = f"a value from {cls.__name__} enum"

        cls._type_py = str
        cls._type_py_repr = cls._build_type_py_repr()
        cls._type_json = {
            "type": "string",
            "enum": list(cls._members.keys())
        }


    @classmethod
    def _describe_value_type(cls, value: Any) -> str:
        value_type = type(value)

        if is_dataclass(value) and not isinstance(value, type):
            field_lines = []
            for field in fields(value):
                field_value = getattr(value, field.name)
                field_lines.append(
                    f"    - {field.name}: {field.type} = {field_value!r}"
                )
            joined = "\n".join(field_lines) if field_lines else "    - <no fields>"
            return f"dataclass {value_type.__name__}:\n{joined}"

        return getattr(value_type, "__name__", repr(value_type))

    @classmethod
    def _build_type_py_repr(cls) -> str:
        display_name = cls.__name__
        if display_name.startswith("Guarded_"):
            display_name = display_name[8:]

        member_lines = []
        for name, value in cls._members.items():
            value_type_description = cls._describe_value_type(value)
            member_lines.append(
                f"    {display_name}.{name} = {value!r}    # value_type: {value_type_description}"
            )

        joined_members = "\n".join(member_lines) if member_lines else "<no members>"
        return f"class {display_name}(Enum):\n{joined_members}"

    @property
    def casting_uncertainty(self) -> UncertaintyLevel:
        return getattr(self, "_casting_uncertainty", 1.0)

    @property
    def source_uncertainty(self) -> UncertaintyLevel:
        return getattr(self, "_source_uncertainty", None)

    @property
    def uncertainty(self) -> UncertaintyLevel:
        c = getattr(self, "_casting_uncertainty", 1.0)
        s = getattr(self, "_source_uncertainty", None)
        if s is None:
            return c
        return 1.0 - (1.0 - c) * (1.0 - s)

    @property
    def abstraction_level(self) -> str:
        return getattr(self, "_abstraction_level", "unknown")

    def unwrap(self):
        """Retourne le membre de l'enum natif s'il est disponible, sinon la valeur native."""
        if self._native_class:
            if isinstance(self._python_value, self._native_class):
                return self._python_value
            try:
                return self._native_class[self._python_value]
            except (KeyError, TypeError):
                pass
        return self.value

    @classmethod
    def _parse_native(cls, value: Any) -> tuple[UncertaintyLevel, Any, str | None]:
        """Vérifie si la valeur est déjà un membre de l'enum."""
        if isinstance(value, cls):
            return UncertaintyLevel(Tolerance.STRICT), value._python_value, None

        if isinstance(value, Enum) and value.name in cls._members:
            return UncertaintyLevel(Tolerance.STRICT), value, None

        if isinstance(value, str) and value in cls._members:
            try:
                return UncertaintyLevel(Tolerance.STRICT), cls._native_class[value], None
            except KeyError:
                return UncertaintyLevel(Tolerance.STRICT), cls._native_class(cls._members[value]), None

        return UncertaintyLevel(Tolerance.ANYTHING), value, "Invalid enum value"

    @classmethod
    def _parse_heuristic(cls, value: Any) -> tuple[UncertaintyLevel, Any, str | None]:
        """Recherche case-insensitive par nom ou par valeur."""

        cleaned_val = cls._clean_llm_response(value)

        if len(cleaned_val) > 3 and "\n" in cleaned_val[1:-1]:
            candidates = [GuardedEnum.attempt(p) for p in cleaned_val.split("\n")]
            candidates = [c for c in candidates if c.success]
            if len(candidates) > 0:
                # TODO: return the most likely candidate based on the context of the document
                return UncertaintyLevel(Tolerance.CREATIVE), candidates[0].value, None

        cleaned_val = cleaned_val.strip(" `'\"\n")

        if cleaned_val.startswith("<") and cleaned_val.endswith(">"):
            cleaned_val = cleaned_val[1:-1].strip()

        if ":" in cleaned_val:
            cleaned_val = cleaned_val.split(":", 1)[0].strip()

        # Remove wrapping quotes, including doubled quotes like ''git push''
        while len(cleaned_val) >= 2 and (
            (cleaned_val.startswith("`") and cleaned_val.endswith("`"))
            or (cleaned_val.startswith("'") and cleaned_val.endswith("'"))
            or (cleaned_val.startswith('"') and cleaned_val.endswith('"'))
        ):
            cleaned_val = cleaned_val[1:-1].strip()

        member_candidate = cleaned_val.split(".")[-1] if "." in cleaned_val else cleaned_val

        for name in cls._members:
            if name.lower() == member_candidate.lower():
                return UncertaintyLevel(Tolerance.PRECISE), cls._native_class(cls._members[name]), None

        for name, member_value in cls._members.items():
            if str(member_value).strip().lower() == cleaned_val.lower():
                return UncertaintyLevel(Tolerance.PRECISE), cls._native_class(cls._members[name]), None


        if isinstance(value, dict) and len(value) == 1:
            dict_val = list(value.values())[0]
            return cls._parse_heuristic(dict_val)

        return UncertaintyLevel(Tolerance.ANYTHING), value, "Invalid enum value"



    def __eq__(self, other):
        """Compare le membre par nom ou par valeur."""
        if isinstance(other, ProxyWrapper):
            return self._python_value == other._python_value

        if isinstance(other, Enum):
            return self._python_value == other.name or self.value == other.value

        return self._python_value == other or self.value == other

    def __repr__(self):
        """Représentation compatible Enum: <ClassName.MEMBER: value>."""
        display_name = self.__class__.__name__
        if display_name.startswith("Guarded_"):
            display_name = display_name[8:]
        return f"<{display_name}.{self.name}: {self.value!r}>"

    @property
    def name(self):
        """Nom du membre (compatible avec enum.Enum)."""
        if isinstance(self._python_value, Enum):
            return self._python_value.name
        return self._python_value

    @property
    def value(self):
        """Valeur du membre (compatible avec enum.Enum)."""
        if isinstance(self._python_value, Enum):
            return self._python_value.value
        return self._members.get(self._python_value)


# Cache pour éviter de recréer la même classe wrapper
_GUARDED_ENUM_CACHE: dict = {}

def guarded_enum(enum_cls: type[Enum]) -> type[GuardedEnum]:
    """
    Factory pour transformer une Enum standard en GuardedEnum.
    """
    if issubclass(enum_cls, GuardedEnum):
        return enum_cls

    if enum_cls in _GUARDED_ENUM_CACHE:
        return _GUARDED_ENUM_CACHE[enum_cls]

    attrs = {}
    for name, member in enum_cls.__members__.items():
        attrs[name] = member.value

    new_name = f"Guarded_{enum_cls.__name__}"
    guarded_enum_cls = type(new_name, (GuardedEnum,), attrs)
    guarded_enum_cls._native_class = enum_cls
    guarded_enum_cls.__doc__ = enum_cls.__doc__

    _GUARDED_ENUM_CACHE[enum_cls] = guarded_enum_cls
    return guarded_enum_cls
