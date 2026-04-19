# src/OpenHosta/semantics/semantic_set.py
"""
SemanticSet — Ensemble à clustering sémantique pré-calculé.

Les clusters sont générés à l'initialisation via emulate_variants,
puis fixés. Les éléments ajoutés sont assignés aux clusters existants.
"""

from __future__ import annotations

from typing import List, Optional, Dict, Any, Iterator

import numpy as np

from ..defaults import config
from ..core.base_model import Model
from ..pipelines import OneTurnConversationPipeline

from .engine import generate_examples, SemanticEngine
from .labeler import label_clusters


class SemanticSet:
    """
    Ensemble sémantique avec clustering pré-calculé.
    
    À l'initialisation :
    1. Génère un nuage d'exemples via emulate_variants
    2. Embed les exemples
    3. Cluster via DBSCAN
    4. Labellise chaque cluster via le DefaultModel
    
    Les clusters sont fixes après l'initialisation.
    
    Usage:
        >>> tasks = SemanticSet(axis="Tâches Ménagères", tolerance=0.15)
        >>> tasks.add("Laver le sol")
        >>> tasks.add("Passer la serpillière")  # Même cluster
        >>> tasks.add("Faire la vaisselle")      # Nouveau cluster
        >>> print(tasks)  # {"Nettoyage sols", "Vaisselle"}
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
        Initialise le SemanticSet en pré-calculant les clusters.
        
        Args:
            axis: Description de l'axe sémantique (ex: "Type d'animal")
            tolerance: Distance cosine max pour regrouper (eps DBSCAN)
            model: Modèle pour embeddings et labelling (défaut: config.DefaultModel)
            pipeline: Pipeline pour la génération d'exemples (défaut: config.DefaultPipeline)
            n_examples: Nombre d'exemples à générer
            min_probability: Seuil de probabilité pour emulate_variants
        """
        self._axis = axis
        self._tolerance = tolerance
        self._model = model or config.DefaultModel
        self._pipeline = pipeline

        # 1. Générer des exemples diversifiés
        self._generated_examples = generate_examples(
            axis=axis,
            pipeline=self._pipeline,
            n=n_examples,
            min_probability=min_probability,
        )

        if len(self._generated_examples) == 0:
            raise RuntimeError(
                f"No examples could be generated for axis '{axis}'. "
                f"Check your model configuration."
            )

        # 2. Embed les exemples
        embeddings = self._model.embed(self._generated_examples)

        # 3. Cluster
        self._engine = SemanticEngine(
            examples=self._generated_examples,
            embeddings=embeddings,
            tolerance=tolerance,
        )

        # 4. Labelliser les clusters
        self._labels = label_clusters(self._engine, model=self._model)

        # Stockage des éléments ajoutés par l'utilisateur
        # {cluster_id: [(item_text, embedding), ...]}
        self._items: Dict[int, List[tuple]] = {cid: [] for cid in self._engine.cluster_ids}

        # Cache des embeddings des items ajoutés
        self._item_embeddings: Dict[str, np.ndarray] = {}

    def add(self, item: str) -> int:
        """
        Ajoute un élément au cluster le plus proche.
        
        Args:
            item: Texte à ajouter
            
        Returns:
            cluster_id auquel l'item a été assigné
            
        Raises:
            ValueError: Si l'item est un outlier (hors du domaine couvert)
        """
        embedding = self._embed_item(item)
        cluster_id = self._engine.predict(embedding)

        self._items[cluster_id].append((item, embedding))
        self._item_embeddings[item] = embedding

        return cluster_id

    def _embed_item(self, item: str) -> np.ndarray:
        """Embed un item et le cache."""
        if item in self._item_embeddings:
            return self._item_embeddings[item]

        embeddings = self._model.embed([item])
        embedding = np.array(embeddings[0], dtype=np.float64)
        return embedding

    def _assign_cluster(self, embedding: np.ndarray) -> int:
        """Assigne un embedding à un cluster (peut lever ValueError)."""
        return self._engine.predict(embedding)

    def __contains__(self, item: str) -> bool:
        """
        Vérifie si un item appartient à un cluster (sans l'ajouter).
        Retourne False si outlier.
        """
        try:
            embedding = self._embed_item(item)
            self._engine.predict(embedding)
            return True
        except ValueError:
            return False

    def __len__(self) -> int:
        """Nombre de clusters."""
        return self._engine.n_clusters

    def __repr__(self) -> str:
        """Représentation sous forme d'ensemble de labels."""
        if not self._labels:
            return "{}"
        label_strs = ", ".join(f'"{label}"' for label in self._labels.values())
        return "{" + label_strs + "}"

    def __str__(self) -> str:
        return self.__repr__()

    def __iter__(self) -> Iterator[str]:
        """Itère sur les labels des clusters."""
        return iter(self._labels.values())

    def members(self, label: str = None) -> List[str]:
        """
        Retourne les éléments ajoutés par l'utilisateur.
        
        Args:
            label: Si spécifié, retourne uniquement les membres de ce cluster.
                   Sinon retourne tous les membres.
                   
        Returns:
            Liste de textes
        """
        if label is not None:
            # Trouver le cluster_id pour ce label
            for cid, lbl in self._labels.items():
                if lbl == label:
                    return [item for item, _ in self._items[cid]]
            return []

        # Tous les membres
        all_members = []
        for cid in self._engine.cluster_ids:
            for item, _ in self._items[cid]:
                all_members.append(item)
        return all_members

    def clusters(self) -> List[Dict[str, Any]]:
        """
        Retourne la structure complète des clusters.
        
        Returns:
            [{"label": str, "members": [str, ...]}, ...]
        """
        result = []
        for cid in self._engine.cluster_ids:
            result.append({
                "label": self._labels.get(cid, f"Cluster {cid}"),
                "members": [item for item, _ in self._items[cid]],
            })
        return result

    def cluster_of(self, item: str) -> Optional[str]:
        """
        Retourne le label du cluster d'un item (sans l'ajouter).
        
        Args:
            item: Texte à rechercher
            
        Returns:
            Label du cluster, ou None si outlier
        """
        try:
            embedding = self._embed_item(item)
            cluster_id = self._engine.predict(embedding)
            return self._labels.get(cluster_id)
        except ValueError:
            return None

    @property
    def axis(self) -> str:
        return self._axis

    @property
    def tolerance(self) -> float:
        return self._tolerance

    @property
    def generated_examples(self) -> List[str]:
        """Exemples générés lors de l'initialisation (pour debug)."""
        return list(self._generated_examples)

    @property
    def engine(self) -> SemanticEngine:
        """Accès au moteur de clustering (pour usage avancé)."""
        return self._engine
