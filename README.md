# OpenHosta Documentation

**- The future of development is human -**

Bienvenue dans la documentation d'OpenHosta, un outil puissant qui facilite l'intégration de fonctions spécifiques à un projet tout en permettant aux débutants de comprendre clairement le projet. OpenHosta sert à émuler des fonctions grâce à l'IA, comparer leurs résultats avec des fonctions codées, et générer des logs détaillés pour chaque appel de fonction. 

---

### Prerequisites

1. **Python 3.8+**
   - Téléchargez et installez Python depuis [python.org](https://www.python.org/downloads/).

2. **pip**
   - pip est généralement inclus avec Python. Vérifiez son installation avec `pip --version`.

3. **Git**
   - Téléchargez et installez Git depuis [git-scm.com](https://git-scm.com/downloads).

4. **Environnement Virtuel (optionnel)**
   - Créez et activez un environnement virtuel :
     ```bash
     python -m venv env
     .\env\Scripts\activate
     ```

5. **Clé API**
   - **Clé API** : Connectez vous à votre compte openai depuis [openai.com](https://openai.com/), puis créez votre clé API.

### Installation

1. Commencez par cloner le **dépôt Git** sur votre machine locale en utilisant la commande suivante:

```bash
git clone git@github.com:hand-e-fr/OpenHosta-dev.git
```

2. Accédez au **répertoire** du projet cloné:

```bash
cd OpenHosta-dev
```

3. Assurez-vous d'avoir installé les dépendances nécessaires avant de commencer.

```bash
pip install -r requirements.txt
```

---

### Usage

Assurez-vous d'importer la bibliothèque.

```python
import OpenHosta
```

Voici un exemple simple d'utilisation:

```python
llm = OpenHosta.emulator()    # Vous devez mettre vos clé api et le modèle en paramètre

@llm.emulate                  # @llm.enhance | @llm.oracle
def example(a:int, b:int)->int:  # Mettre votre prompt dans les docstrings
   """
   This is an example very precise prompt.  
   """
   pass                       # La fonction ne contient donc pas d'instruction

example(4, 2)                 # Appel de la fonction pour activer le décorateur      
```

### Features

```python
llm = emulator()
```

- `llm` contient trois décorateurs principaux :
  - `@llm.emulate` : Décore une fonction pour émuler son exécution par une IA. Vous pouvez choisir le modèle grâce à votre clé API.
  - `@llm.enhance` : Décore une fonction et génère un diagramme Mermaid pour visualiser et comprendre le raisonnement du modèle ainsi qu'un fichier markdown d'aide pour améliorer le prompt de la fonction. Le tout est stocké dans le répertoire `.openhosta` à la racine du répertoire de travail.
  - `@llm.oracle` : Décore une fonction pour capturer les informations et les résultats dans un format JSON. Il est couramment utilisé pour valider les résultats des fonctions IA et générer des données de test. Il identifie chaque fonction par différents paramètres et sert à comparer les valeurs de sortie.

### Configuration

La classe `emulator` peut avoir quatres paramètres:
   - `model` : Modèle de llm auqel le programme va envoyer ses requêtes
   - `creativity` & `diversity` : Correspond au paramètre "temperature" et "top_p" des llm. Pour plus d'information, veuillez consulter la documentation officielle  [openai.com](https://openai.com/)
   - `api_key` :

---

### Contributing

### License

### Authors & Contact

Pour toute question ou assistance supplémentaire, n'hésitez pas à consulter notre documentation complète ou à contacter notre support technique.

