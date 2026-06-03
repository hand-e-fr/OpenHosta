---
id: DOC-DX-004
type: guide
status: approved
title: Talk to my Data Agent
---

# Talk to my Data Agent — Guide pas à pas

Ce guide explique comment créer un agent OpenHosta v5 capable de lire des fichiers CSV dans un dossier spécifique et d'y répondre en langage naturel.

Nous allons utiliser :
- `BackendModel` et `@backend.compile()` pour le modèle LLM.
- `Workspace` pour gouverner l'accès au dossier CSV.
- `Agent` avec un `@tool` pour lire les CSV et un `@infer` pour répondre aux questions.

## Étape 1 : Installer les dépendances

OpenHosta est le runtime. Pour lire des CSV, nous utiliserons `pandas` (ou le module `csv` standard).

```bash
pip install openhosta pandas
```

## Étape 2 : Configurer le Backend et le Workspace

```python
from pathlib import Path
from openhosta import Agent, BackendModel, Workspace

# 1. Le backend (votre LLM local ou distant)
backend = BackendModel(
    provider="openai_compatible",
    model_name="cyankiwi/Qwen3.6-27B-AWQ-INT4",
    base_url="http://127.0.0.1:8000/v1",
    api_key="none"
)

# 2. Le Workspace (le dossier contenant vos CSV)
# Remplacez "/chemin/vers/mon/dossier_csv" par votre dossier réel
data_folder = Path("/chemin/vers/mon/dossier_csv")
workspace = Workspace(root=data_folder)
```

## Étape 3 : Définir l'Agent et ses capacités

L'agent aura deux capacités principales :
1. Un `@tool` déterministe pour lister et lire le contenu d'un fichier CSV.
2. Un `@infer` piloté par le modèle pour analyser les données et répondre à la question.

```python
import pandas as pd

@backend.compile()
class DataAgent(Agent):
    """Agent spécialisé dans l'analyse de fichiers CSV situés dans le workspace.
    
    Il lit les données de manière sécurisée et répond aux questions en langage naturel.
    """

    @tool(tags=["data", "read", "csv"])
    def read_csv_file(self, filename: str) -> str:
        """Lit un fichier CSV spécifique et retourne son contenu sous forme de chaîne structurée.
        
        Args:
            filename: Le nom du fichier CSV présent dans le workspace.
        """
        content = self.workspace.read(filename)
        # On peut retourner le texte brut pour que le LLM l'analyse via l'infer
        return content

    @infer(tags=["data", "analysis", "q&a"])
    def answer_data_question(self, question: str, csv_content: str | None = None) -> str:
        """Répond à une question basée sur le contenu d'un fichier CSV.
        
        Args:
            question: La question de l'utilisateur en langage naturel.
            csv_content: Le contenu brut du CSV (si déjà lu).
        """
        ...
```

## Étape 4 : Lancer l'agent et poser des questions

```python
def main():
    # Initialisation de l'agent
    agent = DataAgent(workspace=workspace)
    
    # Ouverture d'une session (recrutement)
    agent.recruit(quota=16000)
    
    # Exemple d'interaction : L'agent devra router vers read_csv_file puis answer_data_question
    # Ou le LLM utilisera le tool en interne via le dispatcher.
    result = agent.get("Quelles sont les ventes totales par région dans 'sales_2023.csv' ?")
    print(result)
    
    # Clôture propre de la session
    print(agent.free())

if __name__ == "__main__":
    main()
```

## Comment ça marche ?

1. **`Workspace`** : Garantit que l'agent ne peut lire que les fichiers présents dans `data_folder`. Il n'a aucun accès au reste du système de fichiers.
2. **`@tool read_csv_file`** : C'est la porte d'entrée déterministe. Quand le LLM décide qu'il a besoin de données, il appelle ce tool avec le nom du fichier.
3. **`@infer answer_data_question`** : C'est le moteur d'inférence. Le LLM injecte la question et le contenu CSV, et produit une réponse structurée ou textuelle.
4. **`agent.get()`** : C'est la surface conversationnelle. Elle dispatche automatiquement vers le bon outil ou l'inférence appropriée selon le besoin exprimé par l'utilisateur.

> 💡 *Astuce : Pour des fichiers très volumineux, adaptez `read_csv_file` pour retourner uniquement les 50 premières lignes ou un résumé statistique généré par `pandas`, afin de ne pas saturer le contexte du LLM.*