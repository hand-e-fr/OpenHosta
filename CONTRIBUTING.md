# Guide de Contribution

Merci de votre intérêt pour contribuer à OpenHosta ! Nous apprécions les contributions de la communauté et nous sommes ravis de collaborer avec vous pour améliorer ce projet.

All types of contributions are encouraged and valued. See the Table of Contents for different ways to help and details about how this project handles them. Please make sure to read the relevant section before making your contribution.

> And if you like the project, but just don't have time to contribute, that's fine. There are other easy ways to support the project and show your appreciation, which we would also be very happy about:
> - Star the project
> - Tweet about it
> - Refer this project in your project's readme
> - Mention the project at local meetups and tell your friends/colleagues

### Table of Content

- [Guide de Contribution](#guide-de-contribution)
    - [Table of Content](#table-of-content)
  - [Comment contribuer](#comment-contribuer)
    - [Signaler des Bugs](#signaler-des-bugs)
    - [Proposer des Améliorations](#proposer-des-améliorations)
    - [Soumettre des Modifications](#soumettre-des-modifications)
  - [StyleGuide](#styleguide)
    - [Revue de Code](#revue-de-code)
    - [Style de Codage](#style-de-codage)
    - [Documentation](#documentation)
    - [Tests](#tests)
  - [Conclusion](#conclusion)
    - [Informations Additionnelles](#informations-additionnelles)

---

## Comment contribuer

### Signaler des Bugs

Si vous trouvez un bug, veuillez ouvrir une issue sur notre [dépôt GitHub](https://github.com/hand-e-fr/OpenHosta-dev/issues) et inclure autant de détails que possible. Veuillez fournir les informations suivantes :

- Une description claire et concise du bug.
- Les étapes pour reproduire le bug.
- La version de Python et les dépendances utilisées.
- Toute autre information pertinente (logs, captures d'écran, etc.).

### Proposer des Améliorations

Nous accueillons avec plaisir les suggestions d'amélioration. Si vous avez une idée pour améliorer OpenHosta, veuillez ouvrir une issue sur notre [dépôt GitHub](https://github.com/hand-e-fr/OpenHosta-dev/issues) et décrire votre suggestion en détail. Veuillez inclure :

- Une description claire et concise de l'amélioration proposée.
- Les raisons pour lesquelles vous pensez que cette amélioration est nécessaire.
- Toute autre information pertinente (exemples de code, liens vers d'autres projets, etc.).

### Soumettre des Modifications

Si vous souhaitez apporter des modifications au code, veuillez suivre les étapes suivantes :

1. **Fork le Dépôt** : Cliquez sur le bouton "Fork" en haut de la page pour créer une copie de ce dépôt sur votre compte GitHub.

2. **Cloner votre Fork** : Clonez votre fork localement en utilisant la commande suivante :
    ```sh
    git clone https://github.com/votre-utilisateur/OpenHosta-dev.git
    ```

3. **Créer une Branche** : Créez une nouvelle branche pour votre fonctionnalité ou correction de bug :
    ```sh
    git checkout -b ma-nouvelle-fonctionnalite
    ```

4. **Faire vos Modifications** : Apportez les modifications nécessaires dans votre éditeur de code préféré.

5. **Committer les Changements** : Ajoutez et commitez vos changements avec des messages de commit clairs et descriptifs :
    ```sh
    git add .
    git commit -m "Ajout de ma nouvelle fonctionnalité"
    ```

6. **Pousser votre Branche** : Poussez votre branche sur votre fork GitHub :
    ```sh
    git push origin ma-nouvelle-fonctionnalite
    ```

7. **Ouvrir une Pull Request** : Allez sur le dépôt original et ouvrez une Pull Request depuis votre fork. Décrivez les modifications que vous avez apportées et pourquoi elles sont nécessaires.

---

## StyleGuide

### Revue de Code

Toutes les contributions feront l'objet d'une revue de code par les mainteneurs du projet. Veuillez être patient pendant que nous examinons votre Pull Request. Nous pouvons demander des modifications avant de fusionner votre contribution.

### Style de Codage

Veuillez vous assurer que votre code suit les conventions de style du projet. Nous utilisons `black` comme guide de style pour Python. Vous pouvez utiliser des outils comme `flake8` pour vérifier que votre code respecte ces conventions.

### Documentation

Si vous ajoutez une nouvelle fonctionnalité, veuillez mettre à jour la documentation en conséquence. La documentation doit être claire, concise et inclure des exemples d'utilisation.

### Tests

Assurez-vous que votre contribution inclut des tests appropriés. Les tests doivent couvrir les cas d'utilisation courants ainsi que les cas limites. Vous pouvez exécuter les tests en utilisant la commande suivante :
```sh
pytest
```
---

## Conclusion

### Informations Additionnelles
Nous avons adopté un [Code de Conduite](CODE_OF_CONDUCT.md) pour garantir un environnement respectueux et inclusif pour tous les contributeurs. Veuillez prendre un moment pour le lire avant de commencer à contribuer.

Si vous avez des questions ou besoin d'assistance supplémentaire, n'hésitez pas à nous contacter à l'adresse suivante : support@openhosta.com.

---

Merci encore pour votre intérêt à contribuer à OpenHosta !

**L'équipe OpenHosta**