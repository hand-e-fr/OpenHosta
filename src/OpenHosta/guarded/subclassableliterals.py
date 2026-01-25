# ==============================================================================
# LITERAL TYPE - Validation stricte de valeurs littérales
# ==============================================================================

from typing import Any, Tuple, Optional
from .primitives import UncertaintyLevel
from .constants import Tolerance
from .subclassablescalars import GuardedUtf8, GuardedInt, GuardedFloat


def guarded_literal(*values):
    """
    Factory pour créer dynamiquement un GuardedLiteral avec des valeurs spécifiques.
    
    Cette fonction crée une classe qui valide que la valeur est l'une des valeurs littérales autorisées.
    Elle délègue au type Guarded approprié selon le type des valeurs.
    
    Args:
        *values: Les valeurs littérales autorisées
    
    Returns:
        Une classe GuardedPrimitive configurée pour valider les valeurs littérales
    
    Example:
        >>> from typing import Literal
        >>> ColorLiteral = guarded_literal("red", "green", "blue")
        >>> color = ColorLiteral("red")
        >>> print(color)  # "red"
        
        >>> # Via TypeResolver
        >>> from OpenHosta.guarded.resolver import TypeResolver
        >>> StatusType = TypeResolver.resolve(Literal["pending", "active"])
        >>> status = StatusType("pending")
    """
    if not values:
        # Pas de valeurs, retourner GuardedUtf8 par défaut
        return GuardedUtf8
    
    # Déterminer le type de base selon le type des valeurs
    first_type = type(values[0])
    
    if all(isinstance(v, str) for v in values):
        base_class = GuardedUtf8
    elif all(isinstance(v, int) and not isinstance(v, bool) for v in values):
        base_class = GuardedInt
    elif all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in values):
        base_class = GuardedFloat
    else:
        # Type mixte ou non supporté, utiliser GuardedUtf8
        base_class = GuardedUtf8
    
    class DynamicLiteral(base_class):
        """Classe dynamique pour valider des valeurs littérales."""
        
        _allowed_values = values
        _type_en = f"a literal value, one of: {', '.join(repr(v) for v in values)}"
        _type_py = first_type
        _type_json = {
            "enum": list(values)
        }
        
        @classmethod
        def _parse_native(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
            """Vérifie si la valeur est exactement dans les valeurs autorisées."""
            # Vérification stricte
            if value in cls._allowed_values:
                return UncertaintyLevel(Tolerance.STRICT), value, None
            
            return UncertaintyLevel(Tolerance.ANYTHING), value, f"Value must be one of {cls._allowed_values}"
        
        @classmethod
        def _parse_heuristic(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
            """Tentative de conversion avec nettoyage basique."""
            # Pour les strings, essayer avec strip() et case-insensitive
            if isinstance(value, str) and all(isinstance(v, str) for v in cls._allowed_values):
                cleaned = value.strip()
                
                # Essai exact après nettoyage
                if cleaned in cls._allowed_values:
                    return UncertaintyLevel(Tolerance.PRECISE), cleaned, None
                
                # Essai case-insensitive
                for allowed in cls._allowed_values:
                    if cleaned.lower() == allowed.lower():
                        return UncertaintyLevel(Tolerance.PRECISE), allowed, None
            
            # Pour les nombres, essayer de convertir
            if isinstance(value, str) and any(isinstance(v, (int, float)) for v in cls._allowed_values):
                try:
                    # Essayer int
                    try:
                        int_val = int(value)
                        if int_val in cls._allowed_values:
                            return UncertaintyLevel(Tolerance.PRECISE), int_val, None
                    except ValueError:
                        pass
                    
                    # Essayer float
                    try:
                        float_val = float(value)
                        if float_val in cls._allowed_values:
                            return UncertaintyLevel(Tolerance.PRECISE), float_val, None
                    except ValueError:
                        pass
                except:
                    pass
            
            return UncertaintyLevel(Tolerance.ANYTHING), value, f"Value must be one of {cls._allowed_values}"
    
    DynamicLiteral.__name__ = f"Literal[{', '.join(repr(v) for v in values[:3])}{'...' if len(values) > 3 else ''}]"
    return DynamicLiteral


# Alias pour compatibilité
GuardedLiteral = guarded_literal
