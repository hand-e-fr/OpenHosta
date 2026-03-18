# 📖 Documentation OpenHosta.guarded

**OpenHosta.guarded** est le module de validation et de conversion de types avec tolérance configurable. Il transforme des entrées arbitraires en types Python natifs avec métadonnées de confiance et de traçabilité.

---

## I. Introduction : Types Gardés (Guarded Types)

Les types Guarded sont des types Python enrichis qui :
1. **Acceptent des entrées imparfaites** et les nettoient automatiquement
2. **Conservent des métadonnées** sur la qualité de la conversion
3. **Se comportent comme des types natifs** pour une intégration transparente

```python
from OpenHosta.guarded import GuardedInt

# Accepte plusieurs formats
age = GuardedInt("42")        # String numérique
price = GuardedInt("1,000")   # Avec séparateur de milliers
count = GuardedInt(42.0)      # Float rond

# Se comporte comme un int
total = age + 10  # 52

# Mais garde des métadonnées
print(age.uncertainty)        # 0.0 (parfaitement certain)
print(age.abstraction_level)  # 'native'
print(price.uncertainty)      # 0.15 (parsing heuristique)
```

---

## II. Architecture : Le Pipeline de Validation

Chaque type Guarded utilise un pipeline en cascade pour convertir les entrées :

### 2.1 Les 4 Niveaux de Parsing

```
Entrée → Native → Heuristic → Semantic → Knowledge → Sortie
         ↓        ↓           ↓          ↓
         0.00     0.0-0.15    0.0-0.30   0.0+
         (STRICT) (PRECISE)   (FLEXIBLE) (CREATIVE)
```

1. **Native** (Coût: O(1), Uncertainty: 0.0)
   - Vérification de type direct (`isinstance`)
   - Si la valeur est déjà du bon type, validation immédiate

2. **Heuristic** (Coût: O(n), Uncertainty: 0.05-0.15)
   - Nettoyage déterministe (regex, strip, cast)
   - Suppression d'espaces, séparateurs, devises
   - Conversion de formats standards

3. **Semantic** (Coût: ~1s, Uncertainty: 0.15-0.30)
   - Conversion via LLM (non implémenté actuellement)
   - Compréhension du contexte et de l'intention

4. **Knowledge** (Coût: Variable, Uncertainty: 0.30+)
   - Consultation de base de connaissances
   - Mapping de synonymes et variantes

### 2.2 Tolérance et Contrôle

La tolérance définit jusqu'où le pipeline peut aller.

Le constructeur utilise toujours la tolérance par défaut de la classe (`_tolerance`).

Pour forcer une tolérance, utilisez `attempt()` :

```python
from OpenHosta.guarded import GuardedInt, Tolerance

# Tolérance stricte : seul le niveau Native est accepté
strict_result = GuardedInt.attempt("42", tolerance=Tolerance.STRICT)

# Tolérance flexible : Native + Heuristic acceptés
flexible_result = GuardedInt.attempt("1,000", tolerance=Tolerance.FLEXIBLE)

# Tolérance par défaut : _tolerance de la classe
value = GuardedInt("1,000")
```

Pour changer durablement la tolérance, créez une sous-classe :

```python
from OpenHosta.guarded import GuardedInt, Tolerance

class StrictGuardedInt(GuardedInt):
    _tolerance = Tolerance.STRICT

value = StrictGuardedInt(42)
```

| Niveau | Constante | Valeur | Niveaux Acceptés |
|--------|-----------|--------|------------------|
| **Strict** | `Tolerance.STRICT` | 0.00 | Native uniquement |
| **Précis** | `Tolerance.PRECISE` | 0.05 | Native |
| **Flexible** | `Tolerance.FLEXIBLE` | 0.15 | Native + Heuristic |
| **Type Compliant** | `Tolerance.TYPE_COMPLIANT` | 0.999 | Tous (défaut) |

### 2.3 Constructeurs multi-paramètres

Les classes enfants de `GuardedPrimitive` peuvent maintenant accepter plusieurs
arguments positionnels et nommés.

- Si le constructeur reçoit **un seul argument positionnel** et **aucun kwarg**,
  le pipeline reçoit directement cette valeur.
- Sinon, les entrées sont encapsulées dans un objet `GuardedCallInput(args, kwargs)`
  puis transmises comme **valeur unique** au pipeline.

Cela permet à une sous-classe d'implémenter sa propre logique dans `_parse_native()`,
`_parse_heuristic()`, etc., tout en conservant l'architecture actuelle centrée sur
une seule entrée `value`.

```python
from OpenHosta.guarded.primitives import GuardedPrimitive, GuardedCallInput
from OpenHosta.guarded import Tolerance

class FullName(GuardedPrimitive, str):
    _type_en = "a full name"
    _type_py = str
    _tolerance = Tolerance.TYPE_COMPLIANT

    @classmethod
    def _parse_heuristic(cls, value):
        if isinstance(value, GuardedCallInput):
            first = value.kwargs.get("first") or value.args[0]
            last = value.kwargs.get("last") or value.args[1]
            return Tolerance.PRECISE, f"{first.strip()} {last.strip()}", None
        return super()._parse_heuristic(value)

name = FullName("Ada", "Lovelace")
name2 = FullName(first="Ada", last="Lovelace")
```


---

## III. Types Scalaires


### 3.1 GuardedInt

Entier avec parsing intelligent.

```python
from OpenHosta.guarded import GuardedInt

# Formats acceptés
GuardedInt(42)           # Native int
GuardedInt("42")         # String numérique
GuardedInt("1,000")      # Séparateur de milliers
GuardedInt("1 000")      # Espaces
GuardedInt("-42")        # Négatifs
GuardedInt(42.0)         # Float rond
```

**Parsing Heuristic** :
- Suppression des espaces
- Suppression des virgules (si pas de point décimal)
- Validation regex : `-?\d+`

### 3.2 GuardedFloat

Nombre flottant avec parsing flexible.

```python
from OpenHosta.guarded import GuardedFloat

# Formats acceptés
GuardedFloat(3.14)       # Native float
GuardedFloat("3.14")     # String
GuardedFloat("3,14")     # Format européen
GuardedFloat("1.000,5")  # Milliers + décimales
GuardedFloat(42)         # Int vers float
```

**Parsing Heuristic** :
- Remplacement `,` → `.` pour format européen
- Gestion des séparateurs de milliers multiples
- Conversion automatique int → float

### 3.3 GuardedUtf8

String avec gestion d'encodage.

```python
from OpenHosta.guarded import GuardedUtf8

# Formats acceptés
GuardedUtf8("hello")     # Native string
GuardedUtf8(b"hello")    # Bytes UTF-8
```

**Parsing Heuristic** :
- Décodage automatique bytes → string
- Gestion des erreurs d'encodage

---

## III.b Types Scalaires Avancés

### 3.4 GuardedComplex

Nombre complexe avec parsing intelligent.

```python
from OpenHosta.guarded import GuardedComplex

# Formats acceptés
GuardedComplex(1+2j)         # Native complex
GuardedComplex("1+2j")       # String standard
GuardedComplex("1 + 2j")     # Avec espaces
```

### 3.5 GuardedBytes et GuardedByteArray

Types binaires avec parsing flexible depuis strings.

```python
from OpenHosta.guarded import GuardedBytes

# Formats acceptés
GuardedBytes(b"hello")       # Native bytes
GuardedBytes("hello")        # String (encodé en UTF-8)
GuardedBytes([104, 101])     # Liste d'entiers
```

---

## IV. Types Proxy (Non-Subclassables)

Certains types Python ne peuvent pas être subclassés (`bool`, `NoneType`, etc.). Pour ceux-ci, nous utilisons un **ProxyWrapper**.

### 4.1 GuardedBool

Boolean avec parsing de langage naturel.

```python
from OpenHosta.guarded import GuardedBool

# Formats acceptés
b = GuardedBool(True)    # Native bool
b = GuardedBool("yes")   # Anglais
b = GuardedBool("oui")   # Français
b = GuardedBool("1")     # Numérique

# Récupération de la valeur native
b.unwrap()  # → True (vrai bool Python)

# Comparaison
if b:  # Fonctionne grâce à __bool__
    print("Vrai")
```

**Base de connaissances** :
- True: `["yes", "y", "true", "1", "oui", "vrai", "ok"]`
- False: `["no", "n", "false", "0", "non", "faux"]`

### 4.2 GuardedNone

Type None avec parsing flexible.

```python
from OpenHosta.guarded import GuardedNone

# Formats acceptés
n = GuardedNone(None)      # Native None
n = GuardedNone("None")    # String "None"
n = GuardedNone("null")    # JSON null
n = GuardedNone("nothing") # Langage naturel

n.unwrap()  # → None
```


### 4.3 Autres Proxy (Any, Range, MemoryView)

* **GuardedAny**: Accepte tout type, utile comme "pass-through" avec métadonnées.
* **GuardedRange**: Proxy pour `range()`. Accepte `range(10)` ou string `"0:10"`.
* **GuardedMemoryView**: Proxy pour `memoryview`.

### 4.4 Comportement ProxyWrapper

⚠️ **Important** : Les types proxy ne sont PAS des instances du type natif.

```python
from OpenHosta.guarded import GuardedBool

b = GuardedBool("yes")

isinstance(b, bool)        # ❌ False (c'est un proxy)
isinstance(b.unwrap(), bool)  # ✅ True

# Mais ils se comportent comme le type natif
if b:  # ✅ Fonctionne
    pass

b == True  # ✅ True (grâce à __eq__)
```

---

## V. Collections

### 5.1 GuardedList

Liste avec parsing de strings.

```python
from OpenHosta.guarded import GuardedList

# Formats acceptés
lst = GuardedList([1, 2, 3])      # Native list
lst = GuardedList((1, 2, 3))      # Tuple → list
lst = GuardedList({1, 2, 3})      # Set → list
lst = GuardedList("[1, 2, 3]")    # JSON string

# Opérations normales
lst.append(4)
lst[0]  # 1
len(lst)  # 4
```

### 5.2 GuardedDict

Dictionnaire avec parsing JSON.

```python
from OpenHosta.guarded import GuardedDict

# Formats acceptés
d = GuardedDict({"a": 1})         # Native dict
d = GuardedDict('{"a": 1}')       # JSON string
d = GuardedDict("{'a': 1}")       # Python repr

# Opérations normales
d["b"] = 2
d.get("c")  # None
```

### 5.3 GuardedSet et GuardedTuple

Même logique que GuardedList avec leurs spécificités respectives.


### 5.4 Types Composites Avancés

#### GuardedLiteral

Crée un type restreint à un ensemble de valeurs, similaire à `typing.Literal`.

```python
from OpenHosta.guarded import guarded_literal

Color = guarded_literal("red", "green", "blue")

c = Color("red")      # OK
c = Color("RED")      # OK (heuristic: case-insensitive)

# doc-test: raises ValueError
c = Color("yellow")   # Erreur (hors des valeurs permises)
```

#### GuardedUnion

Crée un type qui tente plusieurs conversions successives, similaire à `typing.Union`.

```python
from OpenHosta.guarded.sublassableunions import GuardedUnion, guarded_union
from OpenHosta.guarded import GuardedInt, GuardedUtf8

# Tente d'abord Int, sinon String
IntOrStr = guarded_union(GuardedInt, GuardedUtf8)

v1 = IntOrStr("42")      # → 42 (int)
v2 = IntOrStr("hello")   # → "hello" (str)
```

---

## VI. GuardedEnum : Enums Validées

Créez des enums avec parsing case-insensitive et par valeur.

```python
from OpenHosta.guarded import GuardedEnum

class Status(GuardedEnum):
    PENDING = "pending"
    ACTIVE = "active"
    DONE = "done"

# Parsing flexible
s1 = Status("active")    # Par nom (minuscule)
s2 = Status("ACTIVE")    # Par nom (majuscule)
s3 = Status("pending")   # Par valeur
s4 = Status("Status.ACTIVE")  # Format repr() (EnumName.MEMBER)
s5 = Status(".ACTIVE")        # Format court (.MEMBER)

# API compatible enum.Enum
s1.name   # "ACTIVE"
s1.value  # "active"
repr(s1)  # "Status.ACTIVE"

# Comparaison
s1 == s2  # True
s1 == "ACTIVE"  # True

# Round-trip avec repr()
s = Status("ACTIVE")
s_copy = Status(repr(s))  # ✅ Fonctionne !
```

**Formats acceptés** :
- ✅ Par nom : `Status("ACTIVE")`, `Status("active")`
- ✅ Par valeur : `Status("pending")`
- ✅ Format repr() : `Status("Status.ACTIVE")`
- ✅ Format court : `Status(".ACTIVE")`

**Avantages** :
- ✅ Parsing case-insensitive
- ✅ Recherche par nom ou valeur
- ✅ Compatible avec `repr()` pour sérialisation/désérialisation
- ✅ API compatible avec `enum.Enum`
- ✅ Métadonnées de confiance

---

## VII. Dataclasses Gardées

Transformez vos classes en dataclasses validées avec un seul décorateur.

> **Note** : `@guarded_dataclass` applique automatiquement `@dataclass`, vous n'avez pas besoin des deux !

### 7.1 Usage Simple (Recommandé)

```python
from OpenHosta.guarded import guarded_dataclass

@guarded_dataclass
class Person:
    name: str
    age: int

# Création standard avec kwargs
p1 = Person(name="Alice", age=30)

# Création standard avec args positionnels
p1b = Person("Alice", 30)

# Création depuis dict avec conversion automatique
p2 = Person({"name": "Bob", "age": "25"})  # age converti de str → int


# Les champs sont validés et convertis
assert p2.age == 25
assert isinstance(p2.age, int)  # Converti automatiquement
```

### 7.2 Args et kwargs dans les dataclasses guardées

Les classes décorées avec `@guarded_dataclass` supportent maintenant :

- les **kwargs** classiques
- les **args positionnels**
- les entrées sous forme de **dict**
- les représentations texte de type constructeur ou dictionnaire

```python
from OpenHosta.guarded import guarded_dataclass

@guarded_dataclass
class Point:
    x: int
    y: int

p1 = Point(10, 20)
p2 = Point(x=10, y=20)
p3 = Point({"x": "10", "y": "20"})
p4 = Point("Point(x=10, y=20)")
```

En interne, si plusieurs arguments sont fournis au constructeur, ils sont encapsulés
sous forme de `GuardedCallInput(args, kwargs)` puis parsés par le pipeline.

### 7.3 Avec Options Dataclass


Vous pouvez passer des options directement à `@guarded_dataclass` :

```python
from OpenHosta.guarded import guarded_dataclass

@guarded_dataclass(frozen=True, order=True)
class Point:
    x: int
    y: int

pt = Point(x=10, y=20)
# pt.x = 100  # ❌ Erreur : frozen=True
```

### 7.4 Avec Valeurs Par Défaut


```python
from OpenHosta.guarded import guarded_dataclass

@guarded_dataclass
class Config:
    host: str = "localhost"
    port: int = 8080
    debug: bool = False

# Utiliser les défauts
c1 = Config()
assert c1.host == "localhost"

# Override partiel
c2 = Config(host="example.com")
assert c2.port == 8080  # Garde la valeur par défaut

# Depuis dict
c3 = Config({"host": "api.example.com", "port": "3000"})
assert c3.port == 3000  # Converti de "3000" (str) → 3000 (int)
```

### 7.5 Conversion Automatique des Types


Le décorateur utilise `TypeResolver` pour convertir automatiquement les valeurs :

```python
from OpenHosta.guarded import guarded_dataclass

@guarded_dataclass
class User:
    username: str
    age: int
    active: bool
    tags: list

# Toutes les conversions sont automatiques
user = User({
    "username": "alice",
    "age": "25",        # str → int
    "active": "yes",    # str → bool
    "tags": "python,ai" # str → list (parsing CSV)
})

assert user.age == 25
assert user.active == True
assert isinstance(user.tags, list)
```

### 7.6 Métadonnées Guarded


Comme tous les types Guarded, les dataclasses conservent des métadonnées :

```python
from OpenHosta.guarded import guarded_dataclass

@guarded_dataclass
class Product:
    name: str
    price: float

# Création depuis dict
p = Product({"name": "Widget", "price": "9.99"})

# Métadonnées disponibles
print(p.uncertainty)        # 0.15 (FLEXIBLE - parsing heuristic)
print(p.abstraction_level)  # 'heuristic'

# Création normale
p2 = Product(name="Gadget", price=19.99)
print(p2.uncertainty)       # 0.0 (STRICT - valeurs natives)
print(p2.abstraction_level) # 'native'
```

### 7.7 Usage Legacy (Avec @dataclass Explicite)


Si vous avez déjà `@dataclass`, `@guarded_dataclass` le détecte et ne le réapplique pas :

```python
from dataclasses import dataclass
from OpenHosta.guarded import guarded_dataclass

@guarded_dataclass
@dataclass
class Person:
    name: str
    age: int

# Fonctionne exactement pareil
```

> **Recommandation** : Utilisez uniquement `@guarded_dataclass` pour un code plus propre.

---

## VIII. TypeResolver : Résolution Automatique

Le `TypeResolver` convertit les annotations Python en types Guarded.

```python
from typing import List, Dict, Optional
from OpenHosta.guarded.resolver import TypeResolver, type_returned_data

# Résolution de types simples
TypeResolver.resolve(int)    # → GuardedInt
TypeResolver.resolve(str)    # → GuardedUtf8
TypeResolver.resolve(bool)   # → GuardedBool

# Résolution de types complexes
TypeResolver.resolve(List[int])        # → GuardedList
TypeResolver.resolve(Dict[str, int])   # → GuardedDict
TypeResolver.resolve(Optional[int])    # → GuardedInt

# Utilisation dans le pipeline
result = type_returned_data("42", int)  # Convertit "42" → 42
```

**Utilisé par** : Le pipeline OpenHosta pour typer automatiquement les réponses LLM.

---

## IX. Créer Vos Propres Types

Héritez de `GuardedPrimitive` pour créer des types métier personnalisés.

### 9.1 Exemple Complet : CorporateEmail avec Pipeline 4 Niveaux

Cet exemple montre **tous les niveaux du pipeline** avec validation LLM et annuaire d'entreprise.

```python
import re
from typing import Tuple, Optional, Any
from OpenHosta.guarded import GuardedUtf8, Tolerance
from OpenHosta.guarded.primitives import UncertaintyLevel
from OpenHosta import emulate

# Annuaire d'entreprise (simulé)
CORPORATE_DIRECTORY = {
    "marie.dupont@mycorp.com",
    "jean.martin@mycorp.com",
    "sophie.bernard@mycorp.com",
    "pierre.dubois@mycorp.com",
}

class CorporateEmail(GuardedUtf8):
    """Email d'entreprise validé contre l'annuaire mycorp.com"""
    
    _type_en = (
        "a corporate email address in the format firstname.lastname@mycorp.com "
        "where firstname and lastname are lowercase letters only"
    )
    _type_py = str
    _type_json = {
        "type": "string",
        "format": "email",
        "pattern": r"^[a-z]+\.[a-z]+@mycorp\.com$"
    }
    _type_knowledge = {
        "directory": CORPORATE_DIRECTORY,
        "domain": "mycorp.com"
    }
    
    @classmethod
    def _parse_native(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        """Niveau 1 : Email parfait dans l'annuaire (0.00 - STRICT)."""
        if not isinstance(value, str):
            return UncertaintyLevel(Tolerance.ANYTHING), value, "Not a string"
        
        # PAS de nettoyage - on accepte uniquement les emails parfaits
        if not re.match(r"^[a-z]+\.[a-z]+@mycorp\.com$", value):
            return UncertaintyLevel(Tolerance.ANYTHING), value, "Invalid format"
        
        if value in cls._type_knowledge["directory"]:
            return UncertaintyLevel(Tolerance.STRICT), value, None
        
        return UncertaintyLevel(Tolerance.ANYTHING), value, "Not in directory"
    
    @classmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        """Niveau 2 : Nettoyage déterministe (0.05 - PRECISE)."""
        if not isinstance(value, str):
            return UncertaintyLevel(Tolerance.ANYTHING), value, "Not a string"
        
        original = value
        cleaned = value.strip().lower()
        cleaned = cleaned.replace("mailto:", "").replace("<", "").replace(">", "")
        cleaned = cleaned.replace(" ", "").replace("\t", "") # Supprime les espaces et tabulations
        
        # Vérifier le format après nettoyage
        if re.match(r"^[a-z]+\.[a-z]+@mycorp\.com$", cleaned):
            if cleaned in cls._type_knowledge["directory"]:
                # Nettoyage effectué et dans l'annuaire → PRECISE
                if cleaned != original:
                    return UncertaintyLevel(Tolerance.PRECISE), cleaned, None
                # Pas de nettoyage mais dans l'annuaire (déjà géré par native, mais pour robustesse)
                return UncertaintyLevel(Tolerance.STRICT), cleaned, None
            else:
                # Format valide mais pas dans annuaire → FLEXIBLE (car pas STRICT)
                return UncertaintyLevel(Tolerance.FLEXIBLE), cleaned, "Valid format, not in directory"
        
        return UncertaintyLevel(Tolerance.ANYTHING), value, "Invalid format after heuristic cleaning"
    
    @classmethod
    def _llm_cast_email(cls, text: str) -> str | None:
        """
        Convert the input text to a valid corporate email: firstname.lastname@mycorp.com
        
        Rules:
        - Only lowercase letters for firstname and lastname
        - Examples:
            * "marie dot dupont at mycorp dor com" → "marie.dupont@mycorp.com"
            * "jean martin mycorp" → "jean.martin@mycorp.com"
        
        If the input cannot be converted, return None.
        """
        return emulate()

    @classmethod
    def _parse_semantic(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        """Niveau 3 : Correction LLM (0.15 - FLEXIBLE)."""
        if not isinstance(value, str):
            return UncertaintyLevel(Tolerance.ANYTHING), value, "Not a string"
        
        corrected = cls._llm_cast_email(value)
        
        if corrected and re.match(r"^[a-z]+\.[a-z]+@mycorp\.com$", corrected):
            # Email corrigé existe dans annuaire → FLEXIBLE
            if corrected in cls._type_knowledge["directory"]:
                return UncertaintyLevel(Tolerance.FLEXIBLE), corrected, None
            
            # Sinon, passe au niveau knowledge
            return UncertaintyLevel(Tolerance.ANYTHING), corrected, "LLM corrected but not in directory"
        
        return UncertaintyLevel(Tolerance.ANYTHING), value, "Cannot parse semantically"
    
    @classmethod
    def _parse_knowledge(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        """Niveau 4 : Fuzzy matching (0.30 - CREATIVE)."""
        if not isinstance(value, str):
            return UncertaintyLevel(Tolerance.ANYTHING), value, "Not a string"
        
        # Tente de normaliser l'entrée pour le fuzzy matching
        cleaned = value.strip().lower()
        cleaned = cleaned.replace("mailto:", "").replace("<", "").replace(">", "")
        cleaned = cleaned.replace(" ", "").replace("\t", "")
        
        # Extraire prénom et nom si le format est proche
        match = re.match(r"^([a-z]+)\.?([a-z]+)?@?([a-z\.]*)?$", cleaned)
        if not match:
            return UncertaintyLevel(Tolerance.ANYTHING), value, "Cannot extract name parts for fuzzy matching"
        
        firstname_raw, lastname_raw, domain_raw = match.groups()
        
        # Si le domaine est présent et incorrect, on ne peut pas fuzzy matcher
        if domain_raw and not domain_raw.startswith(cls._type_knowledge["domain"].split('.')[0]):
             return UncertaintyLevel(Tolerance.ANYTHING), value, "Incorrect domain for fuzzy matching"

        # Tente de trouver le meilleur match dans l'annuaire
        best_match = cls._find_closest_email(firstname_raw, lastname_raw)
        
        if best_match:
            return UncertaintyLevel(Tolerance.CREATIVE), best_match, "Fuzzy matched to directory"
        
        return UncertaintyLevel(Tolerance.ANYTHING), value, "No fuzzy match found in directory"
    
    @classmethod
    def _find_closest_email(cls, firstname: str, lastname: str) -> Optional[str]:
        """Trouve l'email le plus proche par distance de Levenshtein."""
        from difflib import get_close_matches
        
        directory_names = []
        for email in cls._type_knowledge["directory"]:
            m = re.match(r"^([a-z]+)\.([a-z]+)@", email)
            if m:
                directory_names.append((m.group(1), m.group(2), email))
        
        # Chercher prénom proche
        firstnames_in_dir = [n[0] for n in directory_names]
        close_first = get_close_matches(firstname, firstnames_in_dir, n=1, cutoff=0.7)
        if not close_first:
            return None
        
        # Filtrer les candidats par prénom proche
        candidates_for_lastname = [(n[1], n[2]) for n in directory_names if n[0] == close_first[0]]
        if not candidates_for_lastname:
            return None
            
        lastnames_in_candidates = [c[0] for c in candidates_for_lastname]
        close_last = get_close_matches(lastname, lastnames_in_candidates, n=1, cutoff=0.7)
        
        if close_last:
            for cand_last, email in candidates_for_lastname:
                if cand_last == close_last[0]:
                    return email
        return None


# ============================================================================
# DÉMONSTRATION
# ============================================================================

# Niveau NATIVE (0.00)
email1 = CorporateEmail("marie.dupont@mycorp.com")
print(f"{email1} - {email1.abstraction_level} - {email1.uncertainty}")
# → marie.dupont@mycorp.com - native - 0.0

# Niveau HEURISTIC (0.05)
email2 = CorporateEmail("  MARIE.DUPONT@MYCORP.COM  ")
print(f"{email2} - {email2.abstraction_level} - {email2.uncertainty}")
# → marie.dupont@mycorp.com - heuristic - 0.05

# Niveau SEMANTIC (0.15) - Correction LLM
email3 = CorporateEmail("marie dot dupont at mycorp dor com")
print(f"{email3} - {email3.abstraction_level} - {email3.uncertainty}")
# → marie.dupont@mycorp.com - semantic - 0.15

# Niveau KNOWLEDGE (0.30) - Fuzzy matching
email4 = CorporateEmail("m.dupond@mycorp.com")  # dupond -> dupont
print(f"{email4} - {email4.abstraction_level} - {email4.uncertainty}")
# → marie.dupont@mycorp.com - knowledge - 0.30

# Niveau HEURISTIC avec format valide mais pas dans annuaire (0.10)
email5 = CorporateEmail("john.doe@mycorp.com") # Format valide, mais pas dans CORPORATE_DIRECTORY
print(f"{email5} - {email5.abstraction_level} - {email5.uncertainty}")
# → john.doe@mycorp.com - heuristic - 0.10 (ou 0.05 si on considère que c'est juste un nettoyage)

# Décision basée sur la confiance
if email3.uncertainty <= Tolerance.PRECISE:
    print("✅ Validation automatique")
elif email3.uncertainty <= Tolerance.FLEXIBLE:
    print("⚠️  Demander confirmation")  # ← Ce cas
else:
    print("❌ Rejeter")
```

**Points clés** :

1. **`_parse_native`** : Aucun nettoyage, validation stricte uniquement
2. **`_parse_heuristic`** : Détecte si nettoyage effectué (`cleaned != original`)
3. **`_parse_semantic`** : Utilise `closure()` pour appel LLM réel
4. **`_parse_knowledge`** : Fuzzy matching avec `difflib.get_close_matches()`
5. **Validation annuaire** : Si email corrigé existe → confiance FLEXIBLE, sinon passe au niveau suivant

**Tests complets** : Voir [`tests/guarded/test_corporate_email.py`](../tests/guarded/test_corporate_email.py) (13/13 tests passent ✅)

### 9.2 Méthodes à Implémenter

| Méthode | Obligatoire | Description |
|---------|-------------|-------------|
| `_parse_native` | ✅ Oui | Validation stricte du type |
| `_parse_heuristic` | ⚠️ Recommandé | Nettoyage déterministe |
| `_parse_semantic` | ❌ Non | Conversion via LLM |
| `_parse_knowledge` | ❌ Non | Base de connaissances |

### 9.3 Attributs de Configuration

| Attribut | Type | Description |
|----------|------|-------------|
| `_type_en` | `str` | Description en anglais pour le LLM |
| `_type_py` | `type` | Type Python cible |
| `_type_json` | `dict` | JSON Schema pour validation |
| `_type_knowledge` | `dict\|Any` | Base de connaissances (optionnel) |
| `_tolerance` | `Tolerance` | Tolérance par défaut |

---

## X. Métadonnées et Traçabilité

Chaque instance Guarded conserve des métadonnées sur sa création.

### 10.1 Attributs Disponibles

```python
from OpenHosta.guarded import GuardedInt

age = GuardedInt("1,000")

# Métadonnées
age.uncertainty         # 0.15 (niveau de confiance)
age.abstraction_level   # 'heuristic' (méthode utilisée)
age.unwrap()           # Valeur native (pour ProxyWrapper)

# Opérations normales
age + 10   # 1010
age > 500  # True
```

### 10.2 Niveaux d'Abstraction

| Niveau | Description | Uncertainty Typique |
|--------|-------------|---------------------|
| `native` | Valeur déjà du bon type | 0.0 |
| `heuristic` | Nettoyage déterministe | 0.05-0.15 |
| `semantic` | Conversion LLM | 0.15-0.30 |
| `knowledge` | Base de connaissances | 0.30+ |

---

## XI. Intégration Pydantic

Les types Guarded s'intègrent avec Pydantic V2.

```python
from pydantic import BaseModel
from OpenHosta.guarded import GuardedInt, GuardedUtf8

class User(BaseModel):
    name: GuardedUtf8
    age: GuardedInt

# Pydantic + Guarded = Validation tolérante
user = User(name="Alice", age="25")  # age converti automatiquement
```

---

## XII. Bonnes Pratiques

### ✅ À Faire

1. **Utiliser les types Guarded pour les entrées utilisateur**
   ```python
   age = GuardedInt(user_input)  # Tolérant
   ```

2. **Forcer la tolérance via `attempt()` pour les cas critiques**
   ```python
   result = GuardedUtf8.attempt(input, tolerance=Tolerance.STRICT)
   if not result.is_success:
       raise ValueError(result.error_message)
   password = result.python_value
   ```

3. **Vérifier l'uncertainty pour les décisions importantes**
   ```python
   amount = GuardedFloat(input)
   if amount.uncertainty > Tolerance.PRECISE:
       logger.warning(f"Uncertain amount: {amount}")
   ```

### ❌ À Éviter

1. **Ne pas utiliser comme clés de dict natif**
   ```python
   # ❌ Erreur : ProxyWrapper types ne sont pas hashables
   d = {GuardedBool("yes"): "value"}
   
   # ✅ Utiliser GuardedDict ou unwrap()
   d = {GuardedBool("yes").unwrap(): "value"}
   ```

2. **Ne pas ignorer les métadonnées**
   ```python
   # ❌ Ignorer l'uncertainty
   price = GuardedFloat(dirty_input)
   charge_customer(price)
   
   # ✅ Vérifier la confiance
   price = GuardedFloat(dirty_input)
   if price.uncertainty <= Tolerance.PRECISE:
       charge_customer(price)
   else:
       ask_confirmation(price)
   ```

---

## XIII. Comparaison avec Pydantic

| Aspect | Pydantic | OpenHosta Guarded |
|--------|----------|-------------------|
| **Philosophie** | Validation stricte | Conversion tolérante |
| **Entrée** | Données structurées | N'importe quoi |
| **Échec** | Lève ValidationError | Tente de réparer |
| **Performance** | ⚡ Très rapide | 🐢 Plus lent (si parsing) |
| **Métadonnées** | Non | Oui (uncertainty, level) |
| **Cas d'usage** | APIs, Config | Agents IA, Scraping |

**Utilisez Pydantic** pour valider des APIs techniques.  
**Utilisez Guarded** pour parser des entrées humaines ou LLM.

---

## XIV. Limitations Connues

### 14.1 Bugs Connus

1. **GuardedList - Parsing CSV**
   - `GuardedList("1,2,3")` convertit en liste de caractères
   - **Workaround** : Utiliser format JSON `"[1,2,3]"`

2. **ProxyWrapper - isinstance()**
   - `isinstance(GuardedBool("yes"), bool)` retourne `False`
   - **Workaround** : Utiliser `.unwrap()` pour le type natif

### 14.2 Types Non Implémentés

- `GuardedRange` (partiel)
- `GuardedMemoryView` (partiel)
- `GuardedCode` (partiel)
- Parsing semantic (LLM) non connecté

---

## XV. Exemples Complets

### 15.1 Validation de Formulaire

```python
from OpenHosta.guarded import GuardedInt, GuardedUtf8, GuardedBool

# Données sales d'un formulaire web
form_data = {
    "name": "  Alice  ",
    "age": "vingt-cinq",  # Nécessiterait LLM (non implémenté)
    "age": "25 ans",      # Fonctionne avec heuristic
    "newsletter": "oui"
}

name = GuardedUtf8(form_data["name"])      # "Alice"
age = GuardedInt(form_data["age"])         # 25
newsletter = GuardedBool(form_data["newsletter"])  # True

print(f"{name}, {age} ans, newsletter: {newsletter.unwrap()}")
```

### 15.2 Parsing de Configuration

```python
from OpenHosta.guarded import GuardedInt, GuardedDict

config_str = '{"port": "8080", "debug": "true"}'
config = GuardedDict(config_str)

port = GuardedInt(config["port"])  # 8080
```

---

## XVI. Ressources

- **Code source** : `src/OpenHosta/guarded/`
- **Tests** : `tests/guarded/`
- **Exemples** : `test_guarded_basic.py`

**Modules** :
- `primitives.py` - Classe de base `GuardedPrimitive`
- `constants.py` - Énumérations `Tolerance`
- `subclassablescalars.py` - Types scalaires
- `subclassablewithproxy.py` - Types proxy
- `subclassablecollections.py` - Collections et dataclasses
- `subclassableclasses.py` - GuardedEnum
- `resolver.py` - Résolution de types
