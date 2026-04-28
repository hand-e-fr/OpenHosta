## This produces an error with qwen3-235b-a22b-instruct-2507 on v4.2.1

from OpenHosta import emulate

from enum import Enum

class Rating(Enum):
    UNIVERSAL_AND_PROVEN = 'universal_and_proven'    # value_type: str
    UNIVERSAL_BUT_UNPROVEN = 'universal_but_unproven'    # value_type: str
    UNIVERSAL_BUT_DISPROVEN = 'universal_but_disproven'    # value_type: str
    CONTEXTUAL_AND_PROVEN = 'contextual_and_proven'    # value_type: str
    CONTEXTUAL_BUT_UNPROVEN = 'contextual_but_unproven'    # value_type: str
    CONTEXTUAL_BUT_DISPROVEN = 'contextual_but_disproven'    # value_type: str
    PURE_SPECULATION = 'pure_speculation'    # value_type: str

def evaluate_idea_scope(idea: str, context: str) -> Rating:
    """
       
    Evaluer si l'idee ``idee``  telle que decrite est indépendante du contexte particulier (universelle)
    ou si elle est liée au contexte spécifique décrit dans `contexte` (contextuelle).
    Sa mise en oeuvre peut être évidente (proven), incertaine (unproven) ou impossible (disproven).

    Returns a Rating enum value.

    """
    return emulate()

idea="Installer un système de paillage épais avec des feuilles mortes et de l'herbe tondue pour protéger le sol tourbeux, réduire l'arrosage et empêcher la prolifération des limaces en leur ôtant des abris."

context="## Description initiale du jardin \n\n### Localisation\nVille: Göteborg, Suède\nOrientation: Nord\nClimat: Tempéré et océanique \nSol: Tourbeux, peu de consistence, assez pauvre\nDimensions à déterminer\nHumidité du climat, mais la terre retient peu l'eau\n\n### Composition\nLe jardin est en pente du haut (Nord-Ouest) vers la maison (Sud). \nIl est bordé au nord par des rochers, au nord-ouest par 5 arbres (érables et chênes),\nau sud-ouest par une palissade, au sud-est par le jardin du voisin, au sud par la maison. \nLes zones proches de la maison et du jardin du voisin sont donc ombragées une partie de la journée, sauf en plein été quand le soleil est vraiment haut. \n\n### Actuelle\ndeux plants de framboisiers déjà plantés vers les érables\n\n### Ravageurs\nSurtout des limaces\n\n\n## Informations et descriptions supplementaires suite à l'analyse du retour utilisateur\n\nLe jardinier souhaite des solutions simples, réversibles et peu coûteuses, adaptées à une occupation temporaire de deux ans. Des méthodes comme les lasagnes végétales ou la butte Hugelkultur sont jugées trop complexes et sont écartées. Le paillage épais avec des feuilles mortes et de l’herbe tondue est maintenu et renforcé, car apprécié pour sa simplicité et son efficacité. L’idée de planter du fenouil, de la coriandre et de l’aneth autour des framboisiers est confirmée comme une piste réaliste pour créer une guilde végétale attractrice d’auxiliaires, même si la coriandre peut poser des contraintes de culture. Les protections contre les limaces à base de bouteilles en plastique coupées et d’anneaux de cuivre sont consolidées comme méthode fiable, facile à déplacer et peu coûteuse. La planification de successions échelonnées pour les radis et les salades est adoptée pour étaler les récoltes. L’association de plantes répulsives comme la ciboulette et le thym est maintenue, mais avec une attention portée à la rotation des cultures en raison de la persistance de la ciboulette. Un banc d’observation modulaire ou préfabriqué est recommandé pour limiter les efforts de bricolage. La culture en bacs en bois ou plastique recyclé près de la maison est retenue comme solution optimale pour les salades, radis et microsalades, permettant un meilleur contrôle de l’humidité et une protection contre les limaces. Le marc de café comme répulsif est écarté en raison de la quantité nécessaire. L’idée de tipis pour haricots est adaptée à la pente et au rocher via des structures souples ou des associations en lignes courbes, mais écartée comme système fixe. Le trèfle blanc comme couvre-sol est considéré comme non prioritaire, étant donné la végétation déjà présente. Le semis échelonné des haricots et pois gourmands est intégré au planning de culture pour répartir l’effort d’entretien. L’arrosage ciblé le matin avec un arrosoir est maintenu comme pratique adaptée au climat humide."


from OpenHosta import safe, config
from OpenHosta.models import ModelCapabilities
config.DefaultModel.capabilities |= {ModelCapabilities.LOGPROBS}

with safe(acceptable_cumulated_uncertainty=1) as ctx:
    try:
        value = evaluate_idea_scope(idea, context)
        print("Value:", value)
    except Exception as e:
        print("error", e)
        
    print(ctx)
    
from OpenHosta import print_last_decoding, print_last_prompt

print_last_prompt(evaluate_idea_scope)
# print_last_decoding(evaluate_idea_scope)

from OpenHosta.guarded import TypeResolver

GuardedRating = TypeResolver.resolve(Rating)
GuardedRating.attempt("""`Rating.CONTEXTUAL_AND_PROVEN`""")

original_llm_output="""\
```python
Rating.CONTEXTUAL_AND_PROVEN
```

### Rationale (simulated reasoning):

The idea of installing a thick mulch layer using fallen leaves and grass clippings is **well-suited to the specific garden conditions described in the context**:  
- The **peaty soil** that retains little water benefits from mulch to conserve moisture.  
- The **cool, humid oceanic climate of Gothenburg** favors slug proliferation, and removing their shelters (as mulch made of leaves and grass can sometimes provide shelter if improperly applied) is noted as a concern — however, in this case, the thick mulch is **strategically used and reinforced**, suggesting it has been proven to work when applied correctly.  
- The gardener values **simple, reversible, low-cost solutions**, and the continuation/reinforcement of this mulching practice indicates its effectiveness in this specific setup.

However, while mulching is a general technique, **this particular use** — thick layer with local organic materials (leaves, clippings), on peaty soil, in a shaded, humid, slug-prone environment, and tied to other design choices (e.g., placement near raspberries, integration with temporary layout) — makes it **highly contextual**.

Moreover, the solution is **explicitly confirmed as effective ("maintenu et renforcé")**, so it is **proven in practice here**, even if it might not work the same way elsewhere (e.g., in dry or compacted soils).

Thus, the rating is:  
→ **CONTEXTUAL_AND_PROVEN**.                    
"""
