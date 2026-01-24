from typing import Type, ClassVar, Any

from ..guarded.constants import Tolerance
from ..guarded.primitives import GuardedPrimitive
from ..guarded.scalars import GuardedUtf8, GuardedInt, GuardedFloat, GuardedBool

def _create_semantic_attribute(
    description: str, 
    base_type: Type[GuardedPrimitive] | str | int | float | bool = GuardedUtf8, 
    tolerance: Tolerance = Tolerance.CREATIVE):
    """
    Factory function to create a semantic type from a GuardedPrimitive type.
    
    This enables the documentation pattern:
        SemanticAttribute("Tâche ménagère")
    
    Args:
        description: Semantic description for the type
        base_type: The base Python type (str, int, float, bool)
        tolerance: Semantic tolerance for comparisons
    
    Returns:
        A new class inheriting from the appropriate Semantic* type
    """
    
    # Map base types to their semantic equivalents
    type_mapping = {
        str: GuardedUtf8,
        int: GuardedInt,
        float: GuardedFloat,
        bool: GuardedBool,
    }
    
    if isinstance(base_type, type) and issubclass(base_type, GuardedPrimitive):
        semantic_base = base_type
    else:
        semantic_base = type_mapping.get(base_type, None)
    
    if semantic_base is None:
        raise TypeError(f"Unsupported base type: {base_type}. Supported: any child of GuardedPrimitive, str, int, float, bool")
    
    # Create a dynamic class with the description embedded
    class DynamicSemanticAttribute(semantic_base):
        semantic_tolerance = tolerance
        
    # Give it a meaningful name for debugging
    DynamicSemanticAttribute.__name__ = f"SemanticAttribute[{base_type.__name__}]"
    DynamicSemanticAttribute.__doc__ = f"{description}"
    DynamicSemanticAttribute.__qualname__ = f"SemanticAttribute[{base_type.__name__}]"
    
    return DynamicSemanticAttribute


class SemanticAttribute(GuardedPrimitive):
    """
    Classe de base pour les types sémantiques riches.
    Ajoute la capacité de COMPARAISON (Embeddings) au-dessus de la Validation des GuardedPrimitive.
    
    Usage:
    
        # Or as a base class:    
        class CleaningTask(SemanticAttribute):
            '''Tâche ménagère'''
            semantic_tolerance = 0.15
            
        class HomeLocation(SemanticAttribute):
            '''Lieu dans la maison'''
            semantic_tolerance = 0.20
            
        # You can also inherit from other SemanticAttribute:
        class CleaningAction(CleaningTask, HomeLocation):
            '''Action de ménage dans la maison'''
            semantic_tolerance = 0.15
           
    an_action = CleaningTask("Laver le sol")
    what_to_do_next = CleaningAction("passer la serpillère dans le salon")
    
    """
    semantic_tolerance: ClassVar[float] = 0.1  # Default similarity threshold
    # Seuil en dessous duquel on bascule sur le LLM (hybride)
    HYBRID_SWITCH_TOLERANCE: float = 0.05
    
    def __new__(cls, value):
        cls._superclasse = None # Définition de l'espace des conditions nécessaires pour l'attribut sémantique
        
        return super().__new__(value, tolerance)
    
    def __hash__(self):
        """
        Sécurité : On interdit le hachage car l'égalité est floue par défaut.
        Cela empêche d'utiliser ces types dans un set() ou dict() natif.
        """
        raise TypeError(
            f"'{self.__class__.__name__}' is not hashable because it uses fuzzy/semantic equality. "
            "Use 'SemanticSet' or 'SemanticDict' instead of native collections."
        )
    
    def __init__(self, value: Any):
        # Note: __new__ a déjà fait le travail de casting/instanciation.
        # __init__ sert ici à initialiser le cache sémantique.
        # Pour les types immuables (str, int), ceci ne sera appelé qu'après création.
        self._vector = None # Vecteur 

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
        
        if isinstance(other, SemanticAttribute):
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
        Cela empêche d'utiliser SemanticAttribute dans un set() ou dict() natif.
        """
        raise TypeError(
            f"'{self.__class__.__name__}' is not hashable because it uses semantic equality. "
            "Use 'SemanticSet' or 'SemanticDict' instead of native collections."
        )