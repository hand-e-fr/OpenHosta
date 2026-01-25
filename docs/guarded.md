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
         0.00     0.05-0.15   0.15-0.30  0.30+
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

La tolérance définit jusqu'où le pipeline peut aller :

```python
from OpenHosta.guarded import GuardedInt, Tolerance

# Tolérance stricte : seul le niveau Native est accepté
strict_int = GuardedInt("42", tolerance=Tolerance.STRICT)

# Tolérance flexible : Native + Heuristic acceptés
flexible_int = GuardedInt("1,000", tolerance=Tolerance.FLEXIBLE)

# Tolérance par défaut : TYPE_COMPLIANT (accepte tout)
default_int = GuardedInt("1,000")  # Fonctionne
```

| Niveau | Constante | Valeur | Niveaux Acceptés |
|--------|-----------|--------|------------------|
| **Strict** | `Tolerance.STRICT` | 0.00 | Native uniquement |
| **Précis** | `Tolerance.PRECISE` | 0.05 | Native |
| **Flexible** | `Tolerance.FLEXIBLE` | 0.15 | Native + Heuristic |
| **Type Compliant** | `Tolerance.TYPE_COMPLIANT` | 0.999 | Tous (défaut) |

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

### 4.3 Comportement ProxyWrapper

⚠️ **Important** : Les types proxy ne sont PAS des instances du type natif.

```python
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

# Création depuis dict avec conversion automatique
p2 = Person({"name": "Bob", "age": "25"})  # age converti de str → int

# Les champs sont validés et convertis
assert p2.age == 25
assert isinstance(p2.age, int)  # Converti automatiquement
```

### 7.2 Avec Options Dataclass

Vous pouvez passer des options directement à `@guarded_dataclass` :

```python
@guarded_dataclass(frozen=True, order=True)
class Point:
    x: int
    y: int

pt = Point(x=10, y=20)
# pt.x = 100  # ❌ Erreur : frozen=True
```

### 7.3 Avec Valeurs Par Défaut

```python
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

### 7.4 Conversion Automatique des Types

Le décorateur utilise `TypeResolver` pour convertir automatiquement les valeurs :

```python
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

### 7.5 Métadonnées Guarded

Comme tous les types Guarded, les dataclasses conservent des métadonnées :

```python
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

### 7.6 Usage Legacy (Avec @dataclass Explicite)

Si vous avez déjà `@dataclass`, `@guarded_dataclass` le détecte et ne le réapplique pas :

```python
from dataclasses import dataclass

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

### 9.1 Exemple : Email d'Entreprise

```python
import re
from OpenHosta.guarded import GuardedPrimitive, GuardedUtf8, Tolerance, UncertaintyLevel
from typing import Tuple, Optional, Any

class CorporateEmail(GuardedUtf8):
    """Email d'entreprise avec domaines autorisés."""
    
    _type_en = "a corporate email address from mycorp.com or mycorp.net"
    _type_py = str
    _type_json = {
        "type": "string",
        "format": "email",
        "pattern": "^[a-z0-9._%+-]+@(mycorp\\.com|mycorp\\.net)$"
    }
    
    @classmethod
    def _parse_native(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        """Validation stricte."""
        if not isinstance(value, str):
            return UncertaintyLevel(Tolerance.ANYTHING), value, "Not a string"
        
        email = value.lower()
        
        # Vérifier le domaine
        if not email.endswith(("@mycorp.com", "@mycorp.net")):
            return UncertaintyLevel(Tolerance.ANYTHING), value, "Invalid domain"
        
        # Vérifier le format
        if re.match(r"^[a-z0-9._%+-]+@(mycorp\.com|mycorp\.net)$", email):
            return UncertaintyLevel(Tolerance.STRICT), email, None
        
        return UncertaintyLevel(Tolerance.ANYTHING), value, "Invalid format"
    
    @classmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        """Nettoyage avant validation."""
        if isinstance(value, str):
            # Nettoyer les espaces et "mailto:"
            cleaned = value.strip().lower()
            cleaned = cleaned.replace("mailto:", "").replace("<", "").replace(">", "")
            
            # Tenter validation native
            uncertainty, val, msg = cls._parse_native(cleaned)
            if uncertainty <= Tolerance.STRICT:
                return UncertaintyLevel(Tolerance.PRECISE), val, None
        
        return UncertaintyLevel(Tolerance.ANYTHING), value, None

# Utilisation
email = CorporateEmail("  mailto:john.doe@mycorp.com  ")
print(email)  # "john.doe@mycorp.com"
print(email.uncertainty)  # 0.05 (PRECISE - nettoyage heuristique)
```

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

2. **Spécifier la tolérance pour les cas critiques**
   ```python
   password = GuardedUtf8(input, tolerance=Tolerance.STRICT)
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
