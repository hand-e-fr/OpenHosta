# 📄 DOCUMENT D'ARCHITECTURE : OpenHosta.Guarded

Rôle IA actif : Architect

Statut : Spécification Officielle de Référence

Sujet : Typage probabiliste, Self-Healing, Représentations Tri-Modales et DX pour LLM.

## 1. BRIEF (Contexte et Objectifs)

### 1.1. Le Véritable Problème : La destruction de l'Expérience Développeur (DX)

L'intégration de données génératives (LLMs, parsing heuristique) dans des applications métiers strictement typées crée une friction majeure. Les approches classiques ruinent l'expérience développeur :

- L'approche "Wrapper" classique : Oblige le développeur métier à écrire du code défensif et lourd (if isinstance(val, Wrapper): val = val.value). La logique métier est polluée par la gestion de l'incertitude.
    
- L'approche "Silent Cast" : Force la donnée brute dans le type attendu, mais détruit la traçabilité. Si un LLM a dû s'y reprendre à 3 fois (retries/healing) pour formater un JSON, l'équipe Ops n'a plus aucun moyen d'investiguer ce coût caché.
    

### 1.2. La Solution : L'illusion parfaite avec OpenHosta.Guarded

Créer un méta-type Guarded[T] qui résout cette dichotomie. La solution doit :

- Côté Métier (DX) : Offrir l'illusion parfaite que la donnée est de type T (Duck Typing absolu).
    
- Côté Moteur (Contrôle & Self-Healing) : Permettre de définir déclarativement l'incertitude et le budget maximums tolérés, et s'auto-réparer en cas d'erreur.
    
- Côté Ops (Observabilité) : Transporter silencieusement les traces de l'IA (logs, temps consommé, traces de healing) en agrégeant dynamiquement les coûts à travers les graphes de données.
    

## 2. MAP (Conception et Principes Architecturaux)

Notre approche repose sur des principes inaliénables pour garantir l'adoption par les développeurs :

1. Principe de Transparence (Duck Typing) : L'objet Guarded[T] doit réagir aux opérateurs standards (==, +, getattr) exactement comme T.
    
2. Principe de Zéro-Collision : Les métadonnées sont stockées dans des attributs dunder exclusifs (__guard_data__). Aucune modification n'est apportée à l'objet natif.
    
3. Principe de Déclaration Native : L'interface utilise typing.Annotated pour s'intégrer nativement avec les linters (Mypy, Pyright).
    
4. Principe de Symétrie Récursive Structurée : Les opérations guard() et unguard() parcourent automatiquement les graphes de données (dict, list, Dataclasses, Pydantic) jusqu'aux feuilles.
    
5. Principe de Cohérence et d'Agrégation des Métadonnées : L'attribution de l'incertitude et des coûts est cumulative.
    

- Si un self-healing a lieu sur une sous-donnée, sa métadonnée locale stocke ces compteurs spécifiques.
    
- Lorsqu'une structure parente (ex: liste, dict) est interrogée via guard_info(), elle retourne la somme des coûts et incertitudes de ses enfants.
    
- Une variable native (non Guarded) a par définition une incertitude de 0, un coût de 0ms et aucune trace.
    

6. Principe du Miroir LLM (Tri-Modal) : L'application doit pouvoir s'expliquer au LLM. Le framework fournit des outils pour exporter n'importe quel type métier en Python, JSON Schema ou Markdown pour construire des prompts robustes.
    

## 3. ACT (Implémentation Core)

```python

import inspect  
import dataclasses  
from enum import Enum  
from typing import TypeVar, Generic, Any, Annotated, Type  
from dataclasses import dataclass, field  
  
T = TypeVar('T')  
  
@dataclass  
class GuardConfig:  
    max_uncertainty: float  
    max_effort_ms: int
    heal_retries_per_layer: int = 2
  
@dataclass  
class GuardMetadata:  
    uncertainty: float = 0.0  
    time_consumed: float = 0.0  
    llm_logs: list[dict] = field(default_factory=list)  
    heal_traces: list[str] = field(default_factory=list)  
  
    def __add__(self, other: 'GuardMetadata') -> 'GuardMetadata':  
        """Permet l'agrégation facile des métadonnées."""  
        return GuardMetadata(  
            uncertainty=self.uncertainty + other.uncertainty,  
            time_consumed=self.time_consumed + other.time_consumed,  
            llm_logs=self.llm_logs + other.llm_logs,  
            heal_traces=self.heal_traces + other.heal_traces  
        )  
  
class Guarded(Generic[T]):  
    """Le Proxy transparent (Zero-Collision Duck Typing)."""  
    def __init__(self, value: T, metadata: GuardMetadata):  
        self.__guard_value__ = value  
        self.__guard_data__ = metadata  
  
    def __getattr__(self, name: str) -> Any: return getattr(self.__guard_value__, name)  
    def __eq__(self, other: Any) -> bool:  
        if isinstance(other, Guarded): return self.__guard_value__ == other.__guard_value__  
        return self.__guard_value__ == other  
    def __hash__(self) -> int: return hash(self.__guard_value__)  
    def __repr__(self) -> str: return repr(self.__guard_value__)  
```

## 4. SPÉCIFICATION D'INTERFACE (Manuel Utilisateur)

Voici le manuel de référence des fonctions exposées par la bibliothèque OpenHosta.Guarded.

### 4.1. Configuration et Types

- GuardConfig(max_uncertainty: float, max_effort_ms: int, heal_retries_per_layer)
    

- Description : Dataclass utilisée dans typing.Annotated pour définir le contrat de génération/validation.
    

- GuardMetadata
    

- Description : Contient l'empreinte de la génération IA (incertitude, temps, logs LLM et traces de healing). Supporte l'addition pour l'agrégation.
    

### 4.2. Cycle de vie de la Donnée (Core API)

- guard(value: Any, metadata: GuardMetadata = None) -> Any
    

- Description : Encapsule récursivement une valeur. Traverse les listes, dicts, Dataclasses et Pydantic. Si value est une structure contenant déjà des sous-éléments Guarded, le metadata parent généré sera l'addition des métadonnées de tous les enfants + le metadata passé en paramètre.
    
- Exemple : my_list = guard([guarded_val1, guarded_val2]) -> guard_info(my_list) renverra la somme exacte des coûts de val1 et val2.
    

- unguard(obj: Any) -> Any
    

- Description : Extrait récursivement la valeur d'origine. Nettoie tout le graphe de données de ses proxies Guarded, purifiant l'objet pour un export (JSON, Base de données) garanti sans erreur.
    

- guard_info(obj: Any) -> GuardMetadata | None
    

- Description : La fonction d'observabilité (Ops). Expose les métadonnées de trace liées à un objet Guarded.
    
- Comportement : Si l'objet est une structure complexe (ex: liste) contenant des éléments Guarded, la fonction parcourt l'objet à la volée et retourne la somme globale des incertitudes et coûts. Retourne un GuardMetadata vide (tout à 0) si l'objet est 100% natif.
    

### 4.3. Interface Tri-Modale (Communication LLM)

- guarded_to_python(target: Type | Any) -> str
    

- Description : Génère le code source Python de la structure via introspection. Idéal pour prompter des LLMs codeurs.
    

- guarded_to_json(target: Type | Any) -> dict
    

- Description : Génère un JSON Schema standard représentant le type cible. Délègue à Pydantic si disponible. Idéal pour configurer l'API response_format des LLMs.
    

- guarded_to_markdown(target: Type | Any) -> str
    

- Description : Génère une description textuelle et sémantique lisible par un humain et optimisée pour un LLM dans un System Prompt (Zero-shot extraction).
    

### 4.4. Le Registre de Layers (Extensions)

- REGISTRY.register_layer(name: str, condition: callable, layer_logic: callable)
    

- Description : Permet d'ajouter une logique d'instanciation personnalisée pour des objets métiers inconnus du moteur. Les layers Pydantic, Enum et Primitives sont inclus par défaut dans openhosta.guarded.layers.
    

## 5. DELIVER (Cas d'Usage et Synergie)

### Exemple 1 : Définition, DX et Self-Healing

```python
from openhosta.guarded import GuardConfig, guard_info  
  
# Contrat : 15% d'incertitude max, auto-healing activé  
SafeEnum = Annotated[MyEnum, GuardConfig(15, 1500)]  
  
# Le LLM hallucine la valeur "value3".  
# Le moteur tente le cast, échoue, et active le self-healing (ex: fuzzy matching).  
# La valeur est corrigée silencieusement en MyEnum.VALUE2.  
action = my_llm_engine.cast("value3", target_type=SafeEnum)  
  
# DX Parfaite : Le linter et le runtime acceptent cette comparaison directement.  
if action == MyEnum.VALUE2:  
    player.jump()  
  
# Observabilité : On peut inspecter la guérison  
print(guard_info(action).heal_traces)  
# ["Enum parsing failed for 'value3'.", "Healed 'value3' -> 'value2'."]  
  

### Exemple 2 : Agrégation Récursive des Coûts

from openhosta.guarded import guard, guard_info, GuardMetadata  
  
# Création de deux valeurs avec des budgets consommés distincts  
val1 = guard("Paris", GuardMetadata(uncertainty=5.0, time_consumed=150))  
val2 = guard("Lyon", GuardMetadata(uncertainty=10.0, time_consumed=300))  
native_val = "Marseille" # incertitude 0, cout 0  
  
# On encapsule le tout dans une structure globale (ex: une réponse de LLM)  
# L'opération `guard` sur la liste va sommer dynamiquement les métadonnées de ses enfants.  
city_list = guard([val1, val2, native_val])  
  
info = guard_info(city_list)  
print(f"Coût total: {info.time_consumed}ms | Incertitude: {info.uncertainty}%")  
# Affiche : Coût total: 450ms | Incertitude: 15.0%  
```

### Exemple 3 : Injection du Contexte Tri-Modal

Avant de demander au LLM de générer de la donnée, on lui explique notre typage natif grâce aux fonctions Tri-Modales :

```python
from openhosta.guarded import guarded_to_markdown, guarded_to_json  
from pydantic import BaseModel  
import json  
  
class UserProfile(BaseModel):  
    age: int  
    role: MyEnum  
  
prompt = f"""  
Extrais l'intention de l'utilisateur.  
Voici la définition attendue :  
{guarded_to_markdown(UserProfile)}  
  
Format de réponse strict :  
\`\`\`json  
{json.dumps(guarded_to_json(UserProfile), indent=2)}  
\`\`\`

```

# Le LLM reçoit un contexte parfait, réduisant les hallucinations et

# allégeant le besoin de self-healing a posteriori.

### Exemple 4 : Exportation (Sauvegarde propre)  
```python  
from openhosta.guarded import unguard  
from openai import client

answer:str = client.cast(raw_text)  
guarded_data:Guarded[UserProfile] = guard(answer, target_type=UserProfile, config=GuardConfig(0.1, 2000))   # Type-safety garanti par Guarded[UserProfile]

# On a un graphe d'objets truffé de proxys Guarded[T]  
  
clean_data = unguard(guarded_data)
# Retourne un dict Pydantic purifié, prêt pour une base de données SQL ou une API classique.  
db.save(clean_data)  
  
```

