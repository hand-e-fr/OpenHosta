# L'idée est de réaliser la grande table des modèles lors de l'execution d'un test auto.
# Cette grande table sert a choisi le paramètre par défaut pour les capababilities des modèles en fonctions de leur nom (fuzzy match)
# Elle sert aussi a classer les modèles par compétences et à les afficher dans le dashboard.

# Le middleware permet de :
# Efficient:
# - réduction des couts par la mise en compétition des fournisseurs : changer de fournisseur sans changer le code
# - pérenité des applications : en encourageant les bonnes pratiques issues de 50 ans de dveloppement de logiciels 
# - optimiser la latence et la consomation d'énergie : en selectionnant automatiquement le modèle le plus adapté à la tâche
# Safe:
# - gouverner l'envoie de data par partenaires IA-API en fonctions de leur habilitation
# - piloter l'incertitude des réponses
# - traiter les obligations légales associés à l'utilisation de l'IA (RIA)


from OpenHosta.models import ModelCapabilities
def safe(
    require_capabilities={ModelCapabilities.DATA_SECURITY, ModelCapabilities.HIGH_AVAILABILITY, ModelCapabilities.RGPD_BY_DESIGN},
    max_uncertainty=0.3, log_conversation=True):
    pass

