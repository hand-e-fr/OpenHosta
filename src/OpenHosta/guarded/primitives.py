# src/OpenHosta/semantics/primitives.py

from abc import ABC, abstractmethod
from typing import Any, Tuple, ClassVar, Dict, Optional
import math

# Imports internes (Moteur & Incertitude)
from .constants import Tolerance

from dataclasses import dataclass
from typing import Any, Optional, Literal, Type

AbstractionLevel = Literal["native", "heuristic", "semantic", "knowledge"]

@dataclass
class CastingResult:
    is_success: bool
    
    uncertainty: float   # Score de 0.0 à 1.0
    abstraction: AbstractionLevel 

    original_input: Any
    python_value: Any          # La valeur convertie (ex: 23) ou None
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

    _uncertainty: ClassVar[float] = NotImplemented
    _tolerance: ClassVar[float] = NotImplemented
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
            cls._tolerance = Tolerance.CREATIVE
            
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
        
        return instance

    @property
    def uncertainty(self) -> float:
        """Score de confiance de la conversion (0.0 à 1.0)."""
        return getattr(self, '_uncertainty', 1.0)

    @property
    def abstraction_level(self) -> str:
        """Niveau d'abstracton utilisé pour la conversion (native, heuristic, vectorial, llm)."""
        return getattr(self, '_abstraction_level', 'unknown')

    @property
    def unwrap(self):
        """Méthode utilitaire pour récupérer la valeur ou lever l'erreur."""
        if not self.is_success:
            raise ValueError(self.error_message)
        return self.value


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
            return CastingResult(True, cleaned_native_val, uncertainty, 'native')

        uncertainty, cleaned_heuristic_val = cls._parse_heuristic(cleaned_native_val)
        if uncertainty <= tolerance:
            return CastingResult(True, cleaned_heuristic_val, uncertainty, 'heuristic')

        uncertainty, cleaned_semantic_value = cls._parse_semantic(cleaned_heuristic_val)
        if uncertainty <= tolerance:
            return CastingResult(True, cleaned_semantic_value, uncertainty, 'semantic')

        uncertainty, cleaned_knowledge_value = cls._parse_knowledge(cleaned_semantic_value)
        if uncertainty <= tolerance:
            return CastingResult(True, cleaned_knowledge_value, uncertainty, 'knowledge')

        return CastingResult(False, None, uncertainty, 'failed')
    
    # --- Hooks Abstraits (À implémenter par SemanticInt, SemanticUtf8...) ---
    
    @classmethod
    @abstractmethod
    def _parse_native(cls, value: Any) -> Tuple[float, Any]:
        """Retourne (1.0, val) si value est DÉJÀ valide."""
        pass

    @classmethod
    @abstractmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[float, Any]:
        """Tentative de nettoyage déterministe (Regex, Strip...).
        
        Retourne (uncertainty, cleaned_val) où uncertainty ∈ [0, 1]."""
        pass
    
    @classmethod
    @abstractmethod
    def _parse_semantic(cls, value: Any) -> Tuple[float, Any]:
        """
        Tentative de nettoyage via LLM.
        if not not implementes of no LLM available,
        
        return the value unchanged with 0.5 uncertainty
        """
        pass
        
    @classmethod
    @abstractmethod
    def _parse_knowledge(cls, value: Any) -> Tuple[float, Any]:
        """
        Tentative de netoyage par une base de connaissance.
        """
        pass


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

def del_me():
        MAX_RETRIES: int = 3

        # --- ÉTAPE 3 : Moteur LLM (Coût: $$$) ---
        # On délègue la complexité de l'appel API au moteur 'core'
        # Le moteur lit cls._type_* pour construire le prompt.
        iterator = iterate_cast_type(value, target_cls=cls, user_desc=description)
        
        retries = 0
        for candidate_str, uncertainty in iterator:
            uncertainty = 1.0 - uncertainty
            
            # Le LLM renvoie toujours du texte/json.
            # Il faut vérifier si ce texte est valide techniquement pour le type natif.
            # Ex: LLM renvoie "20", est-ce que int("20") marche via notre parser ?
            
            # On utilise _parse_native (ou une variante interne) pour valider le candidat
            # Attention : Le candidat peut être une string qu'il faut caster
            try:
                # On suppose que le moteur renvoie un candidat "brut" (ex: "20")
                # On tente de le parser comme une donnée native
                is_valid_candidate, final_val = cls._parse_native(candidate_str)
                
                # Si _parse_native échoue sur "20" (car il attend un int), 
                # on essaie de le caster via le constructeur du type parent si c'est une string
                if not is_valid_candidate and isinstance(candidate_str, str):
                    # Tentative de conversion basique (ex: int("20"))
                    # Cela dépend de l'implémentation spécifique des enfants, 
                    # mais ici on reste générique.
                     pass 
                     # Note: Pour une implémentation robuste, engine.py devrait renvoyer
                     # des données déjà typées (ex: json.loads), ou on utilise _parse_heuristic
                     # sur le retour du LLM.
                     is_valid_candidate, final_val = cls._parse_heuristic(candidate_str)

                if is_valid_candidate and uncertainty >= cls.CONFIDENCE_THRESHOLD:
                    return CastingResult(True, final_val, uncertainty, 'llm')

            except Exception:
                pass # Le candidat du LLM était invalide, on continue/retry
            
            retries += 1
            if retries >= cls.MAX_RETRIES:
                break
                
        # --- ÉTAPE 4 : Échec ---
        return CastingResult(False, None, 0.0, 'failed', "Confidence too low or parse error")

