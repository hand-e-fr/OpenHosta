#!/usr/bin/env python3
"""OpenHosta v5 — Agent avec capacités intégrées (corps virtuel)"""

import sys
sys.path.insert(0, "/home/ebatt/hand-e/hand-e-lab-2026/prototypes/OpenHosta-v5/src")

from openhosta import Agent, BackendModel, tool, router

# 1. Backend
model = BackendModel(
    provider="openai_compatible",
    model_name="Qwen3.6-27B-AWQ-INT4",
    base_url="http://127.0.0.1:8000/v1",
    api_key="none",
)

# 2. Définition de l'Agent et de son corps virtuel
@model.compile()
class AssistantAgent(Agent):
    """Assistant capable de traduire, calculer et router ses propres requêtes."""

    # --- Capacité LLM (Stub) ---
    @model.infer(tags=["lang"])
    def traduire(self, texte: str) -> str:
        """Traduit le texte du français vers l'anglais."""
        ...

    # --- Capacité déterministe (Tool) ---
    @tool(tags=["math"])
    def additionner(self, chiffres: str) -> str:
        """Additionne tous les nombres trouvés dans le message."""
        import re
        nums = re.findall(r"\d+", chiffres)
        return str(sum(int(n) for n in nums))

    # --- Capacité de routage (Router LLM) ---
    @router(tags=["dispatch"], priority=-10)
    def decide_route(self, msg: str) -> str:
        """Classe l'intention en 'route:lang' pour une traduction ou 'route:math' pour un calcul."""
        ...

# 3. Exécution
def main():
    agent = AssistantAgent()
    agent.recruit(quota=8192)
    print(f"🟢 Agent recruté (Statut: {agent.status})")
    print("=" * 60)

    print("\n👤: Traduis en anglais: 'Bonjour, comment allez-vous aujourd'hui ?'")
    res1 = agent.get("Traduis en anglais: 'Bonjour, comment allez-vous aujourd'hui ?'")
    print(f"🤖: {res1}")

    print("\n👤: Combien font 25 + 14 + 6 ?")
    res2 = agent.get("Combien font 25 + 14 + 6 ?")
    print(f"🤖: {res2}")

    agent.free()
    print(f"\n🔴 Agent clôturé (Statut: {agent.status})")

if __name__ == "__main__":
    main()
