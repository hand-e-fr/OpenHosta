"""
OpenHosta.Guarded — Typage probabiliste avec Self-Healing et Observabilité
==========================================================================

Proxy transparent Guarded[T] pour encapsuler des données génératives (LLM)
tout en préservant l'expérience développeur (Duck Typing absolu) et en
transportant silencieusement les traces d'observabilité.

Principes :
  1. Transparence — Guarded[T] réagit aux opérateurs standards exactement comme T
  2. Zéro-Collision — Métadonnées dans __guard_data__, pas de pollution de l'objet natif
  3. Déclaration Native — Compatible typing.Annotated pour Mypy/Pyright
  4. Symétrie Récursive — guard()/unguard() parcourent automatiquement les graphes
  5. Agrégation Cumulative — Coûts et incertitudes se somment à travers les structures
  6. Miroir Tri-Modal — Export Python / JSON Schema / Markdown pour les prompts LLM
"""

from __future__ import annotations

import dataclasses
import inspect
import functools
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import (
    Any,
    Generic,
    TypeVar,
    Type,
    Iterator,
    overload,
    cast,
    Callable,
)

T = TypeVar("T")
F = TypeVar("F", bound=Callable)


# --------------------------------------------------------------------------- #
# 1. CONFIG & METADATA                                                        #
# --------------------------------------------------------------------------- #

@dataclass
class GuardConfig:
    """Contrat de génération/validation déclaré via typing.Annotated.

    Usage :
        SafeStr = Annotated[Guarded[str], GuardConfig(max_uncertainty=0.5, max_effort_ms=1000)]
    """
    max_uncertainty: float = 1.0
    max_effort_ms: int = 120_000  # 2 min
    heal_retries_per_layer: int = 2


@dataclass
class GuardMetadata:
    """Empreinte de la génération IA : incertitude, temps, logs, healing.

    Supporte l'addition pour l'agrégation cumulative à travers les graphes.
    """

    uncertainty: float = 0.0
    time_consumed: float = 0.0
    llm_logs: list[dict] = field(default_factory=list)
    heal_traces: list[str] = field(default_factory=list)

    def __add__(self, other: GuardMetadata) -> GuardMetadata:
        """Agrégation cumulative des métadonnées."""
        return GuardMetadata(
            uncertainty=self.uncertainty + other.uncertainty,
            time_consumed=self.time_consumed + other.time_consumed,
            llm_logs=self.llm_logs + other.llm_logs,
            heal_traces=self.heal_traces + other.heal_traces,
        )

    def __radd__(self, other: GuardMetadata) -> GuardMetadata:
        return self.__add__(other)

    def __repr__(self) -> str:
        return (
            f"GuardMetadata(uncertainty={self.uncertainty:.2f}, "
            f"time_consumed={self.time_consumed:.1f}ms, "
            f"llm_logs={len(self.llm_logs)}, "
            f"heal_traces={len(self.heal_traces)})"
        )

    def is_empty(self) -> bool:
        """Vrai si toutes les métriques sont à 0."""
        return (
            self.uncertainty == 0.0
            and self.time_consumed == 0.0
            and not self.llm_logs
            and not self.heal_traces
        )


# --------------------------------------------------------------------------- #
# 2. REGISTRY — Extension points for custom types                             #
# --------------------------------------------------------------------------- #


class _Layer:
    """Couche d'instanciation pour un type métier spécifique."""

    __slots__ = ("name", "condition", "layer_logic")

    def __init__(self, name: str, condition: Callable[[Any], bool], layer_logic: Callable[..., Any]):
        self.name = name
        self.condition = condition
        self.layer_logic = layer_logic


class _Registry:
    """Registre extensible des layers d'instanciation.

    Permet d'ajouter des types métiers inconnus du moteur.
    Les layers Primitives, Enum et (optionnel) Pydantic sont inclus par défaut.
    """

    def __init__(self):
        self._layers: list[_Layer] = []
        self._register_defaults()

    def _register_defaults(self) -> None:
        """Inscription des layers par défaut : Primitives, Enum."""
        # -- Primitive layer --
        def _is_primitive(obj: Any) -> bool:
            return isinstance(obj, (str, int, float, bool, type(None)))

        def _primitive_logic(obj: Any) -> Guarded:
            return Guarded(obj, GuardMetadata())

        self.register_layer("primitive", _is_primitive, _primitive_logic)

        # -- Enum layer --
        def _is_enum(obj: Any) -> bool:
            return isinstance(obj, Enum)

        def _enum_logic(obj: Enum) -> Guarded:
            return Guarded(obj, GuardMetadata())

        self.register_layer("enum", _is_enum, _enum_logic)

    def register_layer(self, name: str, condition: Callable[[Any], bool], layer_logic: Callable[..., Any]) -> None:
        """Enregistre une couche d'instanciation personnalisée."""
        self._layers.append(_Layer(name, condition, layer_logic))

    def find_layer(self, obj: Any) -> _Layer | None:
        """Retourne le premier layer dont le condition correspond, ou None."""
        for layer in self._layers:
            if layer.condition(obj):
                return layer
        return None

    def get_layers(self) -> list[_Layer]:
        return list(self._layers)


REGISTRY = _Registry()


# --------------------------------------------------------------------------- #
# 3. GUARDED PROXY — Duck Typing complet                                      #
# --------------------------------------------------------------------------- #


class Guarded(Generic[T]):
    """Proxy transparent qui délègue tout à la valeur sous-jacente tout en
    transportant les métadonnées d'observabilité.

    Principes :
      - Duck Typing absolu : tous les opérateurs standards délèguent à la valeur
      - Zéro-Collision : __guard_value__ et __guard_data__ sont exclusifs
      - Agrégation transparente : guard_info() somme les coûts récursifs

    Usage :
        val = Guarded("hello", GuardMetadata(uncertainty=0.05))
        print(val.upper())  # "HELLO" — duck typing
        print(guard_info(val).uncertainty)  # 0.05
    """

    __slots__ = ("__guard_value__", "__guard_data__")

    def __init__(self, value: T, metadata: GuardMetadata | None = None):
        object.__setattr__(self, "__guard_value__", value)
        object.__setattr__(self, "__guard_data__", metadata or GuardMetadata())

    # -- Access to internal fields (protected from __getattr__ shadowing) --
    @property
    def _value(self) -> T:
        return object.__getattribute__(self, "__guard_value__")

    @property
    def _metadata(self) -> GuardMetadata:
        return object.__getattribute__(self, "__guard_data__")

    # -- Core delegation --
    def __getattr__(self, name: str) -> Any:
        return getattr(object.__getattribute__(self, "__guard_value__"), name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name in ("__guard_value__", "__guard_data__"):
            object.__setattr__(self, name, value)
        else:
            setattr(object.__getattribute__(self, "__guard_value__"), name, value)

    # -- Comparisons --
    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Guarded):
            return object.__getattribute__(self, "__guard_value__") == object.__getattribute__(other, "__guard_value__")
        return object.__getattribute__(self, "__guard_value__") == other

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __lt__(self, other: Any) -> bool:
        return object.__getattribute__(self, "__guard_value__") < _unguard_leaf(other)

    def __le__(self, other: Any) -> bool:
        return object.__getattribute__(self, "__guard_value__") <= _unguard_leaf(other)

    def __gt__(self, other: Any) -> bool:
        return object.__getattribute__(self, "__guard_value__") > _unguard_leaf(other)

    def __ge__(self, other: Any) -> bool:
        return object.__getattribute__(self, "__guard_value__") >= _unguard_leaf(other)

    # -- Identity / Hash / Representations --
    def __hash__(self) -> int:
        return hash(object.__getattribute__(self, "__guard_value__"))

    def __repr__(self) -> str:
        return repr(object.__getattribute__(self, "__guard_value__"))

    def __str__(self) -> str:
        return str(object.__getattribute__(self, "__guard_value__"))

    def __format__(self, format_spec: str) -> str:
        return format(object.__getattribute__(self, "__guard_value__"), format_spec)

    # -- Boolean / Numeric --
    def __bool__(self) -> bool:
        return bool(object.__getattribute__(self, "__guard_value__"))

    def __neg__(self) -> Any:
        return -object.__getattribute__(self, "__guard_value__")

    def __pos__(self) -> Any:
        return +object.__getattribute__(self, "__guard_value__")

    def __abs__(self) -> Any:
        return abs(object.__getattribute__(self, "__guard_value__"))

    # -- Arithmetic --
    def __add__(self, other: Any) -> Any:
        return object.__getattribute__(self, "__guard_value__") + _unguard_leaf(other)

    def __radd__(self, other: Any) -> Any:
        return _unguard_leaf(other) + object.__getattribute__(self, "__guard_value__")

    def __sub__(self, other: Any) -> Any:
        return object.__getattribute__(self, "__guard_value__") - _unguard_leaf(other)

    def __rsub__(self, other: Any) -> Any:
        return _unguard_leaf(other) - object.__getattribute__(self, "__guard_value__")

    def __mul__(self, other: Any) -> Any:
        return object.__getattribute__(self, "__guard_value__") * _unguard_leaf(other)

    def __rmul__(self, other: Any) -> Any:
        return _unguard_leaf(other) * object.__getattribute__(self, "__guard_value__")

    def __truediv__(self, other: Any) -> Any:
        return object.__getattribute__(self, "__guard_value__") / _unguard_leaf(other)

    def __rtruediv__(self, other: Any) -> Any:
        return _unguard_leaf(other) / object.__getattribute__(self, "__guard_value__")

    def __floordiv__(self, other: Any) -> Any:
        return object.__getattribute__(self, "__guard_value__") // _unguard_leaf(other)

    def __mod__(self, other: Any) -> Any:
        return object.__getattribute__(self, "__guard_value__") % _unguard_leaf(other)

    def __pow__(self, other: Any) -> Any:
        return object.__getattribute__(self, "__guard_value__") ** _unguard_leaf(other)

    # -- Container protocols --
    def __len__(self) -> int:
        return len(object.__getattribute__(self, "__guard_value__"))

    def __iter__(self) -> Iterator:
        return iter(object.__getattribute__(self, "__guard_value__"))

    def __contains__(self, item: Any) -> bool:
        return _unguard_leaf(item) in object.__getattribute__(self, "__guard_value__")

    def __getitem__(self, key: Any) -> Any:
        return object.__getattribute__(self, "__guard_value__")[_unguard_leaf(key)]

    def __setitem__(self, key: Any, value: Any) -> None:
        obj = object.__getattribute__(self, "__guard_value__")
        obj[_unguard_leaf(key)] = value

    def __delitem__(self, key: Any) -> None:
        del object.__getattribute__(self, "__guard_value__")[key]

    # -- Sequence protocols --
    def __reversed__(self) -> Iterator:
        return reversed(object.__getattribute__(self, "__guard_value__"))

    def __index__(self) -> int:
        return int(object.__getattribute__(self, "__guard_value__"))

    # -- Callable protocol --
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return object.__getattribute__(self, "__guard_value__")(*args, **kwargs)

    # -- Context manager protocol --
    def __enter__(self) -> Any:
        return object.__getattribute__(self, "__guard_value__").__enter__()

    def __exit__(self, *args: Any) -> Any:
        return object.__getattribute__(self, "__guard_value__").__exit__(*args)


# --------------------------------------------------------------------------- #
# 4. CORE API : guard / unguard / guard_info                                  #
# --------------------------------------------------------------------------- #


def _is_guarded(obj: Any) -> bool:
    """Vérifie si obj est un Guarded (sans déclencher __getattr__)."""
    return isinstance(obj, Guarded)


def _unguard_leaf(obj: Any) -> Any:
    """Extrait la valeur d'un seul Guarded (non récursif)."""
    if _is_guarded(obj):
        return obj._value
    return obj


def _aggregate_metadata(*metas: GuardMetadata) -> GuardMetadata:
    """Somme toutes les métadonnées passées."""
    result = GuardMetadata()
    for m in metas:
        result = result + m
    return result


def _is_pydantic_model(value: Any) -> bool:
    """Détection lazy de Pydantic BaseModel."""
    try:
        from pydantic import BaseModel
        return isinstance(value, BaseModel) and not isinstance(value, type)
    except ImportError:
        return False


def _is_pydantic_model_type(value: Any) -> bool:
    """Détection lazy d'un type Pydantic BaseModel."""
    try:
        from pydantic import BaseModel
        return isinstance(value, type) and issubclass(value, BaseModel)
    except ImportError:
        return False


def guard(value: T, metadata: GuardMetadata | None = None) -> Guarded[T]:
    """Encapsule récursivement une valeur dans un proxy Guarded.

    Règles :
      - Primitive native → Guarded(value, metadata)
      - Guarded existant → renvoyer tel quel (pas de double enveloppe)
      - List/tuple → parcourir chaque élément, agréger les métadonnées
      - Dict → parcourir chaque valeur, agréger les métadonnées
      - Dataclass → parcourir chaque champ, agréger les métadonnées
      - Pydantic → parcourir chaque champ, agréger les métadonnées
      - Autre → Guarded(value, metadata)

    L'agrégation : metadata_parent = sum(children_metadata) + metadata_param
    """
    meta = metadata or GuardMetadata()
    child_metas: list[GuardMetadata] = []

    if _is_guarded(value):
        # Déjà guarded — pas de double enveloppe
        return cast(Guarded[T], value)

    if isinstance(value, list):
        guarded_items: list[Any] = []
        for item in value:
            if _is_guarded(item):
                child_metas.append(item._metadata)
                guarded_items.append(item)
            else:
                guarded_item = guard(item)
                child_metas.append(guarded_item._metadata)
                guarded_items.append(guarded_item)
        aggregated = _aggregate_metadata(meta, *child_metas)
        return Guarded(guarded_items, aggregated)

    if isinstance(value, tuple):
        guarded_items = []
        for item in value:
            if _is_guarded(item):
                child_metas.append(item._metadata)
                guarded_items.append(item)
            else:
                guarded_item = guard(item)
                child_metas.append(guarded_item._metadata)
                guarded_items.append(guarded_item)
        aggregated = _aggregate_metadata(meta, *child_metas)
        return Guarded(tuple(guarded_items), aggregated)

    if isinstance(value, dict):
        guarded_dict: dict[Any, Any] = {}
        for k, v in value.items():
            if _is_guarded(v):
                child_metas.append(v._metadata)
                guarded_dict[k] = v
            else:
                guarded_v = guard(v)
                child_metas.append(guarded_v._metadata)
                guarded_dict[k] = guarded_v
        aggregated = _aggregate_metadata(meta, *child_metas)
        return Guarded(guarded_dict, aggregated)

    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        # Dataclass — parcourir les champs
        guarded_fields: dict[str, Any] = {}
        for fld in dataclasses.fields(value):
            v = getattr(value, fld.name)
            if _is_guarded(v):
                child_metas.append(v._metadata)
                guarded_fields[fld.name] = v
            else:
                guarded_v = guard(v)
                child_metas.append(guarded_v._metadata)
                guarded_fields[fld.name] = guarded_v
        aggregated = _aggregate_metadata(meta, *child_metas)
        return Guarded(value, aggregated)

    if _is_pydantic_model(value):
        # Pydantic model — parcourir les champs
        try:
            model_fields = value.model_fields
        except AttributeError:
            model_fields = {}
        for f_name in model_fields:
            v = getattr(value, f_name)
            if _is_guarded(v):
                child_metas.append(v._metadata)
            else:
                guarded_v = guard(v)
                child_metas.append(guarded_v._metadata)
        aggregated = _aggregate_metadata(meta, *child_metas)
        return Guarded(value, aggregated)

    # Check custom registry layers
    layer = REGISTRY.find_layer(value)
    if layer:
        wrapped = layer.layer_logic(value)
        # Aggregate: existing wrapped metadata + child_metas + meta
        aggregated = _aggregate_metadata(wrapped._metadata, meta, *child_metas)
        object.__setattr__(wrapped, "__guard_data__", aggregated)
        return cast(Guarded[T], wrapped)

    # Primitive / autre → envelopper directement
    return Guarded(value, meta)


def unguard(obj: Any) -> Any:
    """Extrait récursivement la valeur native d'un graphe de données.

    Nettoie tout le graphe de ses proxies Guarded, permettant un export
    propre (JSON, DB, API) garanti sans erreur de sérialisation.
    """
    if _is_guarded(obj):
        return unguard(obj._value)

    if isinstance(obj, list):
        return [unguard(item) for item in obj]

    if isinstance(obj, tuple):
        return tuple(unguard(item) for item in obj)

    if isinstance(obj, dict):
        return {k: unguard(v) for k, v in obj.items()}

    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        cls = type(obj)
        kwargs = {}
        for fld in dataclasses.fields(obj):
            v = getattr(obj, fld.name)
            kwargs[fld.name] = unguard(v)
        return cls(**kwargs)

    if _is_pydantic_model(obj):
        # Pydantic → dict then back to model
        try:
            data = obj.model_dump()
            clean_data = {k: unguard(v) for k, v in data.items()}
            cls = type(obj)
            return cls(**clean_data)
        except AttributeError:
            pass

    # Primitive native → retourner tel quel
    return obj


def guard_info(obj: Any) -> GuardMetadata:
    """Observabilité Ops : expose l'empreinte IA d'un objet.

    Comportement :
      - Guarded[T] → retourne son GuardMetadata (déjà agrégé par guard())
      - Liste/Dict/Tuple contenant des Guarded → somme des métadonnées enfants
      - Dataclass contenant des Guarded → somme des métadonnées des champs
      - Objet 100% natif → GuardMetadata() tout à 0
    """
    if _is_guarded(obj):
        # Le metadata du Guarded est déjà l'agrégation calculée par guard()
        # PAS de re-parcours — évite le double-counting
        return obj._metadata

    # Objet natif — parcourir pour trouver des sous-Guarded
    if isinstance(obj, list):
        child_metas = [guard_info(item) for item in obj]
        return _aggregate_metadata(*child_metas)

    if isinstance(obj, tuple):
        child_metas = [guard_info(item) for item in obj]
        return _aggregate_metadata(*child_metas)

    if isinstance(obj, dict):
        child_metas = [guard_info(v) for v in obj.values()]
        return _aggregate_metadata(*child_metas)

    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        child_metas = [guard_info(getattr(obj, fld.name))
                       for fld in dataclasses.fields(obj)]
        return _aggregate_metadata(*child_metas)

    if _is_pydantic_model(obj):
        try:
            model_fields = obj.model_fields
        except AttributeError:
            model_fields = {}
        child_metas = [guard_info(getattr(obj, f_name)) for f_name in model_fields]
        return _aggregate_metadata(*child_metas)

    # Natif total → GuardMetadata vide
    return GuardMetadata()


# --------------------------------------------------------------------------- #
# 5. TRI-MODAL INTERFACE                                                      #
# --------------------------------------------------------------------------- #


def guarded_to_python(obj: Any) -> str:
    """Génère le code source Python d'un type ou d'un Guarded via introspection.

    Usage : idéal pour injecter la signature d'un type dans un prompt LLM.
    """
    value = unguard(obj) if _is_guarded(obj) else obj

    if isinstance(value, type):
        return _type_to_python(value)

    if callable(value) and not isinstance(value, type):
        sig = inspect.signature(value)
        doc = inspect.getdoc(value) or ""
        src_lines: list[str] = [f"def {value.__name__}{sig}:"]
        if doc:
            for line in doc.strip().split("\n"):
                src_lines.append(f"    {line}")
            if not doc.strip().endswith('"""'):
                src_lines.append('    """')
            src_lines.insert(1, '    """')
        else:
            src_lines.append("    ...")
        return "\n".join(src_lines)

    # Valeur simple
    type_name = type(value).__name__
    lines = [f"# type: {type_name}"]
    lines.append(repr(value))
    return "\n".join(lines)


def _type_to_python(tp: Type) -> str:
    """Génère le code Python d'un type (dataclass, Enum, etc.)."""
    if _is_pydantic_model_type(tp):
        return _pydantic_to_python(tp)

    if dataclasses.is_dataclass(tp):
        lines = ["@dataclasses.dataclass", f"class {tp.__name__}:"]
        doc = inspect.getdoc(tp)
        if doc:
            lines.append(f'    """{doc.strip()}"""')
        for fld in dataclasses.fields(tp):
            annotation = _type_hint_str(fld.type)
            lines.append(f"    {fld.name}: {annotation}")
        return "\n".join(lines)

    if isinstance(tp, type) and issubclass(tp, Enum):
        lines = [f"class {tp.__name__}(Enum):"]
        for member in tp:
            lines.append(f"    {member.name} = {member.value!r}")
        return "\n".join(lines)

    # Fallback
    return f"class {tp.__name__}: ..."


def _pydantic_to_python(tp: Type) -> str:
    """Génère le code Python depuis un Pydantic model."""
    try:
        from pydantic import BaseModel
    except ImportError:
        return f"class {tp.__name__}: ..."

    doc = inspect.getdoc(tp)
    lines = [f"class {tp.__name__}(BaseModel):"]
    if doc:
        lines.append(f'    """{doc.strip()}"""')

    model_fields = tp.model_fields if hasattr(tp, "model_fields") else {}
    for f_name, f_info in model_fields.items():
        ann = str(f_info.annotation) if f_info.annotation is not None else "Any"
        lines.append(f"    {f_name}: {ann}")
    return "\n".join(lines)


def _type_hint_str(hint: Any) -> str:
    """Convertit un type hint en string lisible."""
    if hint is None:
        return "None"
    try:
        import typing
        if hasattr(hint, '__origin__') and hasattr(hint, '__args__'):
            origin = hint.__origin__
            args = hint.__args__
            origin_name = getattr(origin, '__name__', str(origin))
            args_str = ", ".join(_type_hint_str(a) for a in args)
            return f"{origin_name}[{args_str}]"
    except (TypeError, AttributeError):
        pass
    try:
        return hint.__name__
    except AttributeError:
        return str(hint)


def guarded_to_json(target: Any) -> dict:
    """Génère un JSON Schema standard représentant le type cible.

    Délègue à Pydantic si disponible. Idéal pour configurer l'API
    response_format des LLMs.
    """
    value = unguard(target) if _is_guarded(target) else target

    if _is_pydantic_model_type(value) or _is_pydantic_model(value):
        try:
            model_cls = type(value) if _is_pydantic_model(value) else value
            return model_cls.model_json_schema()
        except AttributeError:
            pass

    if dataclasses.is_dataclass(value) or (isinstance(value, type) and dataclasses.is_dataclass(value)):
        return _dataclass_to_json(value)

    if isinstance(value, type) and issubclass(value, Enum):
        return {
            "title": value.__name__,
            "type": "string" if all(isinstance(m.value, str) for m in value) else "integer",
            "enum": [m.value for m in value],
        }

    # Primitives (bool before int because bool is subclass of int)
    if isinstance(value, bool):
        return {"type": "boolean"}
    if isinstance(value, str):
        return {"type": "string"}
    if isinstance(value, int):
        return {"type": "integer"}
    if isinstance(value, float):
        return {"type": "number"}
    if isinstance(value, bool):
        return {"type": "boolean"}
    if value is None:
        return {"type": "null"}

    return {"type": "object"}


def _dataclass_to_json(tp: Any) -> dict:
    """Convertit un dataclass en JSON Schema."""
    cls = tp if isinstance(tp, type) else type(tp)
    properties: dict[str, dict] = {}

    for fld in dataclasses.fields(cls):
        properties[fld.name] = _field_to_json_schema(fld.type)

    result: dict[str, Any] = {
        "title": cls.__name__,
        "type": "object",
        "properties": properties,
        "required": [f.name for f in dataclasses.fields(cls)],
    }
    doc = inspect.getdoc(cls)
    if doc:
        result["description"] = doc.strip()
    return result


def _field_to_json_schema(hint: Any) -> dict:
    """Convertit un type hint en JSON Schema."""
    try:
        import typing
        origin = getattr(hint, '__origin__', None)
    except (AttributeError, ImportError):
        origin = None

    if origin is list:
        args = getattr(hint, '__args__', (Any,))
        return {"type": "array", "items": _field_to_json_schema(args[0]) if args else {}}
    if origin is dict:
        args = getattr(hint, '__args__', (Any, Any))
        return {
            "type": "object",
            "additionalProperties": _field_to_json_schema(args[1]) if len(args) > 1 else {},
        }
    if origin is tuple:
        args = getattr(hint, '__args__', ())
        if args:
            return {"type": "array", "items": [_field_to_json_schema(a) for a in args]}
        return {"type": "array"}
    if origin is not None:
        import typing as _t
        # Handle Union/Optional
        if origin is _t.Union or (hasattr(_t, '_UnionGenericAlias') and origin is _t._UnionGenericAlias):
            args = getattr(hint, '__args__', ())
            if args:
                schemas = [_field_to_json_schema(a) for a in args]
                non_null = [s for s in schemas if s.get("type") != "null"]
                if len(non_null) == 1:
                    non_null[0] = {**non_null[0], "nullable": True}
                    return non_null[0]
                return {"anyOf": schemas}

    # Primitives
    if hint is str or (isinstance(hint, type) and issubclass(hint, str)):
        return {"type": "string"}
    if hint is int or (isinstance(hint, type) and issubclass(hint, int) and hint is not bool):
        return {"type": "integer"}
    if hint is float or (isinstance(hint, type) and issubclass(hint, float)):
        return {"type": "number"}
    if hint is bool or (isinstance(hint, type) and issubclass(hint, bool)):
        return {"type": "boolean"}
    if hint is None or hint is type(None):
        return {"type": "null"}

    # Dataclass / Pydantic
    if dataclasses.is_dataclass(hint):
        return _dataclass_to_json(hint)
    if _is_pydantic_model_type(hint):
        try:
            return hint.model_json_schema()
        except (AttributeError, Exception):
            pass

    if isinstance(hint, type) and issubclass(hint, Enum):
        return {
            "type": "string" if all(isinstance(m.value, str) for m in hint) else "integer",
            "enum": [m.value for m in hint],
        }

    return {"type": "object"}


def guarded_to_markdown(target: Any) -> str:
    """Génère une description textuelle et sémantique optimisée pour un LLM
    dans un System Prompt (extraction zero-shot).

    Expose les champs, types, constraints et enums pour maximiser
    la précision de la génération.
    """
    value = unguard(target) if _is_guarded(target) else target

    if _is_pydantic_model_type(value) or _is_pydantic_model(value):
        return _pydantic_to_markdown(type(value) if _is_pydantic_model(value) else value)

    if dataclasses.is_dataclass(value) or (isinstance(value, type) and dataclasses.is_dataclass(value)):
        cls = value if isinstance(value, type) else type(value)
        lines = [f"# {cls.__name__}"]
        doc = inspect.getdoc(cls)
        if doc:
            lines.append(doc.strip())
            lines.append("")
        lines.append("## Fields")
        for fld in dataclasses.fields(cls):
            annotation = _type_hint_str(fld.type)
            lines.append(f"- **{fld.name}** `{annotation}`")
            # Enum members as examples
            if isinstance(fld.type, type) and issubclass(fld.type, Enum):
                examples = ", ".join(f"`{m.value}`" for m in fld.type)
                lines.append(f"  - Allowed values: {examples}")
        return "\n".join(lines)

    if isinstance(value, type) and issubclass(value, Enum):
        lines = [f"# {value.__name__}"]
        lines.append(f"A(n) **{value.__name__}** enumeration with the following values:")
        lines.append("")
        for member in value:
            lines.append(f"- `{member.value}`: {member.name}")
        return "\n".join(lines)

    # Callable
    if callable(value) and not isinstance(value, type):
        sig = inspect.signature(value)
        doc = inspect.getdoc(value) or ""
        lines = [f"# {value.__name__}"]
        if doc:
            lines.append(doc)
            lines.append("")
        lines.append(f"Signature: `{value.__name__}{sig}`")
        return "\n".join(lines)

    return f"Value: `{value}` (type: {type(value).__name__})"


# --------------------------------------------------------------------------- #
# 6. HOSTAMODEL — décorateur auto_body (squelette v5)                         #
# --------------------------------------------------------------------------- #


class HostaModel:
    """Wrapper de modèle LLM avec décorateurs auto_body, formulate_body, emulate_body.

    Le décorateur @model.auto_body transforme une fonction signée Python
    en appel LLM automatique : docstring → prompt, signature → schema,
    retour → Guarded[T].
    """

    def __init__(self, model: str, base_url: str, capabilities: set[str] | None = None):
        self.model = model
        self.base_url = base_url
        self.capabilities = capabilities or set()

    # --- auto_body ---
    @overload
    def auto_body(self, func: F) -> F: ...

    @overload
    def auto_body(self, *args: Any, **kwargs: Any) -> Callable[[F], F]: ...

    def auto_body(self, *args: Any, **kwargs: Any) -> Any:
        """Décorateur auto_body : transforme une fonction Python en appel LLM.

        Accepte optionnellement un GuardConfig en premier argument.
        """
        config = None
        if args and not callable(args[0]):
            config = args[0]
            args = args[1:]

        def decorator(func: F) -> F:
            @functools.wraps(func)
            def wrapper(*f_args: Any, **f_kwargs: Any) -> Any:
                # TODO: Implémentation LLM (prompting, casting, self-healing)
                metadata = GuardMetadata()
                if config:
                    metadata.uncertainty = 0.0
                    metadata.time_consumed = 0.0
                return Guarded(NotImplemented, metadata)
            return cast(F, wrapper)

        if len(args) == 1 and not kwargs and callable(args[0]):
            return decorator(args[0])
        return decorator

    # --- emulate_body ---
    @overload
    def emulate_body(self, func: F) -> F: ...

    @overload
    def emulate_body(self, *args: Any, **kwargs: Any) -> Callable[[F], F]: ...

    def emulate_body(self, *args: Any, **kwargs: Any) -> Any:
        """Décorateur emulate_body : génère du code par émulation LLM."""
        config = None
        if args and not callable(args[0]):
            config = args[0]
            args = args[1:]

        def decorator(func: F) -> F:
            @functools.wraps(func)
            def wrapper(*f_args: Any, **f_kwargs: Any) -> Any:
                return Guarded(NotImplemented, GuardMetadata())
            return cast(F, wrapper)

        if len(args) == 1 and not kwargs and callable(args[0]):
            return decorator(args[0])
        return decorator

    # --- formulate_body ---
    @overload
    def formulate_body(self, func: F) -> Guarded[F]: ...

    @overload
    def formulate_body(self, *args: Any, **kwargs: Any) -> Callable[[F], Guarded[F]]: ...

    def formulate_body(self, *args: Any, **kwargs: Any) -> Any:
        """Décorateur formulate_body : formule une fonction à partir du contexte."""
        config = None
        if args and not callable(args[0]):
            config = args[0]
            args = args[1:]

        def decorator(func: F) -> F:
            @functools.wraps(func)
            def wrapper(*f_args: Any, **f_kwargs: Any) -> Any:
                return Guarded(NotImplemented, GuardMetadata())
            return cast(F, wrapper)

        if len(args) == 1 and not kwargs and callable(args[0]):
            return decorator(args[0])
        return decorator


def envmodel() -> HostaModel:
    """Crée un HostaModel à partir des variables d'environnement."""
    return HostaModel(
        model=os.environ.get("HOSTA_MODEL", "gpt-4.1"),
        base_url=os.environ.get("HOSTA_BASE_URL", "http://localhost:11434/v1"),
        capabilities={"logprobs", "streaming"},
    )
