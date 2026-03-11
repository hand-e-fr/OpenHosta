# src/OpenHosta/semantics/semantic_dict.py
"""
SemanticDict — Dictionnaire à clés sémantiques.

Compose un SemanticSet interne pour la gestion des clés.
Les valeurs sont stockées par clé exacte au sein des clusters.
"""

from __future__ import annotations

from typing import Any, Dict, Iterator, List, Optional, Tuple

import numpy as np
from sklearn.metrics.pairwise import cosine_distances

from ..defaults import config
from ..core.base_model import Model
from ..pipelines import OneTurnConversationPipeline

from .semantic_set import SemanticSet


class SemanticDict:
    """
    Dictionnaire sémantique. Les clés sont gérées par un SemanticSet interne,
    les valeurs sont stockées par clé exacte.
    
    Recherche floue : retrouver la clé exacte la plus proche dans le cluster.
    
    Usage:
        >>> router = SemanticDict(axis="Animal", tolerance=0.15)
        >>> router["Chien"] = "Wouf"
        >>> router["Chat"] = "Miaou"
        >>> print(router["Mon petit toutou"])  # "Wouf"
        >>> print(router["Félin"])              # "Miaou"
    """

    def __init__(
        self,
        axis: str,
        tolerance: float = 0.15,
        model: Model = None,
        pipeline: OneTurnConversationPipeline = None,
        n_examples: int = 50,
        min_probability: float = 1e-3,
    ):
        """
        Crée un SemanticSet interne pour les clés.
        Même init : génération d'exemples, clustering, labelling.
        
        Args:
            axis: Description de l'axe sémantique
            tolerance: Distance cosine max
            model: Modèle LLM (défaut: config.DefaultModel)
            pipeline: Pipeline pour emulate_iterator
            n_examples: Nombre d'exemples à générer
            min_probability: Seuil de probabilité pour emulate_iterator
        """
        self._key_set = SemanticSet(
            axis=axis,
            tolerance=tolerance,
            model=model,
            pipeline=pipeline,
            n_examples=n_examples,
            min_probability=min_probability,
        )

        # Stockage par clé exacte : {key_text: value}
        self._store: Dict[str, Any] = {}
        # Cache des embeddings par clé exacte
        self._key_embeddings: Dict[str, np.ndarray] = {}

    def __setitem__(self, key: str, value: Any) -> None:
        """
        Assigne une valeur à une clé.
        La clé est assignée à un cluster via le SemanticSet interne.
        
        Args:
            key: Clé textuelle
            value: Valeur à stocker
            
        Raises:
            ValueError: Si la clé est un outlier (hors domaine)
        """
        # Assigner au cluster (peut lever ValueError)
        embedding = self._key_set._embed_item(key)
        cluster_id = self._key_set._engine.predict(embedding)

        # Stocker dans le SemanticSet
        if key not in self._store:
            self._key_set._items[cluster_id].append((key, embedding))
            self._key_set._item_embeddings[key] = embedding

        self._store[key] = value
        self._key_embeddings[key] = embedding

    def __getitem__(self, key: str) -> Any:
        """
        Recherche floue. Trouve le cluster, puis la clé exacte
        la plus proche en cosine dans ce cluster.
        
        Args:
            key: Clé textuelle (peut être approximative)
            
        Returns:
            Valeur associée à la clé exacte la plus proche
            
        Raises:
            KeyError: Si outlier ou aucune clé stockée dans le cluster
        """
        # Match exact d'abord
        if key in self._store:
            return self._store[key]

        # Recherche floue
        try:
            embedding = self._key_set._embed_item(key)
            cluster_id = self._key_set._engine.predict(embedding)
        except ValueError:
            raise KeyError(
                f"Key '{key}' is out of sample (outlier). "
                f"No matching cluster found."
            )

        # Trouver la clé exacte la plus proche dans ce cluster
        closest_key = self._find_closest_key_in_cluster(embedding, cluster_id)
        if closest_key is None:
            raise KeyError(
                f"No stored key found in cluster for '{key}'. "
                f"Add items with __setitem__ first."
            )

        return self._store[closest_key]

    def _find_closest_key_in_cluster(self, embedding: np.ndarray, cluster_id: int) -> Optional[str]:
        """Trouve la clé exacte la plus proche d'un embedding dans un cluster."""
        # Collecter les clés stockées dans ce cluster
        cluster_keys = []
        cluster_embs = []
        for item_text, item_emb in self._key_set._items[cluster_id]:
            if item_text in self._store:
                cluster_keys.append(item_text)
                cluster_embs.append(item_emb)

        if not cluster_keys:
            return None

        # Distance cosine
        emb_matrix = np.array(cluster_embs, dtype=np.float64)
        query = np.array(embedding, dtype=np.float64).reshape(1, -1)
        distances = cosine_distances(query, emb_matrix).flatten()

        best_idx = int(np.argmin(distances))
        return cluster_keys[best_idx]

    def __contains__(self, key: str) -> bool:
        """Vérifie si une clé (exacte ou floue) peut être résolue."""
        if key in self._store:
            return True
        try:
            self[key]
            return True
        except KeyError:
            return False

    def __len__(self) -> int:
        """Nombre de clés exactes stockées."""
        return len(self._store)

    def __iter__(self) -> Iterator[str]:
        """Itère sur les clés exactes stockées."""
        return iter(self._store)

    def __repr__(self) -> str:
        items = [f'"{k}": {repr(v)}' for k, v in self._store.items()]
        return "{" + ", ".join(items) + "}"

    def __str__(self) -> str:
        return self.__repr__()

    def keys(self):
        """Retourne les clés exactes."""
        return self._store.keys()

    def values(self):
        """Retourne les valeurs."""
        return self._store.values()

    def items(self):
        """Retourne les paires (clé exacte, valeur)."""
        return self._store.items()

    def get(self, key: str, default: Any = None) -> Any:
        """Recherche floue avec valeur par défaut."""
        try:
            return self[key]
        except KeyError:
            return default

    @property
    def axis(self) -> str:
        return self._key_set.axis

    @property
    def tolerance(self) -> float:
        return self._key_set.tolerance

    @property
    def key_set(self) -> SemanticSet:
        """Accès au SemanticSet interne (pour usage avancé)."""
        return self._key_set
