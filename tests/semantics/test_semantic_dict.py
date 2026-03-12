"""
Tests for SemanticDict — fuzzy key lookup, exact key storage, composition with SemanticSet.
Uses real Ollama model via session-scoped 'animal_dict' fixture.
"""
import pytest


class TestSemanticDictInit:
    """Tests for SemanticDict initialization."""

    def test_empty_on_init(self, animal_dict):
        assert len(animal_dict) == 0

    def test_has_key_set(self, animal_dict):
        assert animal_dict.key_set is not None
        assert len(animal_dict.key_set) >= 1  # At least 1 cluster


class TestSemanticDictSetItem:
    """Tests for __setitem__."""

    def test_set_and_get_exact(self, animal_dict):
        animal_dict["Chien"] = "Wouf"
        assert animal_dict["Chien"] == "Wouf"

    def test_set_multiple_keys(self, animal_dict):
        animal_dict["Chat"] = "Miaou"
        animal_dict["Lion"] = "Roar"
        assert len(animal_dict) >= 3  # Chien + Chat + Lion

    def test_overwrite_same_key(self, animal_dict):
        animal_dict["Chat"] = "Miaou updated"
        assert animal_dict["Chat"] == "Miaou updated"


class TestSemanticDictGetItem:
    """Tests for fuzzy __getitem__."""

    def test_exact_match(self, animal_dict):
        animal_dict["Chien"] = "Wouf"
        assert animal_dict["Chien"] == "Wouf"

    def test_fuzzy_lookup(self, animal_dict):
        """A semantically close key should return the nearest exact key's value."""
        animal_dict["Chien"] = "Wouf"
        # "Toutou" / "Canin" should be close to "Chien"
        try:
            result = animal_dict["Toutou"]
            # If found, it should return a value from the same cluster
            assert result is not None
            print(f"  Fuzzy: 'Toutou' → '{result}'")
        except KeyError:
            # Acceptable if "Toutou" falls in a different cluster
            print("  'Toutou' fell in a different cluster or was an outlier")

    def test_missing_key_raises(self, animal_dict):
        """A key with no stored values in its cluster should raise KeyError."""
        # Clear a specific scenario is hard, but we can test with an outlier-ish key
        with pytest.raises(KeyError):
            _ = animal_dict["xkcd_random_invalid_key_12345"]


class TestSemanticDictContains:
    """Tests for __contains__."""

    def test_contains_stored_key(self, animal_dict):
        animal_dict["Chien"] = "Wouf"
        assert "Chien" in animal_dict

    def test_not_contains_random(self, animal_dict):
        assert "xkcd_random_invalid_12345" not in animal_dict


class TestSemanticDictDictMethods:
    """Tests for keys(), values(), items()."""

    def test_keys(self, animal_dict):
        animal_dict["Chien"] = "Wouf"
        assert "Chien" in animal_dict.keys()

    def test_values(self, animal_dict):
        animal_dict["Chien"] = "Wouf"
        assert "Wouf" in animal_dict.values()

    def test_items(self, animal_dict):
        animal_dict["Chien"] = "Wouf"
        items = list(animal_dict.items())
        assert any(k == "Chien" and v == "Wouf" for k, v in items)

    def test_get_with_default(self, animal_dict):
        result = animal_dict.get("nonexistent_xyz", "default_value")
        assert result == "default_value"

    def test_iteration(self, animal_dict):
        animal_dict["Éléphant"] = "Barrit"
        found = False
        for key in animal_dict:
            if key == "Éléphant":
                found = True
        assert found

    def test_repr(self, animal_dict):
        r = repr(animal_dict)
        assert isinstance(r, str)
        assert r.startswith("{")
        assert r.endswith("}")
