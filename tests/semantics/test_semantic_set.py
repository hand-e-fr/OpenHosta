"""
Tests pour SemanticSet avec clustering sémantique.
Utilise l'API embedding réelle pour le clustering.
"""
import pytest
from dotenv import load_dotenv

load_dotenv()

# Tolerance constants based on model's embedding_similarity_min
# These map to similarity thresholds via: threshold = 0.99 - (tolerance * (0.99 - MIN_SIM))
TOLERANCE_STRICT = 0.0      # threshold = 0.99 (exact match only)
TOLERANCE_NORMAL = 0.5      # threshold = ~0.64 (moderate similarity)
TOLERANCE_PERMISSIVE = 1.0  # threshold = MIN_SIM (accept any similar items)


def test_similar_items_same_cluster():
    """
    Test: Deux éléments sémantiquement similaires doivent être dans le même cluster.
    
    'Laver le sol' et 'Passer la serpillière' sont des synonymes fonctionnels
    et doivent être regroupés.
    """
    from OpenHosta.semantics.collections import SemanticSet
    
    # Use permissive tolerance to group semantically similar items
    tasks = SemanticSet(tolerance=TOLERANCE_PERMISSIVE)
    
    tasks.add("Laver le sol")
    tasks.add("Passer la serpillière")
    
    # Les deux doivent être dans le même cluster
    assert len(tasks) == 1, f"Expected 1 cluster, got {len(tasks)}"
    
    # Vérifier que les deux membres sont présents
    members = tasks.members()
    assert len(members) == 2, f"Expected 2 members, got {len(members)}"
    assert "Laver le sol" in members
    assert "Passer la serpillière" in members


def test_different_items_different_clusters():
    """
    Test: Deux éléments sémantiquement différents doivent être dans des clusters différents.
    """
    from OpenHosta.semantics.collections import SemanticSet
    
    # Use normal tolerance - semantically different items should stay separate
    tasks = SemanticSet(tolerance=TOLERANCE_NORMAL)
    
    tasks.add("Laver le sol")
    tasks.add("Faire les courses")
    
    # Doivent être dans des clusters différents
    assert len(tasks) == 2, f"Expected 2 clusters, got {len(tasks)}"


def test_repr_shows_labels():
    """
    Test: La représentation affiche les labels des clusters.
    """
    from OpenHosta.semantics.collections import SemanticSet
    
    tasks = SemanticSet()
    tasks.add("Test item")
    
    repr_str = repr(tasks)
    assert repr_str.startswith("{"), f"Expected set format, got: {repr_str}"
    assert repr_str.endswith("}"), f"Expected set format, got: {repr_str}"


def test_semantic_context_orange():
    """
    Test: Le contexte sémantique du type influence le clustering.
    
    'Orange' peut être un fruit ou une couleur. Selon le type défini:
    - Avec type="Fruit", 'orange' doit se grouper avec 'agrume'
    - Avec type="Couleur", 'orange' doit se grouper avec 'marron'
    """
    from OpenHosta.semantics import SemanticSet, SemanticType
    
    # Test 1: Orange comme fruit -> doit se grouper avec agrume
    FruitType = SemanticType(str, "fruit par gamme de prix en France.")
    fruits = SemanticSet(type=FruitType, tolerance=0.1)
    fruits.add("poire")
    fruits.add("orange")
    fruits.add("agrume")
    fruits.add("banane")
    fruits.add("banana")
    fruits.add("pomme")
    print(fruits)

    fruits.add("fruit du pommier")
    print(fruits)

    # test si "apple" est dans fruits
    assert "fruit du pommier" in fruits, "fruit du pommier should be in fruits"
    assert "Orange" in fruits, "Orange should be in fruits"

    # Ils devraient être dans le même cluster (contexte: fruit)
    assert len(fruits) == 1, f"[Fruit context] Expected 1 cluster for orange+agrume, got {len(fruits)}"
    
    # Test 2: Orange comme couleur -> doit se grouper avec marron
    ColorType = SemanticType(str, "Couleur")
    colors = SemanticSet(type=ColorType, tolerance=TOLERANCE_PERMISSIVE)
    colors.add("orange")
    colors.add("marron")
    
    # Ils devraient être dans le même cluster (contexte: couleur)
    assert len(colors) == 1, f"[Couleur context] Expected 1 cluster for orange+marron, got {len(colors)}"
