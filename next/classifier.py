from dataclasses import dataclass
from typing import Literal

# --- Définition des axes de classification ---

# L'objectif principal de l'idée
DomaineType = Literal[
    "Lutte anti-nuisibles", 
    "Gestion de l'eau et du sol", 
    "Aménagement de l'espace", 
    "Stratégie de culture", 
    "Biodiversité et synergies"
]

# Le moyen d'action utilisé pour arriver à cet objectif
MethodeType = Literal[
    "Protection physique", 
    "Association végétale", 
    "Organisation temporelle", 
    "Infrastructure matérielle", 
    "Pratique d'entretien"
]

@dataclass(frozen=True)
class CleClassification:
    """
    Clé permettant de regrouper les idées de jardinage.
    Le paramètre frozen=True permet d'utiliser cette dataclass comme clé dans un dictionnaire.
    """
    domaine: DomaineType
    methode: MethodeType

from OpenHosta import emulate, emulate_async

async def classifier(idee: str) -> CleClassification:
    """
    Classifie une idée de jardinage en fonction de son domaine et de sa méthode.
    """
    return await emulate_async()

from OpenHosta import gather_data

with open("../next/liste_idees_a_selectionner.md", 'r') as file:
    text = file.read()

data = [classifier(x.strip()) for x in text.split("---")[:2] if x.strip()]

from OpenHosta import print_last_prompt, print_last_decoding, reload_dotenv
reload_dotenv()
#gather_data(data[:1])
gather_data(data)

gather_data(data, max_delay=1200)
for k,v in data.items():
    print(k,v.val())

print_last_prompt(classifier)
print_last_decoding(classifier)

