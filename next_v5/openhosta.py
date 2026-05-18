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

import asyncio
import dataclasses
import functools
import inspect
import json
import os
import re
import sys
import typing
import urllib.request
import urllib.error
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
    get_origin,
    get_args,
    Annotated,
)

T = TypeVar("T")
F = TypeVar("F", bound=Callable)

# --------------------------------------------------------------------------- #
# V4 BRIDGE — Lazy imports to src/OpenHosta                                   #
# --------------------------------------------------------------------------- #

def _get_v4_imports():
    """
    Lazily imports V4 bricks once.
    """
    if hasattr(_get_v4_imports, "_cache"):
        return _get_v4_imports._cache
    
    cache = {}
    
    # Determine V4 src path relative to this file: next_v5/ -> ../src/
    v4_src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
    if v4_src_dir not in sys.path:
        sys.path.insert(0, v4_src_dir)

    try:
        from OpenHosta.core.analizer import hosta_analyze, AnalyzedFunction, AnalyzedArgument, encode_function
        cache["hosta_analyze"] = hosta_analyze
        cache["AnalyzedFunction"] = AnalyzedFunction
        cache["AnalyzedArgument"] = AnalyzedArgument
        cache["encode_function"] = encode_function
    except ImportError as e:
        print(f"[V5] Warning: Failed to import V4 analizer: {e}")
        
    try:
        from OpenHosta.core.meta_prompt import EMULATE_META_PROMPT, USER_CALL_META_PROMPT
        cache["EMULATE_META_PROMPT"] = EMULATE_META_PROMPT
        cache["USER_CALL_META_PROMPT"] = USER_CALL_META_PROMPT
    except ImportError as e:
        print(f"[V5] Warning: Failed to import V4 meta_prompt: {e}")

    try:
        from OpenHosta.guarded.resolver import type_returned_data
        cache["type_returned_data"] = type_returned_data
    except ImportError as e:
        print(f"[V5] Warning: Failed to import V4 resolver: {e}")

    _get_v4_imports._cache = cache
    return cache


# --------------------------------------------------------------------------- #
# V4 BRIDGE — Import des briques V4 sans copier de code                       #
# --------------------------------------------------------------------------- #

_srcdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src")
if _srcdir not in sys.path:
    sys.path.insert(0, _srcdir)

try:
    from OpenHosta.core.analizer import (
        hosta_analyze,
        encode_function,
        nice_type_name,
        AnalyzedArgument,
        AnalyzedFunction,
    )
    from OpenHosta.core.meta_prompt import (
        EMULATE_META_PROMPT,
        USER_CALL_META_PROMPT,
    )
    from OpenHosta.guarded.resolver import type_returned_data
    try:
        from OpenHosta.guarded.primitives import Guarded as V4_Guarded
        from OpenHosta.guarded.primitives import GuardedPrimitive as V4_GuardedPrimitive
    except ImportError:
        V4_Guarded = None
        V4_GuardedPrimitive = None
except ImportError:
    # If V4 is unavailable, auto_body will raise a clear error at call time
    hosta_analyze = None
    encode_function = None
    nice_type_name = None
    AnalyzedArgument = None
    AnalyzedFunction = None
    EMULATE_META_PROMPT = None
    USER_CALL_META_PROMPT = None
    type_returned_data = None
    V4_Guarded = None


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

    Nettoie tout le graphe de ses proxies Guarded (V5) et des primitives
    V4 (GuardedUtf8, GuardedInt...) en valeur native.
    """
    # -- V5 Guarded[T] --
    if _is_guarded(obj):
        return unguard(obj._value)

    # -- V4 GuardedPrimitive (GuardedUtf8, GuardedInt, etc.) --
    # Ces classes héritent du type natif ET de GuardedPrimitive.
    if V4_GuardedPrimitive is not None and isinstance(obj, V4_GuardedPrimitive):

        # 1) Dataclass wrapper (GuardedDataclassWrapper)
        #    V4 creates a new class that inherits GuardedPrimitive, ProxyWrapper
        #    but NOT the original dataclass. _type_py holds the original class.
        if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
            _type_py = getattr(type(obj), "_type_py", None)
            if _type_py is not None and dataclasses.is_dataclass(_type_py):
                # Reconstruct the original dataclass with unguarded fields
                kwargs = {}
                for fld in dataclasses.fields(obj):
                    kwargs[fld.name] = unguard(getattr(obj, fld.name))
                return _type_py(**kwargs)

        # 2) Scalar primitives (GuardedUtf8 inherits str, GuardedInt inherits int...)
        for base in type(obj).__mro__:
            if base in (str, int, float, bool, list, dict, tuple, set, bytes):
                return base(obj)
        return obj

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
# 5.5 RESPONSE CLEANER — Extract code blocks from LLM markdown                #
# --------------------------------------------------------------------------- #

def _extract_code_block(raw: str, expected_type: Any = None) -> str:
    """Extract the code block from an LLM response.

    LLMs often wrap JSON/Python in ```python ... ``` fences and add
    surrounding explanations. This strips the noise and returns the
    best candidate block, or the original string if no block is found.
    """
    # Match all ```python ... ``` or ``` ... ``` or ```json ... ```
    blocks = re.findall(r"```(?:python|json|py)?\n?(.*?)\n?```", raw, re.DOTALL)
    if blocks:
        # Prefer the last block, but fall back if it looks like a function call
        best = blocks[-1].strip()
        # If it starts with a function call pattern, try earlier blocks
        if re.match(r"^\w+\(", best):
            for b in reversed(blocks[:-1]):
                candidate = b.strip()
                if not re.match(r"^\w+\(", candidate):
                    best = candidate
                    break
        return best

    # No code fences — try to extract the last constructor or JSON dict from
    # prose like: "identify_person(x) -> Person(name='Alice', age=30)"
    # Strategy: find the last occurrence of ClassName(...) or { ... }
    m = re.search(r"(\w+\([^)]*(?:\([^)]*\)[^)]*)*\)|\{[^{}]*\})$", raw.strip(), re.DOTALL)
    if m:
        # Extract the first match if it looks like a valid constructor or JSON
        candidate = m.group(1).strip()
        # Avoid matching simple function calls like identify_person(text)
        if expected_type is not None:
            cls_name = getattr(expected_type, "__name__", "")
            if cls_name and candidate.startswith(cls_name + "("):
                return candidate
    return raw.strip()


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

        Pipeline :
          1. Analyser la signature via hosta_analyze() (brique V4).
          2. Encoder les données via encode_function() (brique V4).
          3. Construire les prompts system/user via les Jinja2 templates V4.
          4. Appeler le modèle LLM via HTTP (OpenAI-compatible /chat/completions).
          5. Parser + caster la réponse via type_returned_data() (brique V4).
          6. Retourner Guarded[T] ou valeur native selon l'annotation.

        Accepte optionnellement un GuardConfig en premier argument.
        """
        config = None
        if args and not callable(args[0]):
            config = args[0]
            args = args[1:]

        # Gate : V4 must be importable
        if hosta_analyze is None:
            def _v4_missing_error(_func: F) -> F:
                def _fail(*_a: Any, **_kw: Any) -> Any:
                    raise RuntimeError(
                        "[auto_body] OpenHosta V4 is not installed or not importable. "
                        "Ensure src/OpenHosta is present and jinja2 is installed."
                    )
                return cast(F, _fail)
            if len(args) == 1 and not kwargs and callable(args[0]):
                return _v4_missing_error(args[0])
            return _v4_missing_error

        model_ref = self  # capture self for use inside closures

        def decorator(func: F) -> F:
            # -----------------------------------------------------------------
            # Extraire le GuardConfig de l'annotation de retour, si présent
            # -----------------------------------------------------------------
            sig = inspect.signature(func)
            return_annotation = sig.return_annotation

            annotation_config: GuardConfig | None = None
            raw_return_type: Any = return_annotation

            if return_annotation is not inspect.Parameter.empty:
                origin = get_origin(return_annotation)
                if origin is typing.Annotated:
                    ann_args = get_args(return_annotation)
                    if len(ann_args) >= 2:
                        raw_return_type = ann_args[0]
                        if isinstance(ann_args[1], GuardConfig):
                            annotation_config = ann_args[1]

            # La config décorateur a priorité, sinon la config annotation
            effective_config: GuardConfig | None = config if config is not None else annotation_config

            # Détecter le type inner du return (unwrap Guarded[T] si nécessaire)
            inner_return_type: Any = raw_return_type
            is_guarded_annotation = False

            if raw_return_type is not inspect.Parameter.empty:
                # Check for Guarded[T] — peut être le V4 ou le V5
                origin = get_origin(raw_return_type)
                if origin is Guarded:
                    is_guarded_annotation = True
                    inner_return_type = get_args(raw_return_type)[0]
                else:
                    # Check against V4 Guarded
                    if V4_Guarded is not None and origin is V4_Guarded:
                        is_guarded_annotation = True
                        inner_return_type = get_args(raw_return_type)[0]

            analyse = hosta_analyze(function_pointer=func)

            if analyse.is_generator:
                # TODO: Phase 3 — Streaming/generator support
                def _gen_not_impl(*_f_args: Any, **_f_kwargs: Any) -> Any:
                    raise NotImplementedError(
                        "[auto_body] Generator functions are not yet supported (Phase 3)."
                        "Use a non-generator return type for now."
                    )
                wrapped = cast(F, cast(Callable, _gen_not_impl))
                # Preserve original metadata
                functools.update_wrapper(_gen_not_impl, func)
                return wrapped

            if analyse.is_async:
                # -----------------------------------------------------------------
                # ASYNC WRAPPER — utilise asyncio.to_thread pour l'HTTP blocking
                # -----------------------------------------------------------------
                model_ref = self

                async def async_wrapper(*f_args: Any, **f_kwargs: Any) -> Any:
                    messages = model_ref._auto_body_prepare(
                        func, analyse, f_args, f_kwargs, inner_return_type,
                    )
                    import time
                    start_ms = time.monotonic()
                    raw_content = await asyncio.to_thread(
                        model_ref._llm_call_sync, messages,
                    )
                    end_ms = time.monotonic()
                    elapsed_ms = round((end_ms - start_ms) * 1000, 1)

                    return model_ref._auto_body_result(
                        raw_content, elapsed_ms,
                        inner_return_type, is_guarded_annotation, self.model,
                    )

                functools.update_wrapper(async_wrapper, func)
                return cast(F, async_wrapper)
            else:
                # -----------------------------------------------------------------
                # SYNC WRAPPER
                # -----------------------------------------------------------------
                model_ref = self

                def sync_wrapper(*f_args: Any, **f_kwargs: Any) -> Any:
                    messages = model_ref._auto_body_prepare(
                        func, analyse, f_args, f_kwargs, inner_return_type,
                    )
                    import time
                    start_ms = time.monotonic()
                    raw_content = model_ref._llm_call_sync(messages)
                    end_ms = time.monotonic()
                    elapsed_ms = round((end_ms - start_ms) * 1000, 1)

                    return model_ref._auto_body_result(
                        raw_content, elapsed_ms,
                        inner_return_type, is_guarded_annotation, self.model,
                    )

                functools.update_wrapper(sync_wrapper, func)
                return cast(F, sync_wrapper)

        if len(args) == 1 and not kwargs and callable(args[0]):
            return decorator(args[0])
        return decorator

    # --------------------------------------------------------------------- #
    # Internal engine — préparation prompts (pure, réutilisable sync/async) #
    # --------------------------------------------------------------------- #

    def _auto_body_prepare(
        self,
        func: Callable,
        analyse: AnalyzedFunction,
        f_args: tuple,
        f_kwargs: dict,
        inner_return_type: Any,
    ) -> list[dict]:
        """Phase 1-3 : analyser, encoder, construire les messages.

        Retourne la liste de messages OpenAI-compatible prête à être envoyée.
        """
        # -- 1. Remplir les valeurs effectives dans analyse.args --
        sig = inspect.signature(func)
        bound = sig.bind_partial(*f_args, **f_kwargs)
        bound.apply_defaults()

        filled_args: list[AnalyzedArgument] = []
        existing_args_map = {a.name: a.type for a in analyse.args}
        for name, value in bound.arguments.items():
            arg_type = existing_args_map.get(name, type(value))
            filled_args.append(AnalyzedArgument(
                name=name,
                value=value,
                type=arg_type,
            ))

        live_analyse = AnalyzedFunction(
            name=analyse.name,
            args=filled_args,
            type=inner_return_type,  # Use inner type — LLM sees `-> Person`, not `-> Guarded[Person]`
            doc=analyse.doc,
            is_async=analyse.is_async,
            is_generator=analyse.is_generator,
            item_type=analyse.item_type,
        )

        # -- 2. Encoder les données --
        encoded = encode_function(live_analyse)

        # -- 3. Construire les prompts system/user --
        system_prompt = EMULATE_META_PROMPT.render(encoded)
        user_prompt = USER_CALL_META_PROMPT.render(encoded)

        # Tri-Modal : enrichir si type retour complexe (dataclass, struct, collection)
        if inner_return_type not in (str, int, float, bool, type(None), inspect.Parameter.empty) \
           and inner_return_type is not None and inner_return_type is not inspect._empty:

            is_complex = False
            if dataclasses.is_dataclass(inner_return_type):
                is_complex = True
            else:
                origin = get_origin(inner_return_type)
                typing_origins = (
                    list, dict, set, tuple,
                    typing.List, typing.Dict, typing.Set, typing.Tuple,
                    typing.Sequence, typing.Mapping, typing.Iterable,
                )
                if origin in typing_origins:
                    is_complex = True
                # Pydantic detection
                if hasattr(inner_return_type, "model_fields"):
                    is_complex = True

            if is_complex:
                type_def_md = guarded_to_markdown(inner_return_type)
                # Force JSON mode for complex types — the V4 resolver parses JSON dicts
                # into dataclasses reliably, whereas "free Python" leads to formats like
                # Eve(28,Berlin) that the resolver cannot handle.
                encoded["use_json_mode"] = True
                encoded["function_return_as_json_schema"] = json.dumps(
                    _field_to_json_schema(inner_return_type), indent=2
                )

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

    # --------------------------------------------------------------------- #
    # Post-traitement — casting + Guarded (pure, réutilisable sync/async)    #
    # --------------------------------------------------------------------- #

    def _auto_body_result(
        self,
        raw_content: str,
        elapsed_ms: float,
        inner_return_type: Any,
        is_guarded_annotation: bool,
        model_name: str,
    ) -> Any:
        """Phase 5-6 : caster la réponse, construire metadata, retourner."""
        # -- 4bis. Strip markdown code fences around the raw response --
        cleaned_content = _extract_code_block(raw_content)

        # -- 5. Parser + caster --
        cast_result = type_returned_data(cleaned_content, inner_return_type)

        # -- 6. Construire metadata + retourner --
        metadata = GuardMetadata(
            uncertainty=0.05,  # Heuristic baseline — to be refined with logprobs
            time_consumed=elapsed_ms,
            llm_logs=[{
                "model": model_name,
                "raw_response": raw_content[:200],
            }],
        )

        if is_guarded_annotation:
            # If the inner value is already a V4 GuardedPrimitive,
            # re-wrap it in our V5 Guarded[T] (the V4 one has different behavior)
            inner = (
                unguard(cast_result)
                if V4_GuardedPrimitive is not None and isinstance(cast_result, V4_GuardedPrimitive)
                else cast_result
            )
            return Guarded(inner, metadata)
        else:
            # Return native value — unwrap any V4 GuardedPrimitive wrappers
            if V4_GuardedPrimitive is not None and isinstance(cast_result, V4_GuardedPrimitive):
                return unguard(cast_result)
            return cast_result

    # --------------------------------------------------------------------- #
    # LLM HTTP call — standalone, no V4 pipeline dependency                 #
    # --------------------------------------------------------------------- #

    def _llm_call_sync(self, messages: list[dict]) -> str:
        """Appel HTTP direct au LLM via une API OpenAI-compatible.

        Utilise urllib stdlib (zéro dépendance externe) pour POST sur
        <base_url>/chat/completions et retourne le contenu brut du message.
        """
        api_url = self.base_url.rstrip("/") + "/chat/completions"

        body = json.dumps({
            "model": self.model,
            "messages": messages,
        }).encode("utf-8")

        req = urllib.request.Request(
            api_url,
            data=body,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
                content = payload["choices"][0]["message"]["content"]
                return content.strip() if content else ""
        except urllib.error.URLError as exc:
            raise RuntimeError(
                f"[auto_body] Failed to reach LLM at {api_url}: {exc.reason}"
            ) from exc
        except (KeyError, IndexError, json.JSONDecodeError) as exc:
            raise RuntimeError(
                f"[auto_body] Unexpected LLM response format: {exc}"
            ) from exc

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
        model=os.environ.get("HOSTA_MODEL", "qwen3.5:4b"),
        base_url=os.environ.get("HOSTA_BASE_URL", "http://192.168.1.188:11434/v1"),
        capabilities={"logprobs", "streaming"},
    )
