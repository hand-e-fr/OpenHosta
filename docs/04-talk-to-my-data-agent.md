---
id: DOC-DX-004
type: guide
status: approved
title: Talk to my Data Agent
---

# Talk to my Data Agent — Guide pas à pas

Ce guide explique comment créer un agent OpenHosta v5 capable de lire des fichiers CSV dans un dossier spécifique et d'y répondre en langage naturel.

Nous allons utiliser :
- `BackendModel` et `@model.infer(tags=...)` pour lier le modèle LLM aux stubs.
- `Workspace` pour gouverner l'accès au dossier CSV.
- `Agent` avec un corps virtuel : `@tool` pour lire les CSV, `@model.infer` pour répondre.

## Étape 1 : Installer les dépendances

OpenHosta est le runtime. Pour lire des CSV, nous utiliserons le module `csv` standard.

```bash
pip install openhosta
```

## Étape 2 : Configurer le Backend et le Workspace

```python
from pathlib import Path
from openhosta import Agent, BackendModel, Workspace

# 1. Le backend (votre LLM local ou distant)
model = BackendModel(
    provider="openai_compatible",
    model_name="Qwen3.6-27B-AWQ-INT4",
    base_url="http://127.0.0.1:8000/v1",
    api_key="none"
)

# 2. Le Workspace (le dossier contenant vos CSV)
# Remplacez "/chemin/vers/mon/dossier_csv" par votre dossier réel
data_folder = Path("/chemin/vers/mon/dossier_csv")
workspace = Workspace(root=data_folder)
```

## Étape 3 : Définir l'Agent et son corps virtuel

L'agent aura deux capacités intégrées :
1. Un `@tool` déterministe pour lister et lire le contenu d'un fichier CSV.
2. Un `@model.infer` lié au backend pour analyser les données et répondre aux questions.

```python
import csv
import io

# @model.compile() attache le backend à la classe
@model.compile()
class DataAgent(Agent):
    """Agent spécialisé dans l'analyse de fichiers CSV situés dans le workspace.

    Il lit les données de manière sécurisée et répond aux questions en langage naturel.
    """

    # Capacité déterministe : lecture de fichier
    @tool(tags=["data", "read", "csv"])
    def read_csv_file(self, filename: str) -> str:
        """Lit un fichier CSV spécifique et retourne son contenu structuré.

        Args:
            filename: Le nom du fichier CSV présent dans le workspace.
        """
        raw = self.workspace.read(filename)
        # Retourner le texte brut pour que le LLM l'analyse
        return raw

    # Capacité LLM : inférence liée au backend
    @model.infer(tags=["data", "analysis", "q&a"])
    def answer_data_question(self, question: str, csv_content: str | None = None) -> str:
        """Répond à une question basée sur le contenu d'un fichier CSV.

        Args:
            question: La question de l'utilisateur en langage naturel.
            csv_content: Le contenu brut du CSV (si déjà lu).
        """
        ...  # stub → inférence via `model`
```

## Étape 4 : Lancer l'agent et poser des questions

```python
def main():
    # Initialisation de l'agent
    agent = DataAgent(workspace=workspace)

    # Ouverture d'une session (recrutement)
    agent.recruit(quota=16000)

    # L'agent dispatche automatiquement via son registre privé :
    # 1. Router → route:data (si un @router est défini)
    # 2. Infer → answer_data_question (via model.infer)
    result = agent.get("Quelles sont les ventes totales par région dans 'sales_2023.csv' ?")
    print(result)

    # Clôture propre de la session
    agent.free()

if __name__ == "__main__":
    main()
```

## Comment ça marche ?

1. **`Workspace`** : Garantit que l'agent ne peut lire que les fichiers présents dans `data_folder`. Il n'a aucun accès au reste du système de fichiers.
2. **`@tool read_csv_file`** : Capacité déterministe intégrée au corps virtuel de l'agent. Appelée directement par le dispatcher.
3. **`@model.infer answer_data_question`** : Stub lié au backend. Le dispatcher injecte le backend automatiquement via `Agent.get()`.
4. **`agent.get()`** : Surface conversationnelle. Elle dispatche automatiquement selon la priorité : Router → Planner → Playbook → Infer → Tool.
5. **Registre isolé** : L'agent construit son propre `CapabilityRegistration` à partir de ses méthodes de classe. Chaque instance d'agent est isolée.

> 💡 *Astuce : Pour des fichiers très volumineux, adaptez `read_csv_file` pour retourner uniquement les 50 premières lignes ou un résumé statistique, afin de ne pas saturer le contexte du LLM.*
