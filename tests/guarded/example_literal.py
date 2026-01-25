"""
Exemple complet de GuardedLiteral - Validation stricte de valeurs littérales

GuardedLiteral permet de créer des types qui n'acceptent qu'un ensemble
fixe de valeurs connues à l'avance. C'est l'équivalent de typing.Literal
mais avec le pipeline de validation guarded.
"""

from typing import Literal
from OpenHosta.guarded import guarded_literal
from OpenHosta.guarded.resolver import TypeResolver
from OpenHosta.guarded.constants import Tolerance


# ==============================================================================
# EXEMPLE 1 : Validation de statuts (strings)
# ==============================================================================

print("=" * 70)
print("EXEMPLE 1 : Statuts de commande")
print("=" * 70)

# Créer un type pour les statuts de commande
OrderStatus = guarded_literal("pending", "processing", "shipped", "delivered")

# ✅ Valeurs valides
status1 = OrderStatus("pending")
print(f"Status 1: {status1} - uncertainty: {status1.uncertainty}")
# → pending - uncertainty: 0.0 (STRICT)

# ✅ Case-insensitive (niveau HEURISTIC)
status2 = OrderStatus("PENDING")
print(f"Status 2: {status2} - uncertainty: {status2.uncertainty}")
# → pending - uncertainty: 0.05 (PRECISE)

# ✅ Avec espaces (niveau HEURISTIC)
status3 = OrderStatus("  shipped  ")
print(f"Status 3: {status3} - uncertainty: {status3.uncertainty}")
# → shipped - uncertainty: 0.05 (PRECISE)

# ❌ Valeur invalide
try:
    invalid_status = OrderStatus("cancelled")  # Pas dans la liste
except ValueError as e:
    print(f"❌ Erreur attendue: {e}")

print()


# ==============================================================================
# EXEMPLE 2 : Via TypeResolver et typing.Literal
# ==============================================================================

print("=" * 70)
print("EXEMPLE 2 : Via TypeResolver (comme dans une fonction)")
print("=" * 70)

# Utilisation avec typing.Literal (comme dans les annotations de fonction)
PriorityType = TypeResolver.resolve(Literal["low", "medium", "high"])

priority = PriorityType("high")
print(f"Priority: {priority} - uncertainty: {priority.uncertainty}")
# → high - uncertainty: 0.0

# Case-insensitive
priority2 = PriorityType("HIGH")
print(f"Priority 2: {priority2} - uncertainty: {priority2.uncertainty}")
# → high - uncertainty: 0.05

print()


# ==============================================================================
# EXEMPLE 3 : Literal avec des nombres
# ==============================================================================

print("=" * 70)
print("EXEMPLE 3 : Niveaux de priorité (entiers)")
print("=" * 70)

# Créer un type pour les niveaux de priorité (1, 2, 3)
PriorityLevel = guarded_literal(1, 2, 3)

level1 = PriorityLevel(2)
print(f"Level 1: {level1} - type: {type(level1).__name__}")
# → 2 - type: Literal[1, 2, 3]

# ✅ Conversion depuis string (niveau HEURISTIC)
level2 = PriorityLevel("3")
print(f"Level 2: {level2} - uncertainty: {level2.uncertainty}")
# → 3 - uncertainty: 0.05

# ❌ Valeur invalide
try:
    invalid_level = PriorityLevel(5)
except ValueError as e:
    print(f"❌ Erreur: Valeur doit être 1, 2 ou 3")

print()


# ==============================================================================
# EXEMPLE 4 : Cas d'usage réel - Configuration d'environnement
# ==============================================================================

print("=" * 70)
print("EXEMPLE 4 : Configuration d'environnement")
print("=" * 70)

from dataclasses import dataclass
from OpenHosta.guarded import guarded_dataclass

# Définir les types littéraux
Environment = guarded_literal("development", "staging", "production")
LogLevel = guarded_literal("debug", "info", "warning", "error")

@guarded_dataclass
class AppConfig:
    """Configuration de l'application avec validation stricte."""
    env: Environment  # Type annoté avec GuardedLiteral
    log_level: LogLevel
    debug: bool

# ✅ Configuration valide
config = AppConfig({
    "env": "production",
    "log_level": "error",
    "debug": "false"
})

print(f"Environment: {config.env}")
print(f"Log Level: {config.log_level}")
print(f"Debug: {config.debug}")
print(f"Env uncertainty: {config.env.uncertainty}")

# ✅ Parsing flexible
config2 = AppConfig({
    "env": "STAGING",  # Case-insensitive
    "log_level": "  INFO  ",  # Avec espaces
    "debug": "yes"
})

print(f"\nConfig 2 - Env: {config2.env} (uncertainty: {config2.env.uncertainty})")

# ❌ Valeur invalide
try:
    invalid_config = AppConfig({
        "env": "testing",  # Pas dans les valeurs autorisées
        "log_level": "info",
        "debug": "false"
    })
except ValueError as e:
    print(f"\n❌ Configuration invalide détectée!")

print()


# ==============================================================================
# EXEMPLE 5 : Comparaison avec enum
# ==============================================================================

print("=" * 70)
print("EXEMPLE 5 : GuardedLiteral vs GuardedEnum")
print("=" * 70)

from OpenHosta.guarded import GuardedEnum

# GuardedEnum : Pour des valeurs avec nom et valeur
class StatusEnum(GuardedEnum):
    PENDING = "pending"
    ACTIVE = "active"
    DONE = "done"

# GuardedLiteral : Pour des valeurs simples sans nom
StatusLiteral = guarded_literal("pending", "active", "done")

# Les deux fonctionnent, mais GuardedEnum a .name et .value
enum_status = StatusEnum("active")
print(f"Enum - name: {enum_status.name}, value: {enum_status.value}")
# → name: ACTIVE, value: active

literal_status = StatusLiteral("active")
print(f"Literal - value: {literal_status}")
# → value: active

print("\n📝 Quand utiliser quoi ?")
print("  - GuardedEnum : Quand vous avez besoin de .name et .value séparés")
print("  - GuardedLiteral : Pour des valeurs simples, plus léger")

print()


# ==============================================================================
# EXEMPLE 6 : Métadonnées et niveaux de confiance
# ==============================================================================

print("=" * 70)
print("EXEMPLE 6 : Métadonnées et décisions basées sur la confiance")
print("=" * 70)

Color = guarded_literal("red", "green", "blue")

# Valeur exacte → STRICT (0.0)
color1 = Color("red")
print(f"Exact match: {color1} - uncertainty: {color1.uncertainty}")

# Case-insensitive → PRECISE (0.05)
color2 = Color("RED")
print(f"Case-insensitive: {color2} - uncertainty: {color2.uncertainty}")

# Décision basée sur la confiance
def process_color(color_input: str):
    """Traite une couleur avec validation."""
    color = Color(color_input)
    
    if color.uncertainty <= Tolerance.STRICT:
        return f"✅ Couleur validée automatiquement: {color}"
    elif color.uncertainty <= Tolerance.PRECISE:
        return f"⚠️  Couleur acceptée après nettoyage: {color}"
    else:
        return f"❌ Couleur rejetée"

print(f"\n{process_color('blue')}")
print(f"{process_color('BLUE')}")

print()


# ==============================================================================
# RÉSUMÉ
# ==============================================================================

print("=" * 70)
print("RÉSUMÉ : GuardedLiteral")
print("=" * 70)
print("""
✅ Avantages :
  - Validation stricte d'un ensemble fixe de valeurs
  - Parsing flexible (case-insensitive, espaces, conversion de types)
  - Métadonnées de confiance (uncertainty)
  - Compatible avec typing.Literal via TypeResolver
  - Fonctionne avec strings, int, float

🎯 Cas d'usage :
  - Statuts de commande/workflow
  - Environnements (dev, staging, prod)
  - Niveaux de log
  - Priorités
  - Tout ensemble fini de valeurs connues

📊 Niveaux de parsing :
  - NATIVE (0.0) : Valeur exacte dans la liste
  - HEURISTIC (0.05) : Case-insensitive, espaces, conversion de type
  
🆚 vs GuardedEnum :
  - GuardedLiteral : Plus simple, pour valeurs simples
  - GuardedEnum : Plus riche, avec .name et .value séparés
""")
