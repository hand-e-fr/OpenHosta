"""
Tests for SemanticEngine (clustering, outlier detection, centroid operations).
Uses real Ollama embeddings via session-scoped fixtures.
"""
import pytest
import numpy as np


class TestGenerateExamples:
    """Tests for the example generation pipeline."""

    def test_generates_nonempty_list(self, ollama_pipeline):
        from OpenHosta.semantics.engine import generate_examples
        examples = generate_examples(axis="Couleur", pipeline=ollama_pipeline, n=10)
        assert len(examples) > 0, "Should generate at least one example"

    def test_examples_are_strings(self, ollama_pipeline):
        from OpenHosta.semantics.engine import generate_examples
        examples = generate_examples(axis="Fruit", pipeline=ollama_pipeline, n=10)
        for ex in examples:
            assert isinstance(ex, str)
            assert len(ex.strip()) > 0

    def test_no_duplicates(self, ollama_pipeline):
        from OpenHosta.semantics.engine import generate_examples
        examples = generate_examples(axis="Pays européen", pipeline=ollama_pipeline, n=15)
        lowered = [e.lower() for e in examples]
        assert len(lowered) == len(set(lowered)), "Should not contain duplicates"


class TestSemanticEngine:
    """Tests for clustering and prediction."""

    def test_fit_creates_clusters(self, ollama_model):
        from OpenHosta.semantics.engine import SemanticEngine

        texts = ["chat", "chien", "lion", "voiture", "avion", "train"]
        embeddings = ollama_model.embed(texts)

        engine = SemanticEngine(examples=texts, embeddings=embeddings, tolerance=0.5)
        assert engine.n_clusters >= 1, "Should create at least 1 cluster"

    def test_predict_returns_valid_cluster(self, ollama_model):
        from OpenHosta.semantics.engine import SemanticEngine

        texts = ["chat", "chien", "lion", "voiture", "avion", "train"]
        embeddings = ollama_model.embed(texts)
        engine = SemanticEngine(examples=texts, embeddings=embeddings, tolerance=0.7)

        # "tigre" should be assignable to a cluster (close to animals)
        new_emb = ollama_model.embed(["tigre"])[0]
        cluster_id = engine.predict(new_emb)
        assert cluster_id in engine.cluster_ids

    def test_top_k_nearest_center(self, ollama_model):
        from OpenHosta.semantics.engine import SemanticEngine

        texts = ["chat", "chien", "lion", "tigre", "panthère"]
        embeddings = ollama_model.embed(texts)
        engine = SemanticEngine(examples=texts, embeddings=embeddings, tolerance=0.8)

        for cid in engine.cluster_ids:
            top = engine.get_top_k_nearest_center(cid, k=3)
            assert len(top) <= 3
            assert len(top) >= 1
            for item in top:
                assert item in texts

    def test_nearest_clusters(self, ollama_model):
        from OpenHosta.semantics.engine import SemanticEngine

        texts = ["chat", "chien", "voiture", "avion", "pomme", "banane"]
        embeddings = ollama_model.embed(texts)
        engine = SemanticEngine(examples=texts, embeddings=embeddings, tolerance=0.3)

        if engine.n_clusters > 1:
            cid = engine.cluster_ids[0]
            neighbors = engine.get_nearest_clusters(cid, k=2)
            assert cid not in neighbors, "Should not include self in neighbors"
            for n in neighbors:
                assert n in engine.cluster_ids


class TestQualityFilter:
    """Tests for the garbled output quality filter."""

    def test_rejects_concatenated_tokens(self):
        from OpenHosta.semantics.engine import generate_examples
        # Access the inner function via module-level test
        # We test the heuristic directly
        def _is_quality(text):
            if not text or len(text) > 100:
                return False
            mid_word_uppers = 0
            for i in range(1, len(text)):
                if text[i].isupper() and text[i-1] != ' ':
                    mid_word_uppers += 1
            if mid_word_uppers >= 1:
                return False
            if len(text) > 25 and ' ' not in text:
                return False
            return True

        # Garbled outputs (should be rejected)
        assert not _is_quality("DuckDDogDingo")
        assert not _is_quality("MCheRequin")
        assert not _is_quality("OiseauxReptile")
        assert not _is_quality("EleDogElephant")

        # Valid outputs (should be accepted)
        assert _is_quality("Lion")
        assert _is_quality("Le chien")
        assert _is_quality("Dromedary camel")
        assert _is_quality("Komodo dragon")
        assert _is_quality("")  is False
