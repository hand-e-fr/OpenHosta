
from OpenHosta.semantics import SemanticSet


# Créer un ensemble de tâches ménagères

# Annotation optionnelle pour la clarté
SemanticSet[HostaSemanticLocation("Type de Tâche")]

def get_locaton(compte_rendu_de_fin_dannee:str) -> FuzzyEnum("Type de Tâche"):
    """
    Quelle est la tache préférée de l'employé d'après son compte rendu de fin d'année ?
    :param compte_rendu_de_fin_dannee: Compte rendu de fin d'année de l'employé
    :return: Type de tâche préférée de l'employé
    :raises: ValueError si le compte rendu de
    """
    return emulate()

class CrLastYear:
    email: str
    cr:str = """l'an dernier j'ai bien aimé...."""

cr1 = CrLastYear(id=3324324)

TaskType = FuzzyEnum("Type de tache", model_location="https://object_storage.com/hande/project1/TakType.json@V1.0.1")

RainbowColorsType = FuzzyEnum("Les couleurs de l'arc en ciel indépendament de la lague (violet, bleu, vert, jaune, orange, rouge)")

RainbowColorsType.save("mylib/rainboxtype.py", format='python')

RainbowColorsType.save_dataset("mylib/rainboxtype.json", format='json')


if Path("mylib/rainboxtype.py").exists():
    RainbowColorsType = FuzzyEnum.load("mylib/rainboxtype.py")
else:
    RainbowColorsType = FuzzyEnum("Les couleurs de l'arc en ciel indépendament de la lague (violet, bleu, vert, jaune, orange, rouge)")

# import pickle

# with open("mylib/rainboxtype.pkl", "wb") as fp:
#     pickle.dump(RainbowColorsType, fp)
    
# with open("mylib/rainboxtype.pkl" "rb") as fp:
#     RainbowColorsType = pickle.load(fp)

# my_code = compile(RainbowColorsType, toolkit="scikit-learn")

# with open("mylib/rainboxtype.py", "w") as fp:
#     fp.write(my_code)

cleaned_anchors = RainbowColorsType.anchors
CleanedRainbowColorsType = FuzzyCleaner("axe ", cleaned_anchors)

WhoLikesWhatDict = SemanticDict[TaskType, GuardedCorporateEmail]

qui_fait_quoi:WhoDoesWhatDict = WhoDoesWhatDict()

with safe(max_uncertainty=0.1) as ctx:
    
    task = get_locaton(cr1.cr)
    verified_email = GuardedCorporateEmail(cr1.email)
    qui_fait_quoi[task] = verified_email

from dataclasses import dataclass

@dataclass
class CrLastYear2:
    email:CorporateEmail
    cr:TaskType = """l'an dernier j'ai bien aimé...."""

my_cr2027 = CrLastYear2(email=GuardedEmail("john.doe@alstom.com"), cr=TaskType("j'ai bien aimé laver le sol"))

## Ordre 1
tasks = SemanticSet(axis="Taches Ménagères", tolerance=0.15)
tasks.add("Laver le sol")
tasks.add("Passer la serpillière")  # Détecté comme doublon sémantique
tasks.add("Faire la vaisselle")     # Nouveau cluster

## Ordre 2
tasks = SemanticSet(axis="Taches Ménagères", tolerance=0.15)
tasks.add("Passer la serpillière")  # Détecté comme doublon sémantique
tasks.add("Faire la vaisselle")     # Nouveau cluster
tasks.add("Laver le sol")


tasks = SemanticSet(axis="Tache par type d'outils", tolerance=0.15)
tasks.add("Laver le sol")
tasks.add("Passer la serpillière")  # Détécté comme différent (outil différent)

# Indépendant de l'ordre d'ajout
print(tasks)
# Output probable : {"Nettoyage des sols", "Vaisselle"} (Labels synthétisés)

# utilisation qwen embedding
CapitalesEurope = SemanticSet(axis="Villes Touristiques Européennes", tolerance=0.15)
CapitalesEurope.add("Paris")
CapitalesEurope.add("Lyon")   # dist cosin 0.017 avec Paris
CapitalesEurope.add("Londres")
CapitalesEurope.add("Berlin")

CapitalesEurope.add("Annecy")  # Pas une capitale touristique => raise ValueError

print(CapitalesEurope)
# Output probable : {"Capitale de la France", "Capitale du Royaume-Uni", "Capitale de l'Allemagne"}

GuardedUtf8 = str

FastGuarded = GuardedUtf8 # Guarded Scalar

# SemanticLocation étend GuardedTypes

def StrWithLevingsteinfDist(str, SemanticLocation):
    
    def __init__(self, value: str):
        self._location:list[float] = embedding(str)
        
        super().__init__(value)

    def __sub__(self, other):
        """distance sémantique [0,1[ en échelle logprobe
        0: match str exacte
        1: comparaison avec distance(value, None)
        proba que les deux soient identiques = 1 - distance
        """
        return abs(self._location - other._location)
        return Levenshtein.distance(self, other)
 
ville_a = MyBigFrenchCity("Paris")  # OK
ville_b = MyBigFrenchCity("Lyon")   # OK
c = MyBigFrenchCity("Annecy") # ValueError : Pas une grande ville française

ville_a - ville_b # Distance sémantique

from typing import Set
SemanticSet = Set

FenchCitySetType = SemanticSet[MyBigFrenchCity]
FenchCitySetByMistralType = SemanticSet[MyBigFrenchCity]
FenchCitySetByQwen3Type = SemanticSet[MyBigFrenchCity]

from pydantic import TypeAdapter, ValidationError

date = {
    "villes": ["Paris", "Lyon", "Marseille"]
}

try:
    validated_data = TypeAdapter[FenchCitySetByQwen3Type].validator(data)
except ValidationError as e:
    print(e)
    
mes_villes_visites_dapres_qwen:FenchCitySetByQwen3Type = FenchCitySetByQwen3Type()
mes_villes_visites_dapres_mistral:FenchCitySetByMistralType  = FenchCitySetByMistralType()

mes_villes_visites.add("Paris")
mes_villes_visites2:SemanticSet[MyBigFrenchCity]  = SemanticSet[MyBigFrenchCity]()

ma_class:MaClass = MaClass()

ma_list:list = ["Paris", "Lyon", "Annecy"]

VillesFrancaises:
VillesFrancaises.add("Paris")
VillesFrancaises.add("Lyon")  # dist cosin 0.017 avec Paris
VillesFrancaises.add("Annecy")  # dist cosin 0.012 avec Paris

print(VillesFrancaises)
# Output probable : {"Capitale de la France", "Ville de province"}