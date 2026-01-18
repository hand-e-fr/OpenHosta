# src/OpenHosta/semantics/primitives.py

from abc import ABC, abstractmethod
from typing import Any, Tuple, ClassVar, Dict, Optional
import math

# Imports internes (Moteur & Incertitude)
from ..core.uncertainty import CastingResult
from ..core.engine import iterate_cast_type, get_embedding, check_equality_llm

class GuardedPrimitive(ABC):
    """
    Mixin abstrait qui implémente le pipeline de validation 'OpenHosta'.
    Il transforme une entrée arbitraire en type natif via :
    1. Check Natif (Instant)
    2. Heuristique (Rapide)
    3. LLM (Intelligent & Coûteux)
    """

    # --- Configuration par défaut ---
    CONFIDENCE_THRESHOLD: float = 0.8
    MAX_RETRIES: int = 3

    # --- Interface Déclarative (À définir par les enfants) ---
    _type_en: ClassVar[str] = NotImplemented
    _type_py: ClassVar[str] = NotImplemented
    _type_json: ClassVar[Dict[str, Any]] = NotImplemented

    def __new__(cls, value: Any, description: str = ""):
        """
        Le constructeur 'Magique'. Il ne crée l'objet que si le pipeline réussit.
        """
        # 1. Lancement du Pipeline (Template Method)
        result = cls.attempt(value, description)

        # 2. Gestion de l'échec
        if not result.is_success:
            raise ValueError(
                f"OpenHosta Casting Failed for type '{cls.__name__}'.\n"
                f"Input: '{value}'\n"
                f"Error: {result.error_message}"
            )

        # 3. Création de l'instance native (int, str, list...)
        # Note: cls doit hériter d'un type natif (ex: class SemanticInt(int, GuardedPrimitive))
        try:
            instance = super().__new__(cls, result.value)
        except TypeError:
            # Fallback pour les types mutables (list, dict) qui utilisent __init__
            instance = super().__new__(cls)

        # 4. Injection des Métadonnées (Shadow Attributes)
        instance._confidence = result.confidence
        instance._source = result.source
        instance._description = description
        
        return instance

    @property
    def confidence(self) -> float:
        """Score de confiance de la conversion (0.0 à 1.0)."""
        return getattr(self, '_confidence', 1.0)

    @property
    def source(self) -> str:
        """Origine de la donnée : 'native', 'heuristic', ou 'llm'."""
        return getattr(self, '_source', 'unknown')

    @classmethod
    def attempt(cls, value: Any, description: str = "") -> CastingResult:
        """
        Le SQUELETTE de l'algorithme (Template Method).
        Orchestre les tentatives du moins coûteux au plus coûteux.
        """
        
        # --- ÉTAPE 1 : Test Natif (Coût: 0) ---
        is_valid, native_val = cls._parse_native(value)
        if is_valid:
            return CastingResult(True, native_val, 1.0, 'native')

        # --- ÉTAPE 2 : Heuristique (Coût: Epsilon) ---
        is_valid, heuristic_val = cls._parse_heuristic(value)
        if is_valid:
            return CastingResult(True, heuristic_val, 0.95, 'heuristic')

        # --- ÉTAPE 3 : Moteur LLM (Coût: $$$) ---
        # On délègue la complexité de l'appel API au moteur 'core'
        # Le moteur lit cls._type_* pour construire le prompt.
        iterator = iterate_cast_type(value, target_cls=cls, user_desc=description)
        
        retries = 0
        for candidate_str, uncertainty in iterator:
            confidence = 1.0 - uncertainty
            
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

                if is_valid_candidate and confidence >= cls.CONFIDENCE_THRESHOLD:
                    return CastingResult(True, final_val, confidence, 'llm')

            except Exception:
                pass # Le candidat du LLM était invalide, on continue/retry
            
            retries += 1
            if retries >= cls.MAX_RETRIES:
                break
                
        # --- ÉTAPE 4 : Échec ---
        return CastingResult(False, None, 0.0, 'failed', "Confidence too low or parse error")

    # --- Hooks Abstraits (À implémenter par SemanticInt, SemanticStr...) ---
    
    @classmethod
    @abstractmethod
    def _parse_native(cls, value: Any) -> Tuple[bool, Any]:
        """Retourne (True, val) si value est DÉJÀ valide."""
        pass

    @classmethod
    @abstractmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[bool, Any]:
        """Tentative de nettoyage déterministe (Regex, Strip...)."""
        pass


class SemanticType(GuardedPrimitive):
    """
    Classe de base pour les types sémantiques riches.
    Ajoute la capacité de COMPARAISON (Embeddings) au-dessus de la Validation.
    
    Usage :
    class Animal(SemanticType):
        _type_en = "an animal"
        semantic_tolerance = 0.15
    """

    # --- Configuration Sémantique ---
    # Tolérance par défaut (correspond à Tolerance.FLEXIBLE)
    semantic_tolerance: float = 0.15
    
    # Seuil en dessous duquel on bascule sur le LLM (hybride)
    HYBRID_SWITCH_TOLERANCE: float = 0.05

    def __init__(self, value: Any, description: str = ""):
        # Note: __new__ a déjà fait le travail de casting/instanciation.
        # __init__ sert ici à initialiser le cache sémantique.
        # Pour les types immuables (str, int), ceci ne sera appelé qu'après création.
        self._vector = None

    @property
    def vector(self):
        """Lazy loading du vecteur d'embedding."""
        if self._vector is None:
            # Appel au moteur d'embedding (core/engine.py)
            # On vectorise la représentation string de la valeur
            self._vector = get_embedding(str(self))
        return self._vector

    def __eq__(self, other: Any) -> bool:
        """
        L'opérateur magique du 'Flou Maîtrisé'.
        """
        # 1. Égalité stricte (Python natif) - Optimisation
        if super().__eq__(other):
            return True

        # 2. Gestion de la stratégie Hybride
        # Si l'utilisateur demande une précision chirurgicale, on utilise le LLM
        if self.semantic_tolerance < self.HYBRID_SWITCH_TOLERANCE:
            return self._check_equality_llm(other)

        # 3. Comparaison Vectorielle (Embeddings)
        return self._check_equality_vector(other)

    def _check_equality_llm(self, other: Any) -> bool:
        """Appel au LLM pour valider l'équivalence sémantique fine."""
        # On délègue au moteur core
        return check_equality_llm(
            value_a=str(self),
            value_b=str(other),
            context=self._description or self._type_en,
            threshold=1.0 - self.semantic_tolerance # Conversion tolérance -> confiance
        )

    def _check_equality_vector(self, other: Any) -> bool:
        """Comparaison via Cosine Similarity."""
        # On a besoin du vecteur de l'autre objet
        other_vector = None
        
        if isinstance(other, SemanticType):
            other_vector = other.vector
        elif isinstance(other, str):
            # On vectorise la string brute à la volée
            other_vector = get_embedding(other)
        else:
            # On ne compare pas des types incompatibles (ex: Animal vs 42)
            return False

        if other_vector is None:
            return False

        # Calcul manuel de la similarité cosinus (évite dépendance numpy lourde ici si souhaité)
        # Mais supposons une fonction utilitaire dans core
        similarity = self._cosine_similarity(self.vector, other_vector)
        
        # Mapping Tolérance -> Seuil
        threshold = self._map_tolerance_to_threshold(self.semantic_tolerance)
        
        return similarity >= threshold

    def _map_tolerance_to_threshold(self, user_tolerance: float) -> float:
        """
        Convertit la tolérance utilisateur (0.0 - 1.0) en seuil Cosinus réel.
        Basé sur une calibration empirique (ex: text-embedding-3).
        """
        # Modèle linéaire simplifié sur la plage utile [0.7, 1.0]
        # Tolérance 0.0 -> Seuil 0.99
        # Tolérance 0.5 -> Seuil 0.80
        # Tolérance 1.0 -> Seuil 0.70
        
        MIN_USEFUL_SIMILARITY = 0.7
        MAX_SIMILARITY = 0.99
        
        # Formule de mapping inverse
        # Si tolerance augmente, threshold diminue
        range_sim = MAX_SIMILARITY - MIN_USEFUL_SIMILARITY
        threshold = MAX_SIMILARITY - (user_tolerance * range_sim)
        
        return max(MIN_USEFUL_SIMILARITY, threshold)

    @staticmethod
    def _cosine_similarity(vec_a, vec_b) -> float:
        """Calcul basique de similarité cosinus (Produit scalaire / Normes)."""
        # Supposons que vec_a et vec_b sont des listes de floats
        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot_product / (norm_a * norm_b)

    def __hash__(self):
        """
        Sécurité : On interdit le hachage car l'égalité est floue.
        Cela empêche d'utiliser SemanticType dans un set() ou dict() natif.
        """
        raise TypeError(
            f"'{self.__class__.__name__}' is not hashable because it uses semantic equality. "
            "Use 'SemanticSet' or 'SemanticDict' instead of native collections."
        )