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
cd nom-du-projet
```

3. Assurez-vous d'avoir installé les dépendances nécessaires avant de commencer.

```bash
pip install -r requirements.txt
```

---

### Usage

Assurez-vous d'importer la bibliothèque.

```python
from OpenHosta import emulator
```

### Features

```python
llm = emulator()
```

- `llm` contient deux décorateurs principaux :
  - `@llm.emulate` : Décore une fonction pour simuler son exécution par une IA. Il génère également un diagramme Mermaid pour visualiser et comprendre le raisonnement du modèle.
  - `@llm.oracle` : Décore une fonction pour capturer les informations et les résultats dans un format JSON. Il est couramment utilisé pour valider les résultats des fonctions IA et générer des données de test.

### Configuration

---

### Contributing

### License

### Authors & Contact

Pour toute question ou assistance supplémentaire, n'hésitez pas à consulter notre documentation complète ou à contacter notre support technique.

