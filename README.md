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

### Code Exemple

Pour illustrer comment utiliser l'Emulator, nous allons créer une classe `Documentation` qui contient des méthodes pour ajouter deux nombres en utilisant à la fois une fonction AI simulée et une fonction humaine.

```python
class Documentation():
    def __init__(self):
        pass

    @llm.emulate
    def AI_add_two_numbers(self, a: int, b: int) -> int:
        """
        This function adds two numbers
        """
        pass

    def Human_add_two_numbers(self, a: int, b: int) -> int:
        return a + b

    def oracle_debuger(self, a: int, b: int) -> bool:
        if a == b :
            return True
        else :
            return False

    @llm.oracle
    def tests(self, a: int, b: int) -> int:

        add_1 = self.AI_add_two_numbers(a, b)
        print(f"Result of AI addition: {add_1}")

        add_2 = self.Human_add_two_numbers(a, b)
        print(f"Result of Human addition: {add_2}")

        data_game = [add_1, add_2]
        result = self.oracle_debuger(add_1, add_2)

        if result == True:
            return data_game, 0
        else:
            return data_game, 1
```

### Explication du Code

1. **Initialisation de l'Emulator**:
   - Nous commençons par initialiser l'Emulator avec `llm = emulator()`.

2. **Définition de Fonctions**:
   - `AI_add_two_numbers` : Une fonction simulée pour ajouter deux nombres en utilisant l'IA.
   - `Human_add_two_numbers` : Une fonction humaine équivalente pour ajouter deux nombres.
   - `horacle_debuger` : Une fonction de débogage pour comparer les résultats des deux fonctions.

3. **Comparaison des Résultats**:
   - La fonction `tests` appelle les deux fonctions (`AI_add_two_numbers` et `Human_add_two_numbers`), compare leurs résultats et génère un log JSON avec les métadonnées.

---

### Résultat

```python
# Exemple d'utilisation
example = Documentation()
json_output = example.tests(5, 2)

print(json_output)
```

Lorsque vous exécutez le code, vous obtenez une sortie qui inclut les résultats des additions AI et humaines, ainsi qu'un log JSON structuré :

```plaintext
Result of AI addition: 7
Result of Human addition: 7
```

```json
{
     "Version": 0.1,
     "Id session": "abcd1234-1234-1234-abcdefghi",
     "Timestamp": 1000000000,
     "func_call": "tests(<__main__.Documentation object at 0x7f6c481f7c50>, 5, 2)",
     "func_hash": "6a136adf929de4c5a55d528e9ac4045e",
     "Tag output": 0,
     "Data": [
          7,
          7
     ]
}
```

---

### Conclusion

OpenHosta est un outil puissant pour simuler des fonctions IA, comparer leurs résultats avec des fonctions codées, et générer des logs détaillés pour chaque appel de fonction. Cette documentation vous guide à travers un exemple simple pour vous aider à comprendre comment l'implémentation fonctionne et comment vous pouvez l'utiliser dans vos projets.

Pour toute question ou assistance supplémentaire, n'hésitez pas à consulter notre documentation complète ou à contacter notre support technique.
