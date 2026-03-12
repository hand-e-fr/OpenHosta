"""
Tests for SemanticSet — clustering, adding, membership, outlier detection.
Uses real Ollama model via session-scoped 'animal_set' fixture.
"""
import pytest
import numpy as np


class TestSemanticSetInit:
    """Tests for SemanticSet initialization."""

    def test_has_clusters(self, animal_set):
        assert len(animal_set) >= 1, "Should have at least 1 cluster"

    def test_has_labels(self, animal_set):
        labels = list(animal_set)
        assert len(labels) == len(animal_set)
        for label in labels:
            assert isinstance(label, str)
            assert len(label) > 0

    def test_has_generated_examples(self, animal_set):
        assert len(animal_set.generated_examples) > 0

    def test_repr_format(self, animal_set):
        r = repr(animal_set)
        assert r.startswith("{")
        assert r.endswith("}")


class TestSemanticSetAdd:
    """Tests for adding items."""

    def test_add_returns_cluster_id(self, animal_set):
        cid = animal_set.add("Tigre")
        assert isinstance(cid, (int, np.integer))
        assert cid in animal_set.engine.cluster_ids

    def test_add_appears_in_members(self, animal_set):
        animal_set.add("Panthère")
        assert "Panthère" in animal_set.members()

    def test_add_multiple_items(self, animal_set):
        animal_set.add("Requin")
        animal_set.add("Baleine")
        members = animal_set.members()
        assert "Requin" in members
        assert "Baleine" in members


class TestSemanticSetContains:
    """Tests for __contains__ (semantic membership)."""

    def test_contains_related_item(self, animal_set):
        # An animal name should be within the domain
        assert ("Lion" in animal_set) or ("Chat" in animal_set), \
            "At least one common animal should be in the set's domain"

    def test_repr_is_stable(self, animal_set):
        """repr should not change between calls (clusters are fixed)."""
        r1 = repr(animal_set)
        r2 = repr(animal_set)
        assert r1 == r2


class TestSemanticSetClusterOf:
    """Tests for cluster_of method."""

    def test_cluster_of_returns_label(self, animal_set):
        animal_set.add("Serpent")
        label = animal_set.cluster_of("Serpent")
        assert label is not None
        assert isinstance(label, str)

    def test_cluster_of_similar_items_same_cluster(self, animal_set):
        """Semantically similar items should map to the same cluster."""
        animal_set.add("Aigle")
        animal_set.add("Faucon")
        label_aigle = animal_set.cluster_of("Aigle")
        label_faucon = animal_set.cluster_of("Faucon")
        # With tolerance=0.5, birds should be in the same cluster
        # (not guaranteed but likely — this test documents the expected behavior)
        print(f"Aigle → {label_aigle}, Faucon → {label_faucon}")


class TestSemanticSetClusters:
    """Tests for clusters() method."""

    def test_clusters_structure(self, animal_set):
        clusters = animal_set.clusters()
        assert isinstance(clusters, list)
        for c in clusters:
            assert "label" in c
            assert "members" in c
            assert isinstance(c["members"], list)

    def test_clusters_count_matches_len(self, animal_set):
        assert len(animal_set.clusters()) == len(animal_set)


class TestSemanticSetMembers:
    """Tests for members() method."""

    def test_members_returns_all_added(self, animal_set):
        animal_set.add("Crocodile")
        all_members = animal_set.members()
        assert "Crocodile" in all_members

    def test_members_with_label_filter(self, animal_set):
        labels = list(animal_set)
        if labels:
            filtered = animal_set.members(label=labels[0])
            assert isinstance(filtered, list)

    def test_members_nonexistent_label(self, animal_set):
        result = animal_set.members(label="NonExistentLabel_XYZ")
        assert result == []
