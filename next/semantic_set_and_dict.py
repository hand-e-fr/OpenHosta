## Lidée ici est de disposer d'un dictionnaire ou d'un ensemble sémantique
## c'est à dire où les clés sont comparées selon leur similarité sémantique
## et non par égalité stricte.

# class SemanticType:
#     """
#     Metaclass that generate semantic types based on a semantic description.
#     The semantic description is used to compare instances of the type inside an LLM latent space.
#     """
#     pass


def example():
    
    from OpenHosta.semantics import SemanticSet, SemanticDict, SemanticType
    from OpenHosta import config

    from typing import Set

    class Salutations(SemanticType):
        """Type sémantique pour les salutations.""" 
        uncertainty_threshold=0.99
    
    salutations:Set[SemanticType, str] = SemanticSet(type=Salutations, uncertainty_threshold=0.75)
    salutations:SemanticSet[Salutations, str] = SemanticSet(type=Salutations, uncertainty_threshold=0.75)
    salutations += {"Hello world"}
    salutations += {"Hi there"}
    salutations += {"Hi ther"}
    salutations += {"Greetings planet"}

    print("Semantic Set contents:")
    for item in salutations:
        print(f"- {item}")
        
    ## Print restults
    #
    # Semantic Set contents:
    # - Hello world
    # - Hi there   # This is considered similar to "Hi ther"
    # - Greetings planet

    class Animals(SemanticType):
        """Type sémantique pour les animaux."""
        uncertainty_threshold=0.75
        
    animals = SemanticDict(key_type=Animals)
    animals["Dog"] = "a domesticated carnivorous mammal."
    animals["Cat"] = "A small domesticated carnivorous mammal."
    animals["cat"] = "a small domesticated carnivorous mammal."
    animals["Elephant"] = "a large herbivorous mammal."
    
    print("Semantic Dict contents:")
    for key in animals:
        print(f"- {key}: {animals[key]}")
        
    ## Print results
    #
    # Semantic Dict contents:
    # - Dog: a domesticated carnivorous mammal.
    # - Cat: a small domesticated carnivorous mammal.  # "Cat" and "cat" are considered similar sot the second assignment replaced the first
    # - Elephant: a large herbivorous mammal.