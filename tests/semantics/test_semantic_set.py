"""
Tests pour SemanticSet avec clustering sémantique.
Utilise l'API embedding réelle pour le clustering.
"""
import math


# Tolerance constants based on model's embedding_similarity_min
# These map to similarity thresholds via: threshold = 0.99 - (tolerance * (0.99 - MIN_SIM))
TOLERANCE_STRICT = 0.0      # threshold = 0.99 (exact match only)
TOLERANCE_NORMAL = 0.5      # threshold = ~0.64 (moderate similarity)
TOLERANCE_PERMISSIVE = 1.0  # threshold = MIN_SIM (accept any similar items)


class TestSemanticSetClustering:
    """Tests pour vérifier que SemanticSet groupe les éléments sémantiquement similaires."""
    
    def _cosine_similarity(self, vec_a, vec_b):
        """Calcul de similarité cosinus."""
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)
    
    def test_similar_items_same_cluster(self):
        """
        Test: Deux éléments sémantiquement similaires doivent être dans le même cluster.
        
        'Laver le sol' et 'Passer la serpillière' sont des synonymes fonctionnels
        et doivent être regroupés.
        """
        from src.OpenHosta.semantics.collections import SemanticSet
        
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
    
    def test_different_items_different_clusters(self):
        """
        Test: Deux éléments sémantiquement différents doivent être dans des clusters différents.
        """
        from src.OpenHosta.semantics.collections import SemanticSet
        
        # Use normal tolerance - semantically different items should stay separate
        tasks = SemanticSet(tolerance=TOLERANCE_NORMAL)
        
        tasks.add("Laver le sol")
        tasks.add("Faire les courses")
        
        # Doivent être dans des clusters différents
        assert len(tasks) == 2, f"Expected 2 clusters, got {len(tasks)}"
    
    def test_repr_shows_labels(self):
        """
        Test: La représentation affiche les labels des clusters.
        """
        from src.OpenHosta.semantics.collections import SemanticSet
        
        tasks = SemanticSet()
        tasks.add("Test item")
        
        repr_str = repr(tasks)
        assert repr_str.startswith("{"), f"Expected set format, got: {repr_str}"
        assert repr_str.endswith("}"), f"Expected set format, got: {repr_str}"


if __name__ == "__main__":
    # Test standalone
    test = TestSemanticSetClustering()
    
    print("Test 1: Similar items in same cluster...")
    try:
        test.test_similar_items_same_cluster()
        print("  ✓ PASS")
    except Exception as e:
        print(f"  ✗ FAIL: {e}")
    
    print("Test 2: Different items in different clusters...")
    try:
        test.test_different_items_different_clusters()
        print("  ✓ PASS")
    except Exception as e:
        print(f"  ✗ FAIL: {e}")
    
    print("Test 3: Repr format...")
    try:
        test.test_repr_shows_labels()
        print("  ✓ PASS")
    except Exception as e:
        print(f"  ✗ FAIL: {e}")
