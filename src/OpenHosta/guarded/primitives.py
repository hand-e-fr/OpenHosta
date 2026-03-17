# src/OpenHosta/guarded/primitives.py
"""
Module core du système de types Guarded.

Le système Guarded implémente un pipeline de validation à plusieurs niveaux
qui transforme des entrées arbitraires en types Python natifs avec métadonnées
de confiance et de traçabilité.

Pipeline de validation (du plus rapide au plus lent) :
1. **Native**    : Vérification de type direct (isinstance)
                   Coût: O(1), Uncertainty: 0.0 (STRICT)
                   
2. **Heuristic** : Nettoyage déterministe (regex, strip, cast)
                   Coût: O(n), Uncertainty: 0.05-0.15
                   
3. **Semantic**  : Conversion via LLM (non implémenté)
                   Coût: ~1s, Uncertainty: 0.15-0.30
                   
4. **Knowledge** : Consultation de base de connaissances
                   Coût: Variable, Uncertainty: 0.30+

Architecture :
    GuardedPrimitive (ABC)
    ├── Héritage Direct (types subclassables)
    │   ├── GuardedInt(int)
    │   ├── GuardedUtf8(str)
    │   ├── GuardedFloat(float)
    │   ├── GuardedList(list)
    │   ├── GuardedDict(dict)
    │   └── ...
    │
    └── ProxyWrapper (types non-subclassables)
        ├── GuardedBool
        ├── GuardedNone
        ├── GuardedRange
        └── GuardedEnum

Exemple d'utilisation :
    >>> from OpenHosta.guarded import GuardedInt
    >>> age = GuardedInt("42 ans")  # Heuristic cleaning
    >>> age
    42
    >>> age.uncertainty
    0.15
    >>> age.abstraction_level
    'heuristic'
    >>> age + 10
    52

Création de types personnalisés :
    >>> class CorporateEmail(GuardedUtf8):
    ...     _type_en = "a corporate email address"
    ...     _tolerance = Tolerance.PRECISE
    ...     
    ...     @classmethod
    ...     def _parse_heuristic(cls, value):
    ...         value = str(value).strip().lower()
    ...         if '@company.com' not in value:
    ...             return UncertaintyLevel(Tolerance.ANYTHING), value, "Invalid domain"
    ...         return UncertaintyLevel(Tolerance.PRECISE), value, None
    
    >>> email = CorporateEmail("John.Doe@COMPANY.COM")
    >>> email
    'john.doe@company.com'
"""

from abc import ABC
from typing import Any, Tuple, ClassVar, Dict, Optional
from dataclasses import is_dataclass, fields


# Imports internes (Moteur & Incertitude)
from .constants import Tolerance

from dataclasses import dataclass
from typing import Any, Optional, Literal, Type

AbstractionLevel = Literal["native", "heuristic", "semantic", "knowledge"]
UncertaintyLevel = float

@dataclass
class CastingResult:
    is_success: bool
    
    python_value: Any    # La valeur convertie (ex: 23) ou None
    uncertainty: float   # Score de 0.0 à 1.0
    abstraction: AbstractionLevel 

    original_input: Any
    python_type: Optional[type] = None

    error_message: Optional[str] = None
    
class GuardedPrimitive(ABC):
    """
    Mixin abstrait qui implémente le pipeline de validation 'OpenHosta'.
    Il transforme une entrée arbitraire en type natif via :
    1. Check Natif (Instant)
    2. Heuristique (Rapide)
    3. LLM (Intelligent & Coûteux)
    4. Règles métier
    """
    # --- Interface Déclarative (À définir par les classes enfants) ---
    
    # 4 niveaux du plus générique au plus spécifique utilisables par les AbtractionLevels
    # - 1. Langage naturel (Anglais)
    # - 2. Type Python natif
    # - 3. Schéma JSON
    # - 4. Connaissances spécifiques (term métier dans une taxonomie ou un graph)
    
    _type_en: ClassVar[str] = NotImplemented
    _type_py: ClassVar[type] = NotImplemented
    _type_json: ClassVar[Dict[str, Any]] = NotImplemented
    _type_knowledge: ClassVar[Dict | Any] = NotImplemented
    _tolerance: ClassVar[Tolerance] = Tolerance.TYPE_COMPLIANT
    
    def __new__(cls, value: Any, tolerance: Tolerance = None):
        """
        Le constructeur 'Magique'. Il ne crée l'objet que si le analyseur sémantique réussit.
        """
                
        # 0. Use docsting as type definition in natural language (_type_en) if not defined 
        if cls._type_en == NotImplemented:
            cls._type_en = f"{cls.__doc__}"
        
        if tolerance is None:
            tolerance = cls._tolerance
            
        if cls._type_py is NotImplemented:
            for parent in cls.__mro__:
                if parent in (int, float, str, bool, list, dict, set, tuple):
                    cls._type_py = parent
                    break
            
        # 1. Lancement du Pipeline (Template Method)
        result = cls.attempt(value, tolerance=tolerance)

        # 2. Gestion de l'échec
        if not result.is_success:
            raise ValueError(
                f"OpenHosta Casting Failed for type '{cls.__name__}'.\n"
                f"Input: '{value}'\n"
                f"Error: {result.error_message}"
            )

        # 3. Création de l'instance native (int, str, list...)
        # Note: Pour les types mutables (list, dict, set), super().__new__(cls) 
        # retourne une instance vide. On la remplira dans __init__.
        try:
            instance = super().__new__(cls, result.python_value)
        except TypeError:
            # Certains types ne prennent pas d'arguments dans __new__
            instance = super().__new__(cls)

        # 4. Injection des Métadonnées
        instance._input = value
        instance._uncertainty = result.uncertainty
        instance._abstraction_level = result.abstraction
        instance._python_value = result.python_value
        
        return instance

    def __init__(self, value: Any, tolerance: Tolerance = None):
        """
        L'initialiseur est appelé après __new__.
        Pour les types mutables (list, dict, set), on doit s'assurer que
        l'instance est peuplée avec la valeur CONVERTIE, pas l'entrée originale.
        """
        # Si c'est un type mutable, on le vide et on le remplit avec la valeur convertie
        # Cela évite que list.__init__ soit appelé avec 'value' original
        python_value = getattr(self, "_python_value", None)
        
        if isinstance(self, list):
            if list(self) != python_value:
                self.clear()
                if python_value is not None:
                    self.extend(python_value)
        elif isinstance(self, dict):
            if dict(self) != python_value:
                self.clear()
                if python_value is not None:
                    self.update(python_value)
        elif isinstance(self, set):
            if set(self) != python_value:
                self.clear()
                if python_value is not None:
                    self.update(python_value)
        # Pour les types immuables (int, str...), __init__ ne fait rien car
        # la valeur a déjà été fixée dans __new__.

    @property
    def uncertainty(self) -> UncertaintyLevel:
        """Score de confiance de la conversion (0.0 à 1.0)."""
        return getattr(self, '_uncertainty', 1.0)

    @property
    def abstraction_level(self) -> str:
        """Niveau d'abstracton utilisé pour la conversion (native, heuristic, vectorial, llm)."""
        return getattr(self, '_abstraction_level', 'unknown')

    @staticmethod
    def _recursive_unwrap(value: Any) -> Any:
        """Déballe récursivement les objets Guarded et les conteneurs natifs."""
        if hasattr(value, "unwrap") and callable(value.unwrap):
            unwrapped = value.unwrap()
            if unwrapped is value:
                if is_dataclass(value):
                    return {
                        field.name: GuardedPrimitive._recursive_unwrap(getattr(value, field.name))
                        for field in fields(value)
                    }
                return value
            return GuardedPrimitive._recursive_unwrap(unwrapped)

        if is_dataclass(value):
            return {
                field.name: GuardedPrimitive._recursive_unwrap(getattr(value, field.name))
                for field in fields(value)
            }
        if isinstance(value, dict):
            return {
                GuardedPrimitive._recursive_unwrap(k): GuardedPrimitive._recursive_unwrap(v)
                for k, v in value.items()
            }
        if isinstance(value, list):
            return [GuardedPrimitive._recursive_unwrap(item) for item in value]
        if isinstance(value, tuple):
            return tuple(GuardedPrimitive._recursive_unwrap(item) for item in value)
        if isinstance(value, set):
            return {GuardedPrimitive._recursive_unwrap(item) for item in value}
        if isinstance(value, frozenset):
            return frozenset(GuardedPrimitive._recursive_unwrap(item) for item in value)
        return value

    def unwrap(self):
        """Méthode utilitaire pour récupérer la valeur native avec unwrapping récursif."""
        return self._recursive_unwrap(getattr(self, "_python_value", None))


    @classmethod
    def attempt(cls, value: Any, tolerance: Tolerance = None) -> CastingResult:
        """
        Le SQUELETTE de l'algorithme (Template Method).
        Orchestre les tentatives du moins coûteux au plus coûteux.
        """
        
        if tolerance is None:
            tolerance = cls._tolerance
            
        # At each layer we have a chance to reduce uncertainty
        
        uncertainty, cleaned_native_val, message = cls._parse_native(value)
        if uncertainty <= tolerance:
            return CastingResult(True, cleaned_native_val, uncertainty, 'native', value, cls._type_py, message)

        uncertainty, cleaned_heuristic_val, message = cls._parse_heuristic(cleaned_native_val)
        if uncertainty <= tolerance:
            return CastingResult(True, cleaned_heuristic_val, uncertainty, 'heuristic', value, cls._type_py, message)

        uncertainty, cleaned_semantic_value, message = cls._parse_semantic(cleaned_heuristic_val)
        if uncertainty <= tolerance:
            return CastingResult(True, cleaned_semantic_value, uncertainty, 'semantic', value, cls._type_py, message)

        uncertainty, cleaned_knowledge_value, message = cls._parse_knowledge(cleaned_semantic_value)
        if uncertainty <= tolerance:
            return CastingResult(True, cleaned_knowledge_value, uncertainty, 'knowledge', value, cls._type_py, message)

        return CastingResult(False, None, Tolerance.ANYTHING, 'failed', value, cls._type_py)
    
    # --- Hooks Abstraits (À implémenter par SemanticInt, SemanticUtf8...) ---
    
    @classmethod
    def _parse_native(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        """Retourne (uncertainty, value, error_message) si value est DÉJÀ valide."""
        if type(value) == cls._type_py:
            return UncertaintyLevel(Tolerance.STRICT), value, None
        
        return UncertaintyLevel(Tolerance.ANYTHING), value, None

    @classmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        """Tentative de nettoyage déterministe (Regex, Strip...).
        
        Retourne (uncertainty, cleaned_val, error_message) où uncertainty ∈ [0, 1]."""
        
        value = str(value)
        
        try:
            value = cls._type_py(value)
            return UncertaintyLevel(Tolerance.TYPE_COMPLIANT), value, None
        except Exception as e:
            pass
        
        return UncertaintyLevel(Tolerance.ANYTHING), value, None
        
    
    @classmethod
    def _parse_semantic(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        """
        Tentative de nettoyage via LLM.
        """
        return UncertaintyLevel(Tolerance.ANYTHING), value, None

        
    @classmethod
    def _parse_knowledge(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        """
        Tentative de nettoyage par une base de connaissance.
        """
        return UncertaintyLevel(Tolerance.ANYTHING), value, None


    ### Pydantic V2 Integration ###

    @classmethod
    def __get_pydantic_core_schema__(cls, _abstraction_level_type: Any, _handler: Any) -> Any:
        """
        Intègre GuardedPrimitive avec Pydantic V2.
        Permet la conversion automatique depuis n'importe quelle entrée.
        """
        from pydantic_core import core_schema
        
        return core_schema.with_info_before_validator_function(
            cls._pydantic_validate,
            core_schema.any_schema()
        )

    @classmethod
    def _pydantic_validate(cls, value: Any, _info: Any) -> Any:
        # Si c'est déjà une instance, on la garde
        if isinstance(value, cls):
            return value
        # Sinon on passe par le constructeur magique (pipeline)
        return cls(value)

    @classmethod
    def __get_pydantic_json_schema__(cls, _core_schema: Any, handler: Any) -> Any:
        """
        Retourne le schéma JSON du type pour Pydantic/OpenAPI.
        Utilise _type_json défini dans les sous-classes.
        """
        # On utilise le mapping _type_json s'il existe, sinon on délègue
        if cls._type_json is not NotImplemented:
            return cls._type_json
        return handler(_core_schema)

class ProxyWrapper:
    """
    Wrapper pour types Python non-subclassables (bool, range, memoryview, NoneType).
    
    Ces types ne peuvent pas être hérités directement, donc on crée un proxy
    qui stocke la valeur native dans `_python_value` et délègue les opérations.
    
    IMPORTANT: Les instances ne sont PAS des instances du type natif.
    Utilisez .unwrap() pour récupérer la valeur native si nécessaire.
    
    Exemple:
        b = GuardedBool("yes")
        isinstance(b, bool)  # ❌ False
        b.unwrap()           # ✅ True (vrai bool)
    """
    def __new__(cls, value):
        instance = super().__new__(cls)
        return instance
    
    def unwrap(self):
        """Retourne la valeur Python native avec unwrapping récursif."""
        return GuardedPrimitive._recursive_unwrap(getattr(self, "_python_value", None))


    def __getattr__(self, name):
        """Délègue l'accès aux attributs à la valeur native."""
        return getattr(self._python_value, name)
    
    # Délégation des opérations de comparaison
    def __eq__(self, other):
        if isinstance(other, ProxyWrapper):
            return self._python_value == other._python_value
        return self._python_value == other
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __hash__(self):
        return hash(self._python_value)
    
    def __repr__(self):
        return repr(self._python_value) if self._python_value is not None else "None"
    
    def __str__(self):
        return str(self._python_value) if self._python_value is not None else "None"

    def __call__(self, *args, **kwargs):
        """Délègue l'appel à la valeur native si elle est callable."""
        if callable(self._python_value):
            return self._python_value(*args, **kwargs)
        raise TypeError(f"'{type(self).__name__}' object is not callable")

    def __len__(self):
        return len(self._python_value)

    def __iter__(self):
        return iter(self._python_value)

    def __contains__(self, item):
        return item in self._python_value

    def __getitem__(self, key):
        return self._python_value[key]
