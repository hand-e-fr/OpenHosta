#!/usr/bin/env python3
"""OpenHosta v5 — Exemples progressifs avec @model.infer"""

import sys
sys.path.insert(0, "/home/ebatt/hand-e/hand-e-lab-2026/prototypes/OpenHosta-v5/src")

from openhosta import BackendModel

# 1. Backend commun
model = BackendModel(
    provider="openai_compatible",
    model_name="Qwen3.6-27B-AWQ-INT4",
    base_url="http://127.0.0.1:8000/v1",
    api_key="none",
)

# 2. Stub de traduction
@model.infer(tags=["lang"])
def traduire_fr_en(texte: str) -> str:
    """Traduit le texte du français vers l'anglais en préservant le sens et le ton."""
    ...

# 3. Stub de résumé
@model.infer(tags=["nlp", "summarize"])
def resume_texte(texte: str) -> str:
    """Résume le texte en une phrase concise."""
    ...

# 4. Stub d'extraction d'entités
@model.infer(tags=["nlp", "extraction"])
def extraire_entites(texte: str) -> list[str]:
    """Extrait les noms propres, lieux et organisations mentionnés."""
    ...

# 5. Exécution
print("=" * 60)
print("OpenHosta V5 — Exemples avec @model.infer")
print("=" * 60)

# Traduction
print("\n--- Traduction FR→EN ---")
phrases = [
    "Bonjour, Comment allez-vous aujourd'hui ?",
    "Le chat est sur le toit et il fait très froid.",
    "Je voudrais réserver une table pour deux ce soir.",
]
for phrase in phrases:
    result = traduire_fr_en(texte=phrase)
    print(f"🇫🇷 {phrase} → 🇬🇧 {result}")

# Résumé
print("\n--- Résumé ---")
texte_long = (
    "Intelligence artificielle, apprentissage automatique et traitement du langage naturel "
    "transforment radicalement le monde technologique. Les modèles de langage de grande taille "
    "permettent de comprendre, générer et traduire le texte avec une précision remarquable."
)
resume = resume_texte(texte=texte_long)
print(f"📄 Résumé : {resume}")

# Extraction
print("\n--- Extraction d'entités ---")
entites = extraire_entites(texte=texte_long)
print(f"🔍 Entités : {entites}")

print("\n" + "=" * 60)
print("✅ Tous les stubs fonctionnent avec @model.infer")
print("=" * 60)
