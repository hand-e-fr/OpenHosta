# 📖 Documentation OpenHosta.semantics

**OpenHosta.semantics** est le module qui gère la **distance sémantique** entre concepts via embeddings et graphes de connaissances. Il permet de comparer, regrouper et organiser des données par leur **sens** plutôt que par leur syntaxe.

> **Note** : Ce module est en cours de refactoring. Les types de validation de base (`SemanticInt`, `SemanticStr`, etc.) ont été déplacés vers le module [`guarded`](./guarded.md).

---

## I. Introduction : Distance Sémantique

En informatique classique, le test `if "Chat" == "Félin":` est toujours **Faux**.  
Avec OpenHosta.semantics, nous introduisons une mesure de distance. Si deux concepts sont suffisamment proches dans l'espace vectoriel du sens, nous considérons qu'ils sont **égaux**.

### Le Principe

```python
from OpenHosta.semantics import SemanticSet

# Créer un ensemble sémantique
animals = SemanticSet()
animals.add("Chat")
animals.add("Félin")  # Détecté comme similaire à "Chat"

print(len(animals))  # 1 (regroupés sémantiquement)
```

---

## II. Types Sémantiques Disponibles

> ⚠️ **Module en refactoring** : Seuls les types suivants resteront dans `semantics`. Les autres ont été déplacés vers `guarded`.

### Types Actuels

| Type | Description | Statut |
|------|-------------|--------|
| `SemanticSet` | Ensemble avec clustering sémantique | ✅ Conservé |
| `SemanticDict` | Dictionnaire avec index spatial | ✅ Conservé |
| `SemanticAttribute` | Attribut avec distance sémantique | ✅ Conservé |
| `SemanticModel` | Modèle avec validation sémantique | ✅ Conservé |

### Types Déplacés vers `guarded`

Les types suivants sont maintenant dans le module [`guarded`](./guarded.md) :
- `SemanticInt` → `GuardedInt`
- `SemanticStr` → `GuardedUtf8`
- `SemanticFloat` → `GuardedFloat`
- `SemanticBool` → `GuardedBool`
- `SemanticList` → `GuardedList`
- `SemanticTuple` → `GuardedTuple`

---

## III. SemanticSet : L'Ensemble Auto-Synthétisé

Un `SemanticSet` regroupe les éléments par "clusters" de sens. Il est idéal pour dédupliquer des listes d'idées ou de tâches.

### 3.1 Fonctionnalités

* **Ajout intelligent** : Si vous ajoutez un synonyme, il rejoint le groupe existant sans créer de doublon
* **Auto-Labelling** : Le nom du groupe est recalculé dynamiquement pour représenter le "centre de gravité" des éléments qu'il contient
* **Clustering** : Les éléments sont regroupés par similarité sémantique

### 3.2 Exemple d'Utilisation

```python
from OpenHosta.semantics import SemanticSet

# Créer un ensemble de tâches ménagères
tasks = SemanticSet()
tasks.add("Laver le sol")
tasks.add("Passer la serpillière")  # Détecté comme doublon sémantique
tasks.add("Faire la vaisselle")     # Nouveau cluster

print(tasks)
# Output probable : {"Nettoyage des sols", "Vaisselle"} (Labels synthétisés)
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
router = SemanticDict()
router["Chien"] = "Wouf"
router["Chat"] = "Miaou"

# Recherche floue
print(router["Mon petit toutou"])  # "Wouf" (proche de "Chien")
print(router["Félin"])             # "Miaou" (proche de "Chat")
```

### 4.3 Cas d'Usage

**Routage de Commandes** :
```python
command_router = SemanticDict()
command_router["créer un fichier"] = create_file_handler
command_router["supprimer un dossier"] = delete_folder_handler

# L'utilisateur peut utiliser des variantes
handler = command_router["faire un nouveau fichier"]  # → create_file_handler
```

**Traduction Contextuelle** :
```python
translations = SemanticDict()
translations["bonjour"] = "hello"
translations["au revoir"] = "goodbye"

# Fonctionne avec des variantes
print(translations["salut"])  # "hello"
print(translations["bye"])    # "goodbye"
```

---

## V. SemanticAttribute : Attributs avec Distance

Un `SemanticAttribute` est un attribut de classe qui peut être comparé sémantiquement.

### 5.1 Utilisation

```python
from OpenHosta.semantics import SemanticAttribute

class Product:
    category = SemanticAttribute()
    
    def __init__(self, category):
        self.category = category

# Comparaison sémantique
laptop = Product("Ordinateur portable")
computer = Product("PC")

# Les catégories sont sémantiquement proches
if laptop.category == computer.category:  # True (sémantiquement)
    print("Même catégorie")
```

---

## VI. SemanticModel : Modèles avec Validation Sémantique

Un **`SemanticModel`** permet de définir des objets complexes composés de plusieurs champs, et de les instancier directement depuis du langage naturel non structuré.

> ⚠️ **En refactoring** : La documentation complète sera mise à jour après la refonte du module.

### 6.1 Définition d'un Modèle

```python
from OpenHosta.semantics import SemanticModel

class ClientProfile(SemanticModel):
    """Profil structuré d'un client entreprise."""
    first_name: str
    last_name: str
    email: str
    segment: str  # VIP, Regular, New Lead
    tags: list[str]
```

### 6.2 Extraction Sémantique

```python
raw_text = """
J'ai eu Jean Dupont au téléphone, il fait partie du groupe mycorp-group.net. 
C'est un client VIP. Notez qu'il est intéressé par l'offre cloud.
"""

# Instanciation depuis le chaos
client = ClientProfile(raw_text)

print(client.first_name)  # "Jean"
print(client.last_name)   # "Dupont"
print(client.email)       # "jean.dupont@mycorp-group.net"
print(client.segment)     # "VIP"
print(client.tags)        # ["cloud", "intéressé"]
```

### 6.3 Validation Croisée (Coherence Check)

Une fonctionnalité unique aux `SemanticModel` est la capacité de valider la logique *entre* les champs.

```python
class JobOffer(SemanticModel):
    title: str
    salary: int

    def validate_coherence(self):
        """
        Méthode spéciale appelée après l'instanciation.
        Vérifie la cohérence sémantique entre les champs.
        """
        # Si le salaire est < 20k et le titre est "Senior Engineer", 
        # c'est sémantiquement louche
        pass
```

---

## VII. Le Moteur de Comparaison

### 7.1 Stratégies de Comparaison

Lorsque vous faites `if variable == concept`, OpenHosta choisit dynamiquement la meilleure stratégie :

* **Stratégie Vectorielle (Rapide)** : Pour les tolérances standards, utilise la distance cosinus entre les embeddings
* **Stratégie Générative (Précise)** : Pour les tolérances très strictes, utilise le LLM pour vérifier les nuances (négation, antonymes proches)

### 7.2 Tolérance et Distance

La `semantic_tolerance` définit la distance maximale acceptée pour considérer deux concepts comme égaux.

```python
from OpenHosta.semantics import Tolerance

# Guide des tolérances pour la distance sémantique
Tolerance.STRICT     # 0.00 - Égalité exacte uniquement
Tolerance.PRECISE    # 0.05 - Synonymes directs
Tolerance.FLEXIBLE   # 0.15 - Concepts liés (défaut)
Tolerance.CREATIVE   # 0.30 - Thématique commune
```

| Niveau | Constante | Distance | Exemple |
|--------|-----------|----------|---------|
| **Strict** | `STRICT` | 0.00 | "Chat" == "Chat" uniquement |
| **Précis** | `PRECISE` | 0.05 | "Chat" == "chat" (casse) |
| **Flexible** | `FLEXIBLE` | 0.15 | "Chat" == "Félin" |
| **Créatif** | `CREATIVE` | 0.30 | "Chat" == "Animal domestique" |

---

## VIII. Performance des Embeddings

### 8.1 Calcul et Cache

Les vecteurs sont calculés de manière "Lazy" (uniquement au besoin) et mis en cache. Cependant, le premier appel pour un nouveau texte déclenche une requête (locale ou API).

**Bonnes pratiques** :
* Privilégiez l'instanciation unique de vos objets sémantiques
* Utilisez `SemanticSet` pour traiter des lots de données textuelles massifs
* Pré-calculez les embeddings pour les données fréquemment utilisées

### 8.2 Backends Supportés

OpenHosta supporte plusieurs backends pour les embeddings :
* **Local** : Modèles Sentence-Transformers
* **API** : OpenAI, Cohere, etc.
* **Custom** : Implémentez votre propre backend

---

## IX. Limitations et Bonnes Pratiques

### 9.1 Hachage et Dictionnaires Natifs

> [!CAUTION]
> **Ne jamais utiliser** un type sémantique comme clé dans un `dict` Python standard (`{}`).
> Pour garantir le "Flou Maîtrisé", les types sémantiques surchargent l'égalité (`__eq__`) mais rendent l'objet **non-hachable**. Python lèvera une erreur `TypeError: unhashable type`. Utilisez toujours `SemanticDict`.

### 9.2 Coût des Comparaisons

> [!WARNING]
> **Attention au coût** : Une tolérance **STRICT** ou **PRECISE** (< 0.05) force souvent l'utilisation du LLM pour valider l'égalité, ce qui est plus lent et coûteux que la comparaison vectorielle utilisée par **FLEXIBLE**.

### 9.3 Choix de la Tolérance

Ne choisissez pas un chiffre au hasard. Utilisez les constantes fournies pour définir votre **intention** :

```python
from OpenHosta.semantics import Tolerance

# Pour des IDs, codes, mots de passe
strict_field = SemanticAttribute(tolerance=Tolerance.STRICT)

# Pour des catégories, tags (défaut)
flexible_field = SemanticAttribute(tolerance=Tolerance.FLEXIBLE)

# Pour du brainstorming, idéation
creative_field = SemanticAttribute(tolerance=Tolerance.CREATIVE)
```

---

## X. Migration depuis l'Ancienne API

Si vous utilisez l'ancienne API avec `SemanticInt`, `SemanticStr`, etc., migrez vers le module `guarded` :

### Avant (Ancien)
```python
from OpenHosta.semantics import SemanticInt, SemanticStr

age = SemanticInt("42")
name = SemanticStr("Alice")
```

### Après (Nouveau)
```python
from OpenHosta.guarded import GuardedInt, GuardedUtf8

age = GuardedInt("42")
name = GuardedUtf8("Alice")
```

**Changements** :
- `SemanticInt` → `GuardedInt`
- `SemanticStr` → `GuardedUtf8`
- `SemanticFloat` → `GuardedFloat`
- `SemanticBool` → `GuardedBool`
- `SemanticList` → `GuardedList`

**Les types sémantiques restants** (`SemanticSet`, `SemanticDict`, `SemanticAttribute`, `SemanticModel`) restent dans le module `semantics`.

---

## XI. Roadmap

### En Cours de Développement

- [ ] Refactoring complet du module `semantics`
- [ ] Amélioration des algorithmes de clustering
- [ ] Support de graphes de connaissances
- [ ] Optimisation des performances d'embedding
- [ ] Documentation complète de `SemanticModel`

### Types Maintenus

Les types suivants resteront dans `semantics` après le refactoring :
- ✅ `SemanticSet` - Clustering sémantique
- ✅ `SemanticDict` - Index spatial
- ✅ `SemanticAttribute` - Comparaison sémantique
- ✅ `SemanticModel` - Validation croisée

---

## XII. Ressources

- **Module guarded** : [`docs/guarded.md`](./guarded.md) - Types de validation
- **Code source** : `src/OpenHosta/semantics/`
- **Exemples** : À venir après refactoring

---

## XIII. Conclusion

Le module `semantics` se concentre désormais sur la **distance sémantique** et le **clustering** de concepts. Pour la **validation et conversion de types**, utilisez le module [`guarded`](./guarded.md).

**Utilisez `semantics`** pour :
- Regrouper des concepts similaires (`SemanticSet`)
- Recherche floue par clé (`SemanticDict`)
- Comparaison sémantique d'attributs
- Validation croisée de modèles

**Utilisez `guarded`** pour :
- Valider et convertir des entrées utilisateur
- Parser des données sales
- Typage avec tolérance configurable