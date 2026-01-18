
📖 Documentation OpenHosta.semantics
---


OpenHosta.semantics est une bibliothèque qui permet de manipuler des données non plus par leur syntaxe (les lettres qui les composent), mais par leur sens (leur sémantique). Elle est optimisée pour les architectures d'agents et le traitement du langage naturel.

# I. Les Fondamentaux : Pourquoi la Sémantique ?

##1.1 Le passage au "Flou Maîtrisé"

En informatique classique, le test if "Chat" == "Félin": est toujours Faux. En sémantique, nous mesurons une distance. Si deux concepts sont assez proches, nous considérons qu'ils sont égaux.

## 1.2 Le concept de semantic_tolerance

C'est le curseur qui définit la "souplesse" de votre code.
 * Tolerance = 0.0 : Équivalent au Python standard (stricte égalité).
 * Tolerance = 0.05 : Accepte les synonymes quasi parfaits.
 * Tolerance = 0.15 : Accepte des concepts élargis (ex: "Voiture" et "Automobile").

## II. L'Objet de Base : SemanticType

Le SemanticType est une classe qui définit un contexte. Il permet d'utiliser l'opérateur == de manière intelligente.
from OpenHosta.semantics import SemanticType

class Animal(SemanticType):
    """Représente le domaine des animaux domestiques."""
    semantic_tolerance = 0.1  # Tolérance aux synonymes

# Usage simple
chat = Animal("Un petit chaton")
felin = Animal("Un félin domestique")

if chat == felin:
    print("Le système comprend que c'est le même concept.")

> [!CAUTION]
> Attention : Bien que chat == felin fonctionne pour un test if, n'utilisez jamais un SemanticType comme clé dans un dictionnaire standard dict(). Pour cela, utilisez le SemanticDict fourni par la lib (voir section III).
> 
III. Les Collections Sémantiques
Les collections OpenHosta ne se contentent pas de stocker des données, elles les organisent.
3.1 SemanticSet (L'ensemble auto-synthétisé)
Un SemanticSet regroupe les éléments par "clusters" de sens.
 * Ajout intelligent : Si vous ajoutez un synonyme, il rejoint le groupe existant sans créer de doublon.
 * Centroïdes et Labels : La bibliothèque calcule le "centre de gravité" de chaque groupe. Le nom affiché du groupe est généré par un LLM à partir des éléments les plus représentatifs.
 * Rebalance automatique : Chaque ajout recalcule l'équilibre pour s'assurer que le nom du groupe est toujours le plus précis.
<!-- end list -->
from OpenHosta.semantics import SemanticSet

tasks = SemanticSet(type=Animal)
tasks.add("Nourrir le chat")
tasks.add("Donner à manger au félin") # Fusionné avec le précédent

# Le print n'affichera pas "Nourrir le chat", mais un label synthétique
# généré par LLM, par exemple : "Alimentation animale"
print(tasks) 

3.2 SemanticDict (Le dictionnaire à boussole)
Il fonctionne comme un dictionnaire classique, mais sa clé est un concept.
from OpenHosta.semantics import SemanticDict

router = SemanticDict(key_type=Animal)
router["Chat"] = "Appeler le vétérinaire"

# On cherche avec une phrase différente
print(router["Mon chaton semble malade"]) 
# Output: "Appeler le vétérinaire"

IV. Cas d'Usage : Agents et Workflows
4.1 Routage d'Intention
Idéal pour diriger une requête utilisateur vers le bon agent sans faire de longues listes de mots-clés.
4.2 Déduplication de Mémoire
Permet à un agent d'enregistrer des faits dans sa mémoire sans stocker dix fois la même information formulée différemment.
V. Architecture et Optimisations (Experts)
Cette section explique comment OpenHosta reste rapide et fiable "sous le capot".
5.1 Recherche Vectorielle O(\log n)
Plutôt que de demander au LLM de comparer chaque mot (très lent), OpenHosta transforme chaque texte en un vecteur numérique (embedding).
Nous utilisons ensuite Scikit-learn (algorithme BallTree) pour trouver instantanément les voisins les plus proches dans cet espace vectoriel.
5.2 Pourquoi un SemanticDict plutôt qu'un dict classique ?
En Python, un dictionnaire natif utilise le Hachage. Pour que dict[A] trouve B, il faut que hash(A) == hash(B). Or, il est impossible de garantir des hashs identiques pour des sens proches sans casser la logique de Python.
SemanticDict contourne ce problème en remplaçant la table de hachage par un index spatial.
5.3 Visualisation et Debug
Vous pouvez à tout moment voir comment vos données sont regroupées :
# Affiche une projection 2D de vos clusters sémantiques
tasks.visualize()

5.4 Reproductibilité
 * Seed Freeze : Les vecteurs sont générés avec une graine aléatoire fixe.
 * Config Hash : Si vous changez de modèle de langue, vos collections existantes sont verrouillées pour éviter de comparer des "pommes" (Modèle A) avec des "oranges" (Modèle B).
Souhaitez-vous que je développe un exemple de code spécifique pour la migration de données (.migrate()) entre deux configurations de modèles différentes ?
