# src/OpenHosta/semantics/labeler.py
"""
Auto-labelling des clusters sémantiques.

Pour chaque cluster, prend les 10 exemples les plus proches du centre
et les 5 clusters voisins pour générer un label distinctif via le DefaultModel.
"""

from __future__ import annotations

from typing import Dict, List

from ..core.base_model import Model
from ..defaults import config


def label_clusters(engine, model: Model = None) -> Dict[int, str]:
    """
    Génère un label distinctif pour chaque cluster.
    
    Pour chaque cluster:
    1. Prend les max 10 éléments les plus proches du centroïde
    2. Identifie les 5 clusters voisins les plus proches
    3. Prompt le LLM pour nommer le cluster de façon distinctive
    
    Args:
        engine: SemanticEngine avec clusters déjà fitté
        model: Modèle LLM à utiliser (défaut: config.DefaultModel)
        
    Returns:
        {cluster_id: label}
    """
    if model is None:
        model = config.DefaultModel

    labels: Dict[int, str] = {}

    for cluster_id in engine.cluster_ids:
        # Top 10 exemples proches du centre
        top_examples = engine.get_top_k_nearest_center(cluster_id, k=10)

        # 5 clusters voisins les plus proches
        neighbor_ids = engine.get_nearest_clusters(cluster_id, k=5)
        neighbor_summaries = []
        for nid in neighbor_ids:
            neighbor_examples = engine.get_top_k_nearest_center(nid, k=3)
            neighbor_summaries.append(", ".join(neighbor_examples))

        # Construire le prompt
        prompt = _build_labeling_prompt(top_examples, neighbor_summaries)

        # Appel LLM
        messages = [
            {"role": "system", "content": [{"type": "text", "text": 
                "You are a naming expert. Your job is to give a short, distinctive "
                "label to a group of items. The label must clearly differentiate this "
                "group from its neighboring groups. Reply with ONLY the label, nothing else. "
                "Maximum 4 words. Use the same language as the examples."
            }]},
            {"role": "user", "content": [{"type": "text", "text": prompt}]}
        ]

        try:
            response_dict = model.generate(messages)
            label = model.get_response_content(response_dict).strip().strip('"\'')
            labels[cluster_id] = label
        except Exception as e:
            # Fallback: utiliser le premier exemple comme label
            labels[cluster_id] = top_examples[0] if top_examples else f"Cluster {cluster_id}"

    return labels


def _build_labeling_prompt(
    top_examples: List[str],
    neighbor_summaries: List[str]
) -> str:
    """Construit le prompt pour le labelling d'un cluster."""
    
    examples_str = "\n".join(f"  - {ex}" for ex in top_examples)
    
    prompt = f"Here are the representative items of this group:\n{examples_str}\n"

    if neighbor_summaries:
        prompt += "\nThe closest neighboring groups contain items like:\n"
        for i, summary in enumerate(neighbor_summaries, 1):
            prompt += f"  {i}. {summary}\n"
        prompt += "\nGive a short label that clearly distinguishes THIS group from the neighbors."
    else:
        prompt += "\nGive a short label for this group."

    return prompt
