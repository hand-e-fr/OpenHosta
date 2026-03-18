"""
Test manuel pour SemanticSet et SemanticDict.
Nécessite un modèle avec embeddings configuré (OpenAI ou Ollama).

Usage:
    python tests/manual/test_semantic_manual.py
"""
from dotenv import load_dotenv
load_dotenv()

from OpenHosta import config, reload_dotenv
reload_dotenv()

from OpenHosta.core.base_model import ModelCapabilities
config.DefaultModel.capabilities |= {ModelCapabilities.LOGPROBS}

from OpenHosta.semantics import SemanticSet, SemanticDict


def test_semantic_set():
    print("\n" + "=" * 60)
    print("TEST: SemanticSet")
    print("=" * 60)

    print("\n--- Creating SemanticSet(axis='Type d\\'animal') ---")
    animals = SemanticSet(axis="Type d'animal", tolerance=0.15, n_examples=30)

    print(f"\nGenerated {len(animals.generated_examples)} examples:")
    for ex in animals.generated_examples[:10]:
        print(f"  - {ex}")
    if len(animals.generated_examples) > 10:
        print(f"  ... and {len(animals.generated_examples) - 10} more")

    print(f"\nClusters: {len(animals)}")
    print(f"Labels: {animals}")

    print("\n--- Adding items ---")
    for item in ["Chat", "Félin", "Chien", "Canin", "Poisson"]:
        try:
            cluster_id = animals.add(item)
            label = animals.cluster_of(item)
            print(f"  ✅ '{item}' → cluster '{label}'")
        except ValueError as e:
            print(f"  ❌ '{item}' → ValueError: {e}")

    print("\n--- Testing outlier detection ---")
    try:
        animals.add("Calculatrice quantique")
        print("  ❌ 'Calculatrice quantique' was NOT rejected (unexpected)")
    except ValueError as e:
        print(f"  ✅ 'Calculatrice quantique' correctly rejected: {e}")

    print(f"\n--- Members ---")
    for cluster in animals.clusters():
        print(f"  {cluster['label']}: {cluster['members']}")

    print(f"\n--- Contains test ---")
    print(f"  'Chaton' in animals: {'Chaton' in animals}")
    print(f"  'Ordinateur' in animals: {'Ordinateur' in animals}")


def test_semantic_dict():
    print("\n" + "=" * 60)
    print("TEST: SemanticDict")
    print("=" * 60)

    print("\n--- Creating SemanticDict(axis='Animal') ---")
    router = SemanticDict(axis="Animal", tolerance=0.15, n_examples=30)

    print(f"\nClusters: {len(router.key_set)}")
    print(f"Labels: {router.key_set}")

    print("\n--- Setting items ---")
    router["Chien"] = "Wouf"
    router["Chat"] = "Miaou"
    print(f"  router['Chien'] = 'Wouf'")
    print(f"  router['Chat'] = 'Miaou'")

    print("\n--- Fuzzy lookup ---")
    for query in ["Mon petit toutou", "Félin", "Chien", "Chat"]:
        try:
            result = router[query]
            print(f"  router['{query}'] → '{result}'")
        except KeyError as e:
            print(f"  router['{query}'] → KeyError: {e}")

    print(f"\n--- Dict info ---")
    print(f"  len: {len(router)}")
    print(f"  keys: {list(router.keys())}")
    print(f"  repr: {router}")


if __name__ == "__main__":
    test_semantic_set()
    test_semantic_dict()
    print("\n✅ All manual tests completed.")
