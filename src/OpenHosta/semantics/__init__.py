# src/OpenHosta/semantics/__init__.py
"""
OpenHosta.semantics — Collections sémantiques.

Fournit des structures de données qui comparent les éléments par leur sens
plutôt que par leur syntaxe, en utilisant des embeddings et du clustering.
"""

from .semantic_set import SemanticSet
from .semantic_dict import SemanticDict

__all__ = [
    "SemanticSet",
    "SemanticDict",
]
