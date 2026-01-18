# Facade Pattern : On expose tout au même niveau
from .constants import Tolerance
from .primitives import SemanticType
from .scalars import SemanticInt, SemanticStr, SemanticBool, SemanticFloat
from .collections import SemanticList, SemanticDict, SemanticSet
from .models import SemanticModel

# On expose aussi la méthode de résolution statique sur SemanticType
# (Injection de dépendance pour éviter les imports circulaires)
from .resolver import TypeResolver
SemanticType.resolve = staticmethod(TypeResolver.resolve)

__all__ = [
    "Tolerance",
    "SemanticType",
    "SemanticModel",
    "SemanticInt", 
    "SemanticStr", 
    "SemanticBool", 
    "SemanticFloat",
    "SemanticList", 
    "SemanticDict",
    "SemanticSet"
]


# src/OpenHosta/
# ├── __init__.py                # Version et exports globaux
# │
# ├── core/                      # ⚙️ LE MOTEUR (Interne)
# │   ├── __init__.py
# │   ├── config.py              # Configuration (Clés API, Modèles par défaut)
# │   ├── engine.py              # L'ex-type_converter (Appels LLM, Prompts, Retries)
# │   └── uncertainty.py         # Objets mathématiques (CastingResult, UncertainValue)
# │
# └── semantics/                 # 🧠 L'INTELLIGENCE (Public API)
#     ├── __init__.py            # Facade (expose SemanticType, SemanticModel, etc.)
#     ├── constants.py           # La classe Tolerance
#     ├── primitives.py          # GuardedPrimitive (Pipeline) & SemanticType (Base class)
#     ├── scalars.py             # Implémentations concrètes (SemanticInt, SemanticStr...)
#     ├── collections.py         # Structures dynamiques (SemanticList, SemanticDict)
#     ├── models.py              # SemanticModel (Dataclasses / Pydantic integration)
#     └── resolver.py            # TypeResolver (Gestion du module typing)