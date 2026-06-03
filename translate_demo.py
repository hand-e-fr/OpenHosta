#!/usr/bin/env python3
"""OpenHosta v5 — Stub de traduction FR → EN (binding @model)"""

import sys
sys.path.insert(0, "/home/ebatt/hand-e/hand-e-lab-2026/prototypes/OpenHosta-v5/src")

from openhosta import BackendModel

# 1. Configurer le backend
model = BackendModel(
    provider="openai_compatible",
    model_name="Qwen3.6-27B-AWQ-INT4",
    base_url="http://127.0.0.1:8000/v1",
    api_key="none",
)

# 2. Déclarer le stub avec binding automatique au backend
@model(tags=["lang"])
def traduire_fr_en(texte: str) -> str:
    """Traduit le texte du français vers l'anglais en préservant le sens et le ton."""
    ...

# 3. Appeler le stub directement — le backend est déjà injecté
print("=" * 60)
print("OpenHosta V5 — Stub de traduction FR → EN")
print("=" * 60)

phrases = [
    "Bonjour, Comment allez-vous aujourd'hui ?",
    "Le chat est sur le toit et il fait très froid.",
    "Je voudrais réserver une table pour deux ce soir.",
]

for phrase in phrases:
    result = traduire_fr_en(texte=phrase)
    print(f"\n🇫🇷  FR : {phrase}")
    print(f"🇬🇧  EN : {result}")

print("\n" + "=" * 60)
print("✅  Test terminé")
print("=" * 60)
