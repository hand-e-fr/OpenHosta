# src/OpenHosta/core/semantics.py
from typing import Any, Type
from .engine import llm_convert_scalar  # On appelle l'ancien code refactorisé
from .uncertainty import calculate_confidence, UncertainValue

# --- L'INTERFACE ---
class SemanticNode:
    """Tous les objets sémantiques ont une description et une confiance."""
    def __init__(self, description: str):
        self.description = description
        self.confidence = 1.0

# --- LES PRIMITIVES ---
class SemanticScalar(SemanticNode):
    """
    
    """
    pass

def create_semantic_type(base_type: Type, name: str):
    class SemanticType(base_type, SemanticScalar):
        def __new__(cls, value: Any, description: str = ""):
            # 1. Délégation au moteur (ex-type_converter)
            val_converted, logprobs = llm_convert_scalar(value, base_type, description)
            
            # 2. Création de l'objet natif (int, str...)
            instance = super().__new__(cls, val_converted)
            
            # 3. Valorisation de l'incertitude
            instance.confidence = calculate_confidence(logprobs)
            instance.description = description
            return instance
            
    SemanticType.__name__ = name
    return SemanticType

# Définition explicite des types pour l'autocomplétion
SemanticInt = create_semantic_type(int, "SemanticInt")
SemanticStr = create_semantic_type(str, "SemanticStr")
SemanticFloat = create_semantic_type(float, "SemanticFloat")
SemanticBool = create_semantic_type(bool, "SemanticBool")

# --- NIVEAU 3 : LES MODÈLES (Structures) ---
class SemanticModel(SemanticNode):
    """Pour les objets complexes (Animal, User, etc.)"""
    def __init__(self, **kwargs):
        # Logique d'initialisation et de validation globale
        super().__init__(description=self.__doc__)
        # ...