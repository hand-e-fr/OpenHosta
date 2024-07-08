# Documentation OpenHosta

Bienvenue dans la documentation d'OpenHosta, un outil puissant qui facilite l'intégration de fonctions spécifiques à un projet tout en permettant aux débutants de comprendre clairement le projet.

### Installation

Assurez-vous d'avoir installé les dépendances nécessaires avant de commencer.

```bash
pip install -r requirements.txt
```

### Importer la bibliothèque

Assurez-vous d'importer la bibliothèque.

```python
from OpenHosta import emulator
```

### Étapes :

```python
llm = emulator()
```

- `llm` contient deux décorateurs principaux :
  - `@llm.emulate` : Décore une fonction pour simuler son exécution par une IA. Il génère également un diagramme Mermaid pour visualiser et comprendre le raisonnement du modèle.
  - `@llm.oracle` : Décore une fonction pour capturer les informations et les résultats dans un format JSON. Il est couramment utilisé pour valider les résultats des fonctions IA et générer des données de test.

---

### Conclusion

OpenHosta est un outil puissant pour simuler des fonctions IA, comparer leurs résultats avec des fonctions codées, et générer des logs détaillés pour chaque appel de fonction. Cette documentation vous guide à travers un exemple simple pour vous aider à comprendre comment l'implémentation fonctionne et comment vous pouvez l'utiliser dans vos projets.

Pour toute question ou assistance supplémentaire, n'hésitez pas à consulter notre documentation complète ou à contacter notre support technique.
