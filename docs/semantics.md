
# 📖 Documentation OpenHosta.semantics

**OpenHosta.semantics** est le module qui transforme Python en un langage de programmation **probabiliste et sémantique**. Il permet de manipuler des données non plus par leur syntaxe (les bits qui les composent), mais par leur **sens** (leur intention).

Il réconcilie deux mondes : la **Rigueur** du typage fort et la **Flexibilité** de l'Intelligence Artificielle.

---

## I. Les Fondamentaux : Du "Vrai/Faux" au "Flou Maîtrisé"

En informatique classique, le test `if "Chat" == "Félin":` est toujours **Faux**.
Avec OpenHosta, nous introduisons une mesure de distance. Si deux concepts sont suffisamment proches dans l'espace vectoriel du sens, nous considérons qu'ils sont **égaux**.

### Le Type Sémantique (`SemanticType`)

C'est l'atome de la bibliothèque. Un `SemanticType` est une "Primitive Intelligente" (Smart Primitive). Elle se comporte comme un type natif (`int`, `str`, `list`), mais possède deux super-pouvoirs :

1. **Casting Universel :** Elle peut s'instancier à partir de langage naturel.
2. **Comparaison Sémantique :** Elle peut être comparée à des concepts flous.

```python
from OpenHosta.semantics import SemanticType

# 1. Définition d'un type par l'intention
# On demande un entier qui représente un âge humain
Age = SemanticType(int, "Un âge humain valide en années")

# 2. Instanciation "Magique" (Casting Sémantique)
# Le système comprend, nettoie et valide la donnée brute
user_age = Age("Il a la trentaine environ") 

print(user_age)      # Output: 30
print(type(user_age)) # Output: <class 'SemanticInt'> (hérite de int)

# 3. Usage naturel
# L'objet se comporte comme un entier normal pour Python
if user_age > 18:
    print("Majeur")

```

---

## II. L'Architecture Hybride : Comment ça marche ?

OpenHosta ne se contente pas d'appeler un LLM. Il utilise une architecture en **entonnoir** pour garantir performance et précision.

### 2.1 Le Pipeline d'Instanciation (`GuardedPrimitive`)

Lorsque vous créez `Age("trente")`, le système suit 4 étapes rigoureuses pour économiser des ressources :

1. **Check Natif (Instant) :** Si la valeur est déjà `30` (int), on valide.
2. **Heuristique (Rapide) :** On tente des nettoyages classiques (Regex, `strip`, suppression de devises).
3. **Boucle LLM (Intelligent) :** Si l'échec persiste, le moteur génératif (Logprobs) prend le relais pour extraire l'information et la convertir au format cible (JSON/Python).
4. **Validation Finale :** La valeur extraite est réinjectée dans le validateur natif pour garantir l'intégrité du type.

### 2.2 Le Moteur de Comparaison (Vecteurs vs Logprobs)

Lorsque vous faites `if variable == concept`, OpenHosta choisit dynamiquement la meilleure stratégie :

* **Stratégie Vectorielle (Rapide) :** Pour les tolérances standards, il utilise la distance cosinus entre les embeddings.
* **Stratégie Générative (Précise) :** Pour les tolérances très strictes, il utilise le LLM pour vérifier les nuances (négation, antonymes proches).

---

## III. Le Contrôle de la Tolérance

La `semantic_tolerance` est le curseur qui définit le niveau de risque que vous acceptez.
Ne choisissez pas un chiffre au hasard. Utilisez les constantes fournies pour définir votre **intention**.

```python
from OpenHosta.semantics import Tolerance

# Définition avec une tolérance explicite
Animal = SemanticType(str, "Un animal domestique", tolerance=Tolerance.PRECISE)

```

### Le Guide des Tolérances

| Niveau | Constante | Valeur | Mécanique | Cas d'usage | Analogie Cible |
| --- | --- | --- | --- | --- | --- |
| **Strict** | `Tolerance.STRICT` | `0.00` | LLM (Logprobs) | IDs, Mots de passe, Codes | 🎯 La Mouche (Centre exact) |
| **Précis** | `Tolerance.PRECISE` | `0.05` | Hybride | Commandes CLI ("git push"), Formulaires | 🟡 Zone Jaune (Exactitude fonctionnelle) |
| **Flexible** | `Tolerance.FLEXIBLE` | `0.15` | Vecteurs (Embeddings) | **(Défaut)** Chatbots, Catégorisation | 🔵 La Cible (Même concept) |
| **Créatif** | `Tolerance.CREATIVE` | `0.30` | Vecteurs (Large) | Brainstorming, Idéation | 🧱 Le Mur (Thématique liée) |

> [!WARNING]
> **Attention au coût :** Une tolérance **STRICT** ou **PRECISE** (< 0.05) force souvent l'utilisation du LLM pour valider l'égalité, ce qui est plus lent et coûteux que la comparaison vectorielle utilisée par **FLEXIBLE**.

---

## IV. Le Système de Types Avancé (`TypeResolver`)

OpenHosta s'intègre parfaitement avec le module `typing` de Python. Vous n'avez pas besoin de réécrire vos modèles de données.

### 4.1 Résolution de Types Complexes

Utilisez `SemanticType.resolve()` pour transformer des annotations Python standards en validateurs sémantiques puissants.

```python
from typing import List
from OpenHosta.semantics import SemanticType

# "Je veux une liste d'entiers, débrouille-toi avec l'entrée."
# Le système génère une classe SemanticList[SemanticInt] à la volée.
IntList = SemanticType.resolve(List[int])

# L'entrée est sale, mélange texte et chiffres
data = IntList("[10, 'vingt', 30]")

print(data) # Output: [10, 20, 30]

```

### 4.2 Syntaxe Directe

Pour du scripting rapide, vous pouvez utiliser la syntaxe de tableau :

```python
from OpenHosta.semantics import SemanticList, SemanticInt

# Instanciation directe en une ligne
users = SemanticList[SemanticInt, str]("[1, 2, 'trois']")

```

---

## V. Les Collections Sémantiques

Les collections OpenHosta ne se contentent pas de stocker des données, elles les **organisent** spatialement.

### 5.1 `SemanticSet` (L'ensemble auto-synthétisé)

Un `SemanticSet` regroupe les éléments par "clusters" de sens. Il est idéal pour dédupliquer des listes d'idées ou de tâches.

* **Ajout intelligent :** Si vous ajoutez un synonyme, il rejoint le groupe existant sans créer de doublon.
* **Auto-Labelling :** Le nom du groupe est recalculé dynamiquement pour représenter le "centre de gravité" des éléments qu'il contient.

```python
from OpenHosta.semantics import SemanticSet

tasks = SemanticSet(type=SemanticType(str, "Tâche ménagère"))
tasks.add("Laver le sol")
tasks.add("Passer la serpillière") # Détecté comme doublon sémantique

print(tasks) 
# Output probable : {"Nettoyage des sols"} (Label synthétisé)

```

### 5.2 `SemanticDict` (Le dictionnaire à boussole)

Contrairement au `dict` Python qui utilise le hachage (égalité stricte), le `SemanticDict` utilise un **index spatial** (BallTree). Il permet de retrouver une valeur à partir d'une clé *approximative*.

```python
from OpenHosta.semantics import SemanticDict

# Clé : Concept d'animal
router = SemanticDict(key_type=SemanticType(str, "Animal"))
router["Chien"] = "Wouf"

# Recherche floue
print(router["Mon petit toutou"]) 
# Output: "Wouf" (Car "Toutou" est proche de "Chien")

```

Le routeur peut aussi être instancié en une ligne avec correction automatique de la syntaxe :

```python
router = SemanticDict[AnimalType, str]("{chien:'wouf', 'chat':miaou}")
```

---

## VI. Limitations et Bonnes Pratiques

### 6.1 Hachage et Dictionnaires Natifs

> [!CAUTION]
> **Ne jamais utiliser** un `SemanticType` comme clé dans un `dict` Python standard (`{}`).
> Pour garantir le "Flou Maîtrisé", `SemanticType` surcharge l'égalité (`__eq__`) mais rend l'objet **non-hachable**. Python lèvera une erreur `TypeError: unhashable type`. Utilisez toujours `SemanticDict`.

### 6.2 Performance des Embeddings

Les vecteurs sont calculés de manière "Lazy" (uniquement au besoin) et mis en cache. Cependant, le premier appel pour un nouveau texte déclenche une requête (locale ou API).

* Privilégiez l'instanciation unique de vos objets sémantiques.
* Utilisez `SemanticSet` pour traiter des lots de données textuelles massifs.

---

## VII. Créer vos propres Types Métier (`GuardedPrimitive`)

Jusqu'à présent, nous avons utilisé des types génériques (`SemanticInt`, `SemanticStr`). Mais la vraie puissance d'OpenHosta réside dans la création de types "Métier" qui encapsulent vos règles d'entreprise spécifiques.

Pour créer un type personnalisé, il suffit d'hériter de `GuardedPrimitive` et de votre type de base (ici `str`), puis d'implémenter les règles du jeu.

### 7.1 L'Étude de Cas : `CorporateEmail`

Imaginons que nous devions valider les emails d'une entreprise aux règles historiques complexes.

**Les Règles Métier :**

1. **Domaines autorisés (3) :** `mycorp.com` (actuel), `mycorp-group.net` (filiales), `legacy-subsidiary.fr` (historique).
2. **Formats locaux autorisés :**
* Standard : `prenom.nom` ou `prenom.nom-ext` (pour les prestataires).
* Legacy : `prenom_nom` ou `prenom_nom_externe`.



### 7.2 L'Implémentation

Voici comment traduire ces règles en un `SemanticType` robuste.

```python
import re
from OpenHosta.core.semantics import GuardedPrimitive

class CorporateEmail(str, GuardedPrimitive):
    """
    Type sémantique pour valider et normaliser les emails d'entreprise.
    Gère les formats 'dot' (nouveau) et 'underscore' (ancien).
    """

    # --- 1. CONFIGURATION LLM (L'Intention) ---
    # C'est ce que le moteur lira pour comprendre quoi faire si l'entrée est sale.
    
    _type_en = (
        "a professional corporate email address. "
        "Allowed domains: mycorp.com, mycorp-group.net, legacy-subsidiary.fr. "
        "Format: 'first.last' or 'first_last', optionally with '-ext' or '_externe' suffix."
    )
    
    _type_py = "str"
    
    # Le JSON Schema aide le LLM à pré-valider le format via une Regex générique
    _type_json = {
        "type": "string",
        "format": "email",
        "pattern": "^[a-z0-9._-]+@(mycorp\.com|mycorp-group\.net|legacy-subsidiary\.fr)$"
    }

    # --- 2. CONFIGURATION TECHNIQUE (La Loi) ---

    @classmethod
    def _parse_native(cls, value):
        """
        La validation stricte. Si cette méthode retourne False, 
        même une réponse du LLM sera rejetée.
        """
        if not isinstance(value, str):
            return False, None
            
        # Règle 0 : Minuscules uniquement pour la standardisation
        email = value.lower()
        
        # Validation de base : présence du @
        if "@" not in email:
            return False, None
            
        local_part, domain = email.split("@")

        # Règle 1 : Domaines Autorisés
        ALLOWED_DOMAINS = {"mycorp.com", "mycorp-group.net", "legacy-subsidiary.fr"}
        if domain not in ALLOWED_DOMAINS:
            return False, None

        # Règle 2 : Formats Locaux (Regex Python)
        # Format Standard : jean.dupont ou jean.dupont-ext
        is_standard = bool(re.match(r"^[a-z]+\.[a-z]+(-ext)?$", local_part))
        
        # Format Legacy : jean_dupont ou jean_dupont_externe
        is_legacy = bool(re.match(r"^[a-z]+_[a-z]+(_externe)?$", local_part))

        if is_standard or is_legacy:
            return True, email
            
        return False, None

    @classmethod
    def _parse_heuristic(cls, value):
        """
        Nettoyage rapide et gratuit avant d'appeler le LLM.
        """
        if isinstance(value, str):
            # On retire les espaces, les 'mailto:', les chevrons < >
            cleaned = value.strip().lower()
            cleaned = cleaned.replace("mailto:", "").replace("<", "").replace(">", "")
            
            # On tente la validation native immédiate
            is_valid, val = cls._parse_native(cleaned)
            if is_valid:
                return True, val
                
        return False, None

```

### 7.3 Comment OpenHosta utilise votre classe ?

Grâce au pipeline `GuardedPrimitive`, votre classe agit intelligemment selon la qualité de la donnée.

#### Scénario A : Donnée Parfaite (Coût Zéro)

```python
# _parse_native valide directement. Le LLM n'est pas appelé.
email = CorporateEmail("jean.dupont@mycorp.com")

```

#### Scénario B : Donnée "Sale" mais réparable (Coût Zéro)

```python
# _parse_heuristic retire le "mailto:" et les espaces. Validation native OK.
email = CorporateEmail("  mailto:jean.dupont@mycorp.com  ")

```

#### Scénario C : Donnée Incorrecte ou Incomplète (Réparation LLM)

C'est ici que la magie opère. L'utilisateur rentre une donnée humaine, le système utilise vos règles `_type_en` et `_type_json` pour la corriger.

```python
# L'utilisateur se trompe de format ("." au lieu de "_") et oublie l'extension exacte.
# Entrée : "jean.dupont_externe chez legacy subsidiary"
raw_input = "jean.dupont_externe chez legacy subsidiary"

# 1. Native & Heuristic échouent.
# 2. Le LLM reçoit le prompt : "Convert this to a professional corporate email..."
# 3. Le LLM comprend qu'il doit basculer en format 'underscore' pour le domaine legacy.
email = CorporateEmail(raw_input)

print(email) 
# Output: "jean_dupont_externe@legacy-subsidiary.fr"
# (Le type a forcé la cohérence entre le séparateur et le domaine)

```

### 7.4 Résumé des étapes de création

1. **Héritage :** `class MonType(BaseType, GuardedPrimitive)`.
2. **Intention (`_type_en`) :** Décrivez les règles en anglais pour guider le LLM en cas d'erreur.
3. **Validation (`_parse_native`) :** Codez vos règles métier strictes en Python (`regex`, `if`, listes). C'est le gardien final.
4. **Nettoyage (`_parse_heuristic`) :** (Optionnel) Implémentez des `replace` ou `strip` pour éviter d'appeler le LLM pour des broutilles.

> [!TIP]
> **Pourquoi le _type_json ?**
> Définir une regex dans le `_type_json` ("pattern": "...") est très efficace. Cela permet au LLM de "vérifier lui-même" sa réponse avant de vous l'envoyer, augmentant drastiquement le taux de succès du premier coup (One-shot success rate).

---

## VIII. Structures Complexes : `SemanticModel`

Maintenant que vous maîtrisez les atomes (`SemanticType`), passons aux molécules.
Un **`SemanticModel`** permet de définir des objets complexes composés de plusieurs champs, et de les instancier directement depuis du langage naturel non structuré.

### 8.1 Définition d'un Modèle

La syntaxe est volontairement identique aux `dataclasses` ou à `Pydantic`. Vous définissez une classe, vous annotez les types, et OpenHosta s'occupe du reste.

Reprenons notre type `CorporateEmail` créé au chapitre précédent pour l'intégrer dans une fiche client.

```python
from OpenHosta.semantics import SemanticModel, SemanticType
from typing import List

# On réutilise nos briques de base
class CorporateEmail(SemanticType): 
    ... # (Voir chapitre VII)

class ClientProfile(SemanticModel):
    """
    Profil structuré d'un client entreprise.
    """
    first_name: str
    last_name: str
    email: CorporateEmail  # Notre type personnalisé
    
    # On peut définir des types à la volée
    segment: SemanticType(str, "Marketing segment: VIP, Regular, or New Lead", tolerance=0.05)
    
    # Et utiliser des collections complexes
    tags: List[str] 

```

### 8.2 L'Extraction Sémantique (Le "Magic Constructor")

C'est ici que la différence avec une classe classique est frappante. Vous n'avez pas besoin de passer les arguments nommés (`first_name=...`). Vous pouvez passer une phrase brute.

```python
raw_text = """
J'ai eu Jean Dupont au téléphone, il fait partie du groupe mycorp-group.net. 
C'est un client VIP. Notez qu'il est intéressé par l'offre cloud.
"""

# Instanciation depuis le chaos
client = ClientProfile(raw_text)

print(client.first_name) # "Jean"
print(client.last_name)  # "Dupont"
print(client.email)      # "jean.dupont@mycorp-group.net" (Généré et validé par CorporateEmail)
print(client.segment)    # "VIP"
print(client.tags)       # ["cloud", "intéressé"] (Liste extraite du contexte)

```

**Que s'est-il passé ?**
Le `SemanticModel` a analysé la docstring de la classe et les types de chaque champ pour construire un "Extracteur sur mesure". Il a mappé le texte vers les champs, nettoyé les données via les `GuardedPrimitive`, et validé la cohérence globale.

---

### 8.3 Comparatif : Dataclasses vs Pydantic vs OpenHosta

C'est la question que tout développeur Python se pose. Lequel choisir ?

| Fonctionnalité | 🐍 Python `dataclasses` | 🚀 `Pydantic` | 🧠 `OpenHosta` |
| --- | --- | --- | --- |
| **Philosophie** | **Stockage** léger | **Validation** stricte | **Extraction** & Compréhension |
| **Entrée attendue** | Données propres | Données structurées (JSON/Dict) | **N'importe quoi** (Texte, JSON sale, Langage naturel) |
| **Tolérance** | Aucune (Crash si type incorrect) | Faible (Cast simple "1"->1) | **Maximale** (Réparation, Traduction, Déduction) |
| **Coût (Performance)** | ⚡️ Instantané | ⚡️ Très Rapide | 🐢 Plus lent (Appels LLM si nécessaire) |
| **Cas d'usage** | Stockage interne, Config | APIs REST, Sérialisation | **Agents IA**, Parsing d'emails, Scraping, Chatbots |

#### En résumé :

1. **Utilisez `dataclasses**` si vous manipulez des données internes à votre code dont vous maîtrisez la source à 100%.
2. **Utilisez `Pydantic**` si vous construisez une API technique qui reçoit du JSON et doit rejeter les erreurs de format (Fail Fast).
3. **Utilisez `SemanticModel**` si vous êtes en "bout de chaîne" face à un utilisateur humain ou un LLM. Là où Pydantic lèverait une `ValidationError` parce que l'utilisateur a écrit "vingt" au lieu de `20`, OpenHosta comprend et convertit.

### 8.4 La Validation Croisée (Coherence Check)

Une fonctionnalité unique aux `SemanticModel` est la capacité de valider la logique *entre* les champs.

Imaginez un modèle `OffreEmploi`. Pydantic peut vérifier que le salaire est un nombre. Mais seul OpenHosta peut vérifier si le salaire est cohérent avec le titre du poste.

```python
class JobOffer(SemanticModel):
    title: str
    salary: int

    def validate_coherence(self):
        """
        Méthode spéciale appelée après l'instanciation.
        """
        # Si le salaire est < 20k et le titre est "Senior Engineer", 
        # c'est sémantiquement louche (même si c'est techniquement un int valide).
        pass 

```

OpenHosta peut effectuer cette vérification de cohérence (via LLM) et lever une alerte ou marquer l'objet comme incertain si les champs se contredisent sémantiquement.

---

### 8.5 Intégration Native avec Pydantic (Si installé)

OpenHosta a été conçu pour s'effacer devant les standards de l'industrie. Si la librairie **Pydantic (V2)** est détectée dans votre environnement, `SemanticModel` hérite automatiquement de `pydantic.BaseModel`.

Cela transforme OpenHosta en un **Middleware de Validation** invisible.

**Comment ça marche sous le capot ?**
Normalement, Pydantic rejette immédiatement une donnée du mauvais type (Ex: "trente" pour un `int`).
Avec OpenHosta, le `SemanticType` agit comme un **Intercepteur (BeforeValidator)** :

1. **Interception :** Pydantic reçoit la donnée brute.
2. **Délégation :** Avant de lever une erreur, il passe la main au pipeline `GuardedPrimitive` d'OpenHosta.
3. **Réparation :** OpenHosta nettoie (Regex) ou traduit (LLM) la donnée.
4. **Validation :** La donnée propre (ex: `30`) est rendue à Pydantic pour la validation finale.

> [!TIP]
> **Zéro Config :** Vous n'avez rien à activer. Si `pip install pydantic` a été lancé, vos modèles sémantiques sont automatiquement compatibles avec FastAPI, Typer, et SQLModel.

---

### 8.6 Cas d'Usage : Une API FastAPI "Auto-Healing"

C'est l'application la plus spectaculaire. En utilisant un `SemanticModel` dans une API FastAPI, vos endpoints deviennent capables de "s'auto-réparer" face à des requêtes mal formées, sans écrire une seule ligne de gestion d'erreur.

#### Le Code de l'API

```python
from fastapi import FastAPI
from OpenHosta.semantics import SemanticModel, SemanticType, SemanticList

app = FastAPI()

# 1. Définition du Modèle (Compatible Pydantic & Swagger)
class UserOnboarding(SemanticModel):
    first_name: str
    
    # On définit des types tolérants pour les champs "à risque"
    age: SemanticType(int, "Age de l'utilisateur")
    email: SemanticType(str, "Email professionnel")
    
    # Une liste capable de parser une string CSV ou JSON mal formée
    skills: SemanticList[str]

# 2. Endpoint standard
@app.post("/users/")
def create_user(user: UserOnboarding):
    # Ici, 'user' est déjà propre et typé.
    return {
        "status": "success",
        "message": f"Utilisateur {user.first_name} créé.",
        "cleaned_data": user.model_dump() # Méthode Pydantic standard
    }

```

#### Le Test : Requête "Sale" vs Réponse "Propre"

Imaginons qu'un script client buggé ou un utilisateur fatigué envoie cette requête JSON **techniquement invalide** (types incorrects, formats douteux) :

**Requête reçue (`POST /users/`) :**

```json
{
    "first_name": "Alice",
    "age": "vingt-cinq ans",          <-- Erreur: String au lieu de Int
    "email": "alice at google.com",   <-- Erreur: Format email invalide
    "skills": "python, java et docker" <-- Erreur: String au lieu de List
}

```

**Comportement Standard (FastAPI classique) :**
❌ **422 Unprocessable Entity**. L'API rejette tout en bloc.

**Comportement OpenHosta :**
✅ **200 OK**. Le système intercepte les erreurs et reconstruit l'objet.

**Réponse renvoyée :**

```json
{
    "status": "success",
    "message": "Utilisateur Alice créé.",
    "cleaned_data": {
        "first_name": "Alice",
        "age": 25,                    // Converti en int
        "email": "alice@google.com",  // Reformatté
        "skills": ["python", "java", "docker"] // Parsé en liste
    }
}

```

### Conclusion

Avec `SemanticModel`, vous ne validez plus seulement la **structure** des données (rôle de Pydantic), vous garantissez leur **compréhension** (rôle d'OpenHosta). Vos APIs deviennent résilientes par design.