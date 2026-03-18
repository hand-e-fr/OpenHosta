# 📖 Documentation OpenHosta.semantics

**OpenHosta.semantics** est le module qui gère la **distance sémantique** entre concepts via embeddings et graphes de connaissances. Il permet de comparer, regrouper et organiser des données par leur **sens** plutôt que par leur syntaxe.


## I. Introduction : Distance Sémantique

En informatique classique, le test `if "Chat" == "Félin":` est toujours **Faux**.  
Avec OpenHosta.semantics, nous introduisons une mesure de distance. Si deux concepts sont suffisamment proches dans l'espace vectoriel du sens suvant un axe donné, nous considérons qu'ils sont **égaux**.

### Le Principe

```python
from OpenHosta.semantics import SemanticSet

# Créer un ensemble sémantique
animals = SemanticSet(axis="Type d'animal", tolerance=0.15)
animals.add("Chat")
animals.add("Félin")  # Détecté comme similaire à "Chat"
animals.add("Chaton")
animals.add("Chien")
animals.add("Canin")

print(len(animals))  # 2 (regroupés sémantiquement)
print(animals)
# Output probable : {"Chat", "Chien"}
```

---

## II. Types Sémantiques Disponibles


| Type | Description | Statut |
|------|-------------|--------|
| `SemanticSet` | Ensemble avec clustering sémantique | x |
| `SemanticDict` | Dictionnaire avec index spatial | x |


## III. SemanticSet : L'Ensemble Auto-Synthétisé

Un `SemanticSet` regroupe les éléments par "clusters" de sens. Il est idéal pour dédupliquer des listes d'idées ou de tâches.

### Fonctionnalités

* **Ajout intelligent** : Si vous ajoutez un synonyme, il rejoint le groupe existant sans créer de doublon
* **Auto-Labelling** : La liste des groupes est précalculée au moment de la création de l'instance et dépend de la tolérance, de l'axe sémantique et du modèle d'embedding utilisé. 
* **Clustering** : Les éléments sont regroupés par similarité sémantique d'après le clustering précalculé.

### Exemple d'Utilisation

```python
from OpenHosta.semantics import SemanticSet


# Créer un ensemble de tâches ménagères

# Annotation optionnelle pour la clarté
SemanticSet[SemanticAxis("Type de Tâche")]

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

def MyBigFrenchCity(GuardedUtf8):
    _type_fr = """"Villes Françaises de plus de 1M d'habitants"""
    _tolerance=0.15
    
    def _parse_semantics(self, value):
        """Valide que la ville est une grande ville française."""
        return value

    def _parse_knowledge(self, value):
        """Compare la ville à une liste de grandes villes françaises."""
        if value not in ["Paris", "Lyon", "Marseille"]:
            raise ValueError(f"{value} n'est pas une grande ville française.")
        
        return value
 
MyBigFrenchCity("Paris")  # OK
MyBigFrenchCity("Lyon")   # OK
MyBigFrenchCity("Annecy") # ValueError : Pas une grande ville française

FenchCitySetType = SemanticSet[MyBigFrenchCity]

mes_villes_visites:FenchCitySetType  = FenchCitySetType()
mes_villes_visites:SemanticSet[MyBigFrenchCity]  = SemanticSet[MyBigFrenchCity]()

ma_class:MaClass = MaClass()

ma_list:list = ["Paris", "Lyon", "Annecy"]

VillesFrancaises:
VillesFrancaises.add("Paris")
VillesFrancaises.add("Lyon")  # dist cosin 0.017 avec Paris
VillesFrancaises.add("Annecy")  # dist cosin 0.012 avec Paris

print(VillesFrancaises)
# Output probable : {"Capitale de la France", "Ville de province"}
```


### 3.3 Configuration

```python
from OpenHosta.semantics import SemanticSet, Tolerance

# Contrôler la sensibilité du clustering
strict_set = SemanticSet(tolerance=Tolerance.PRECISE)   # Clusters stricts
flexible_set = SemanticSet(tolerance=Tolerance.FLEXIBLE)  # Clusters larges
```

---

## IV. SemanticDict : Le Dictionnaire à Boussole

Contrairement au `dict` Python qui utilise le hachage (égalité stricte), le `SemanticDict` utilise un **index spatial** (BallTree). Il permet de retrouver une valeur à partir d'une clé *approximative*.

### 4.1 Fonctionnalités

* **Recherche floue** : Retrouver une valeur même si la clé n'est pas exacte
* **Index spatial** : Utilise BallTree pour la recherche rapide
* **Tolérance configurable** : Contrôler la distance maximale acceptée

### 4.2 Exemple d'Utilisation

```python
from OpenHosta.semantics import SemanticDict

# Créer un routeur sémantique
router = SemanticDict(axis="Animal", tolerance=0.15)
router["Chien"] = "Wouf"
router["Chat"] = "Miaou"

# Recherche floue
print(router["Mon petit toutou"])  # "Wouf" (proche de "Chien")
print(router["Félin"])             # "Miaou" (proche de "Chat")
```

### 4.3 Cas d'Usage

**Routage de Commandes** :
```python
command_router = SemanticDict(axis="Tache par type d'outils", tolerance=0.15)
command_router["créer un fichier"] = create_file_handler
command_router["supprimer un dossier"] = delete_folder_handler

# L'utilisateur peut utiliser des variantes
handler = command_router["faire un nouveau fichier"]  # → create_file_handler
```

**Traduction Contextuelle** :
```python
translations = SemanticDict(axis="Salutation", tolerance=0.15)
translations["bonjour"] = "hello"
translations["au revoir"] = "goodbye"

# Fonctionne avec des variantes
print(translations["salut"])  # "hello"
print(translations["bye"])    # "goodbye"
```

## Conclusion

**Utilisez `semantics`** pour :
- Regrouper des concepts similaires (`SemanticSet`)
- Recherche floue par clé (`SemanticDict`)
- Comparaison sémantique d'attributs
- Validation croisée de modèles

**Utilisez `guarded`** pour :
- Valider et convertir des entrées utilisateur
- Parser des données sales
- Typage avec tolérance configurable