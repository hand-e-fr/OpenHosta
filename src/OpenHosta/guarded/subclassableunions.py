# ==============================================================================
# UNION TYPE - Choix entre plusieurs types
# ==============================================================================

from typing import Any, Tuple, Optional
from .primitives import GuardedPrimitive, UncertaintyLevel, CastingResult
from .constants import Tolerance


class GuardedUnion(GuardedPrimitive):
    """
    Type pour valider une union de plusieurs types Guarded.
    Tente de convertir l'entrée vers chacun des types spécifiés, dans l'ordre.
    """
    
    _types: tuple = ()  # Liste des types Guarded à tenter
    
    @classmethod
    def attempt(cls, value: Any, tolerance: Tolerance = None) -> CastingResult:
        """
        Surcharge de attempt pour essayer chaque type de l'union.
        """
        if tolerance is None:
            tolerance = cls._tolerance
            
        best_result = None
        winning_type = None
        
        for guarded_type in cls._types:
            # Tenter la conversion avec ce type
            result = guarded_type.attempt(value, tolerance=tolerance)
            
            if result.success:
                # Si on a un match parfait (STRICT), on s'arrête
                if result.uncertainty <= Tolerance.STRICT:
                    # On attache le type gagnant au résultat pour que __new__ sache quoi instancier
                    result.python_type = guarded_type
                    return result
                
                # Sinon on garde le meilleur résultat trouvé jusqu'ici
                if best_result is None or result.uncertainty < best_result.uncertainty:
                    best_result = result
                    winning_type = guarded_type
        
        if best_result:
            best_result.python_type = winning_type
            return best_result
            
        # Échec total
        return CastingResult(False, None, Tolerance.ANYTHING, 'failed', value, cls)

    def __new__(cls, value: Any, tolerance: Tolerance = None):
        """
        Pour une Union, on ne veut pas une instance de GuardedUnion,
        mais une instance du type qui a réussi la conversion.
        """
        result = cls.attempt(value, tolerance=tolerance)
        
        if not result.success:
            raise ValueError(
                f"OpenHosta Casting Failed for Union type '{cls.__name__}'.\n"
                f"Input: '{value}'\n"
                f"Error: {result.error_message}"
            )
        
        # Instancier le type gagnant
        winning_type = result.python_type
        
        # Si le type gagnant est une GuardedPrimitive, on l'appelle
        # (il passera par son propre __new__ et fera son propre casting)
        return winning_type(value)


def guarded_union(*guarded_types):
    """
    Factory pour créer un type GuardedUnion.
    
    Args:
        *guarded_types: Les types (Standards ou Guarded) autorisés
        
    Returns:
        Une classe GuardedUnion configurée
    """
    # Résoudre les types pour s'assurer qu'ils ont .attempt()
    from .resolver import TypeResolver
    resolved_types = tuple(TypeResolver.resolve(t) for t in guarded_types)
    
    class DynamicUnion(GuardedUnion):
        _types = resolved_types
        _type_en = f"one of: {', '.join(t._type_en if hasattr(t, '_type_en') else str(t) for t in resolved_types)}"
        _type_py = Any
        _type_json = {
            "anyOf": [t._type_json if hasattr(t, '_type_json') else {"type": "string"} for t in resolved_types]
        }
        
    DynamicUnion.__name__ = f"Union[{', '.join(t.__name__ if hasattr(t, '__name__') else str(t) for t in resolved_types)}]"
    return DynamicUnion
