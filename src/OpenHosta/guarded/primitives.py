# src/OpenHosta/semantics/primitives.py

from abc import ABC, abstractmethod
from typing import Any, Tuple, ClassVar, Dict, Optional
import math

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
    _type_knowledge: ClassVar[str] = NotImplemented
    _tolerance: ClassVar[Tolerance] = Tolerance.TYPE_COMPLIANT

    _uncertainty: ClassVar[UncertaintyLevel] = NotImplemented
    _input: ClassVar[Any] = NotImplemented
    _abstraction_level = ClassVar[AbstractionLevel]
    
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
        instance = super().__new__(cls, result.python_value)

        # 4. Injection des Métadonnées
        instance._input = value
        instance._uncertainty = result.uncertainty
        instance._abstraction_level = result.abstraction
        instance._python_value = result.python_value
        
        return instance

    @property
    def uncertainty(self) -> UncertaintyLevel:
        """Score de confiance de la conversion (0.0 à 1.0)."""
        return getattr(self, '_uncertainty', 1.0)

    @property
    def abstraction_level(self) -> str:
        """Niveau d'abstracton utilisé pour la conversion (native, heuristic, vectorial, llm)."""
        return getattr(self, '_abstraction_level', 'unknown')

    def unwrap(self):
        """Méthode utilitaire pour récupérer la valeur."""
        return getattr(self, "_python_value", None)

    @classmethod
    def attempt(cls, value: Any, tolerance: Tolerance = None) -> CastingResult:
        """
        Le SQUELETTE de l'algorithme (Template Method).
        Orchestre les tentatives du moins coûteux au plus coûteux.
        """
        
        if tolerance is None:
            tolerance = cls._tolerance
            
        # At each layer we have a chance to reduce uncertainty
        
        uncertainty, cleaned_native_val = cls._parse_native(value)
        if uncertainty <= tolerance:
            return CastingResult(True, cleaned_native_val, uncertainty, 'native', value, cls._type_py)

        uncertainty, cleaned_heuristic_val = cls._parse_heuristic(cleaned_native_val)
        if uncertainty <= tolerance:
            return CastingResult(True, cleaned_heuristic_val, uncertainty, 'heuristic', value, cls._type_py)

        uncertainty, cleaned_semantic_value = cls._parse_semantic(cleaned_heuristic_val)
        if uncertainty <= tolerance:
            return CastingResult(True, cleaned_semantic_value, uncertainty, 'semantic', value, cls._type_py)

        uncertainty, cleaned_knowledge_value = cls._parse_knowledge(cleaned_semantic_value)
        if uncertainty <= tolerance:
            return CastingResult(True, cleaned_knowledge_value, uncertainty, 'knowledge', value, cls._type_py)

        return CastingResult(False, None, Tolerance.ANYTHING, 'failed', value, cls._type_py)
    
    # --- Hooks Abstraits (À implémenter par SemanticInt, SemanticUtf8...) ---
    
    @classmethod
    def _parse_native(cls, value: Any) -> Tuple[UncertaintyLevel, Any]:
        """Retourne (1.0, val) si value est DÉJÀ valide."""
        if type(value) == cls._type_py:
            return UncertaintyLevel(Tolerance.STRICT), value
        
        return UncertaintyLevel(Tolerance.ANYTHING), value

    @classmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[UncertaintyLevel, Any]:
        """Tentative de nettoyage déterministe (Regex, Strip...).
        
        Retourne (uncertainty, cleaned_val) où uncertainty ∈ [0, 1]."""
        
        value = str(value)
        
        try:
            value = cls._type_py(value)
            return UncertaintyLevel(Tolerance.TYPE_COMPLIANT), value
        except Exception:
            pass
        
        return UncertaintyLevel(Tolerance.ANYTHING), value
        
    
    @classmethod
    def _parse_semantic(cls, value: Any) -> Tuple[UncertaintyLevel, Any]:
        """
        Tentative de nettoyage via LLM.
        """
        return UncertaintyLevel(Tolerance.ANYTHING), value

        
    @classmethod
    def _parse_knowledge(cls, value: Any) -> Tuple[UncertaintyLevel, Any]:
        """
        Tentative de netoyage par une base de connaissance.
        """
        return UncertaintyLevel(Tolerance.ANYTHING), value


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
