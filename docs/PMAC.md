
# Compilateur assisté par modèle pré-entraîné (PMAC)

**Un [Compilateur](https://fr.wikipedia.org/wiki/Compilateur) Assisté par Modèle Pré-Entraîné** (Acronyme anglais : PMAC) est un concept qui utilise les [modèles de langage multimodaux](https://fr.wikipedia.org/wiki/Mod%C3%A8les_de_langage_multimodaux) de grande taille (MLLM) pour améliorer le processus de compilation. Ce concept vise à rapprocher le [langage informatique](https://fr.wikipedia.org/wiki/Langage_informatique) compilable du [langage naturel](https://fr.wikipedia.org/wiki/Langage_naturel) tout en respectant la syntaxe et la structure établies des langages de programmation.

## Histoire

L'apparition des [transformeurs](https://fr.wikipedia.org/wiki/Transformeur), introduits par [Google](https://fr.wikipedia.org/wiki/Google) en 2017, a radicalement changé le paysage technologique, en particulier dans le domaine du [traitement du langage naturel](https://fr.wikipedia.org/wiki/Traitement_du_langage_naturel). Ces modèles ont ouvert la voie à des avancées significatives, perturbant les méthodes traditionnelles d'interaction linguistique. En 2022, [OpenAI](https://fr.wikipedia.org/wiki/OpenAI) a lancé [ChatGPT](https://fr.wikipedia.org/wiki/ChatGPT), qui a marqué un tournant majeur en établissant de nouvelles références en matière de dialogue automatisé et d'interaction avec des machines.

Parmi les innovations qui ont suivi, [LangChain](https://www.langchain.com/), introduit en 2023, a permis aux développeurs d'intégrer des modèles de langage avancés dans les applications logicielles. Cette évolution a simplifié le développement d'applications conversationnelles et ouvert la voie à l'utilisation généralisée de l'IA dans des contextes de programmation traditionnels.

En parallèle, 2023 a vu [GitHub](https://fr.wikipedia.org/wiki/GitHub) introduire [Copilot](https://fr.wikipedia.org/wiki/GitHub_Copilot), une assistance IA permettant de suggérer du code contextuel, révolutionnant la productivité et le processus de codage.

Dans ce contexte d'innovation rapide, l'intégration de l'intelligence artificielle dans une multitude de domaines, y compris le processus de compilation, devient évidente. En 2024, le concept de PMAC voit le jour à Lyon, conçu par un équipe de passionées : [Emmanuel Batt](https://fr.wikipedia.org/wiki/Emmanuel_Batt), [Léandre Ramos](https://fr.wikipedia.org/wiki/L%C3%A9andre_Ramos), [William Jolivet](https://fr.wikipedia.org/wiki/William_Jolivet) et [Merlin Devillard](https://fr.wikipedia.org/wiki/Merlin_Devillard). En parallèle, [Meta](https://fr.wikipedia.org/wiki/Meta_(entreprise)) explore une approche similaire avec le développement de son [LLM Compiler](https://arxiv.org/abs/2407.02524).

## Principe de Base

Avec l'émergence de l'intelligence artificielle et l'évolution continue des modèles de langage, en particulier les modèles multimodaux, les capacités de traitement du NLP ([Natural Language Processing](https://fr.wikipedia.org/wiki/Traitement_automatique_des_langues)) se sont considérablement améliorées. Cette avancée permet de réévaluer les étapes traditionnelles de la compilation en intégrant une compréhension plus profonde et contextuelle des langages de programmation.

En programmation, un compilateur est un outil qui traduit un [langage de programmation](https://fr.wikipedia.org/wiki/Langage_de_programmation) en un [langage machine](https://fr.wikipedia.org/wiki/Langage_machine) , permettant aux ordinateurs d'exécuter les instructions. Les langages de programmation varient par leur niveau d'abstraction, allant des [langages de bas niveau](https://fr.wikipedia.org/wiki/Langage_de_programmation_de_bas_niveau), proches de l'architecture matérielle (langage machine), aux [langages de haut niveau](https://fr.wikipedia.org/wiki/Langage_de_programmation_de_haut_niveau), conçus pour être plus abstraits et lisibles pour les humains.

Le concept de PMAC utilise les MLLM pour traduire du code contenant des expressions plus claires et concrètes. Cette approche confie le traitement des ambiguïtés au PMAC, ce qui permet de gérer des aspects que les compilateurs traditionnels ne pouvaient pas traiter auparavant. Cela offre une interprétation plus précise des opérations programmatiques, permettant ainsi l'apparition de fonctions plus nuancées et complexes.

## Avantages et Inconvénients

|**Avantages**|**Inconvénients**|
|---|---|
|**Flexibilité des entrées :** Les fonctions peuvent être spécifiées en langage naturel, permettant ainsi l'exécution d'actions complexes qui seraient autrement difficiles, voire impossibles, à réaliser avec des instructions machine traditionnelles.|**Temps de compilation plus lent :** L'utilisation de MLLM peut entraîner des temps de compilation plus longs par rapport aux méthodes traditionnelles.|
|**Variété des stratégies d'implémentation :** Le compilateur PMAC peut générer divers types de stratégies d'implémentation, facilitant ainsi l'intégration de différents modes d'exécution adaptés aux besoins spécifiques de l'utilisateur.|**Coût plus élevé :** Les appels [API](https://fr.wikipedia.org/wiki/Interface_de_programmation) aux modèles ou leur stockage peut entraîner des coûts supplémentaires significatifs.|
|**Optimisation du code :** Grâce à la vaste connaissance des [LLM](https://fr.wikipedia.org/wiki/Grand_mod%C3%A8le_de_langage) en matière de code, PMAC intègre efficacement des techniques d'optimisation, améliorant ainsi les performances du code compilé par une compréhension approfondie des structures et logiques sous-jacentes.|**Imperfections des modèles :** Les modèles peuvent présenter des erreurs ou des divergences, posant des risques potentiels pour la fiabilité du code.|

 