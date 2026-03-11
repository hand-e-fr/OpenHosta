# src/OpenHosta/semantics/engine.py
"""
Moteur de clustering sémantique.

Génère un nuage d'exemples via emulate_iterator, les embeds, puis les cluster
avec DBSCAN. Les clusters sont fixes une fois créés.
"""

from __future__ import annotations

from typing import List, Optional, Dict, Any
import numpy as np

from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import cosine_distances

from ..defaults import config
from ..core.base_model import Model, ModelCapabilities
from ..pipelines import OneTurnConversationPipeline
from ..exec.emulate_iterator import emulate_iterator


def generate_examples(
    axis: str,
    pipeline: OneTurnConversationPipeline = None,
    n: int = 50,
    min_probability: float = 1e-3
) -> List[str]:
    """
    Génère des exemples diversifiés pour un axe sémantique donné
    en utilisant emulate_iterator (logprob branching).
    
    Args:
        axis: Description de l'axe sémantique (ex: "Tâches Ménagères")
        pipeline: Pipeline à utiliser, par défaut config.DefaultPipeline
        n: Nombre maximum d'exemples à générer
        min_probability: Seuil de probabilité minimum pour le branching
        
    Returns:
        Liste de chaînes de caractères (exemples diversifiés)
    """
    if pipeline is None:
        pipeline = config.DefaultPipeline

    def _generate_example() -> str:
        """placeholder"""
        return emulate_iterator(
            pipeline=pipeline,
            max_generation=n,
            min_probability=min_probability
        )

    # f-string docstrings don't work in Python — __doc__ must be set explicitly
    _generate_example.__doc__ = (
        f"Returns a single diverse example of: {axis}.\n"
        f"Give only the example itself, nothing else. No numbering, no explanation.\n\n"
        f"Returns:\n"
        f"    str: A single example of {axis}"
    )

    def _is_quality_example(text: str) -> bool:
        """Filter out garbled outputs from logprob token concatenation."""
        if not text or len(text) > 100:
            return False
        # Reject strings with uppercase letters mid-word (e.g. "MCheRequin", "OiseauxReptile")
        # Count transitions: lowercase→uppercase without space separator
        mid_word_uppers = 0
        for i in range(1, len(text)):
            if text[i].isupper() and text[i-1].isalpha() and text[i-1].islower():
                # Allow normal CamelCase-like at word start (after space)
                if i >= 2 and text[i-2] == ' ':
                    continue
                mid_word_uppers += 1
        if mid_word_uppers > 1:
            return False
        # Reject long strings without spaces (likely concatenated tokens)
        if len(text) > 30 and ' ' not in text:
            return False
        return True

    examples = []
    seen = set()
    for example in _generate_example():
        cleaned = example.strip().strip('"\'')
        if cleaned and cleaned.lower() not in seen and _is_quality_example(cleaned):
            seen.add(cleaned.lower())
            examples.append(cleaned)
    
    return examples


class SemanticEngine:
    """
    Moteur de clustering. Encapsule les embeddings, le DBSCAN et
    les centroïdes pour assignation rapide.
    """

    def __init__(
        self,
        examples: List[str],
        embeddings: np.ndarray,
        tolerance: float = 0.15,
    ):
        """
        Fit les clusters sur les embeddings fournis.
        
        Args:
            examples: Les textes générés
            embeddings: Matrice (n_samples, dim) des embeddings
            tolerance: Distance cosine max pour appartenir au même cluster (eps DBSCAN)
        """
        self.examples = list(examples)
        self.embeddings = np.array(embeddings, dtype=np.float64)
        self.tolerance = tolerance

        # DBSCAN avec distance cosine
        clustering = DBSCAN(eps=tolerance, min_samples=1, metric="cosine")
        self.labels = clustering.fit_predict(self.embeddings)

        # Identifier les clusters (exclure le bruit label=-1 de DBSCAN)
        unique_labels = set(self.labels)
        unique_labels.discard(-1)
        self.cluster_ids = sorted(unique_labels)

        # Calculer les centroïdes (moyenne des embeddings par cluster)
        self.centroids: Dict[int, np.ndarray] = {}
        for cid in self.cluster_ids:
            mask = self.labels == cid
            self.centroids[cid] = self.embeddings[mask].mean(axis=0)

        # Pré-calculer la matrice de distances inter-centroïdes
        if len(self.cluster_ids) > 1:
            centroid_matrix = np.array([self.centroids[cid] for cid in self.cluster_ids])
            self._centroid_distances = cosine_distances(centroid_matrix)
        else:
            self._centroid_distances = np.zeros((1, 1))

        # Calculer le seuil outlier : distance max observée dans les clusters
        self._max_cluster_radius = 0.0
        for cid in self.cluster_ids:
            mask = self.labels == cid
            cluster_embs = self.embeddings[mask]
            if len(cluster_embs) > 1:
                dists = cosine_distances(cluster_embs, [self.centroids[cid]]).flatten()
                self._max_cluster_radius = max(self._max_cluster_radius, dists.max())

        # Marge de sécurité pour outlier detection
        self._outlier_threshold = self._max_cluster_radius + self.tolerance

    def predict(self, embedding: np.ndarray) -> int:
        """
        Assigne un embedding au cluster le plus proche.
        Raise ValueError si outlier.
        
        Args:
            embedding: Vecteur d'embedding (dim,)
            
        Returns:
            cluster_id
            
        Raises:
            ValueError: Si l'embedding est un outlier (trop loin de tout cluster)
        """
        embedding = np.array(embedding, dtype=np.float64).reshape(1, -1)
        centroid_matrix = np.array([self.centroids[cid] for cid in self.cluster_ids])
        distances = cosine_distances(embedding, centroid_matrix).flatten()

        best_idx = int(np.argmin(distances))
        best_distance = distances[best_idx]

        if best_distance > self._outlier_threshold:
            raise ValueError(
                f"Out of sample: distance {best_distance:.4f} exceeds "
                f"threshold {self._outlier_threshold:.4f}. "
                f"The item does not belong to any known cluster."
            )

        return self.cluster_ids[best_idx]

    def get_top_k_nearest_center(self, cluster_id: int, k: int = 10) -> List[str]:
        """
        Retourne les k exemples les plus proches du centroïde d'un cluster.
        
        Args:
            cluster_id: ID du cluster
            k: Nombre d'exemples à retourner
            
        Returns:
            Liste de textes (max k éléments)
        """
        mask = self.labels == cluster_id
        indices = np.where(mask)[0]
        cluster_embs = self.embeddings[indices]

        dists = cosine_distances(cluster_embs, [self.centroids[cluster_id]]).flatten()
        sorted_idx = np.argsort(dists)[:k]

        return [self.examples[indices[i]] for i in sorted_idx]

    def get_nearest_clusters(self, cluster_id: int, k: int = 5) -> List[int]:
        """
        Retourne les k clusters les plus proches d'un cluster donné.
        
        Args:
            cluster_id: ID du cluster de référence
            k: Nombre de voisins
            
        Returns:
            Liste de cluster_ids triés par proximité
        """
        if len(self.cluster_ids) <= 1:
            return []

        idx = self.cluster_ids.index(cluster_id)
        distances = self._centroid_distances[idx]

        # Exclure lui-même (distance=0) en triant
        sorted_indices = np.argsort(distances)
        neighbors = []
        for i in sorted_indices:
            if self.cluster_ids[i] != cluster_id:
                neighbors.append(self.cluster_ids[i])
                if len(neighbors) >= k:
                    break

        return neighbors

    @property
    def n_clusters(self) -> int:
        return len(self.cluster_ids)
