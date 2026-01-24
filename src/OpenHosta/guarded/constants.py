# src/OpenHosta/semantics/constants.py

class Tolerance:
    """
    Définit le niveau de "flou" accepté lors des comparaisons sémantiques.
    
    Ces constantes pilotent le choix de la stratégie interne :
    - < 0.05 : Stratégie Hybride (Vecteurs + Vérification LLM/Logprobs) -> Plus lent, très précis.
    - >= 0.05 : Stratégie Vectorielle pure (Embeddings) -> Très rapide, approximation thématique.
    """

    # --- 1. IDENTITÉ STRICTE (Le "Paranoïaque") ---
    # Usage : Mots de passe, IDs, Codes, égalité logique pure.
    # Comportement : Rejette tout ce qui n'est pas strictement identique ou synonyme parfait.
    # Coût : Élevé (Vérification LLM souvent requise).
    STRICT: float = 0.0

    # --- 2. PRÉCISION SÉMANTIQUE (Le "Rigoureux") ---
    # Usage : Commandes CLI ("git push" == "push git"), Formulaires, Validation de données.
    # Comportement : Accepte les variations grammaticales, les fautes de frappe légères.
    # Rejette : Les généralisations abusives (Un chien n'est pas un loup).
    PRECISE: float = 0.05

    # --- 3. COMPRÉHENSION NATURELLE (Le "Standard") ---
    # Usage : Chatbots, Routage d'intention, Recherche documentaire.
    # Comportement : Idéal pour comprendre l'intention humaine.
    # Accepte : "Voiture" == "Automobile", "Pas cher" == "Économique".
    # Coût : Faible (Vectoriel pur).
    FLEXIBLE: float = 0.15

    # --- 4. ASSOCIATION D'IDÉES (Le "Créatif") ---
    # Usage : Brainstorming, Recommandation, Exploration.
    # Comportement : Accepte les liens thématiques larges.
    # Accepte : "Plage" == "Vacances", "Pizza" == "Italie".
    CREATIVE: float = 0.30

    # --- 5. TOLÉRANCE MAXIMALE (Le "Chaos" dans le respect du type python) ---
    # Usage : Génération libre, Exploration aléatoire.
    # Accepte : Tout sauf les types impossibles (ex: dict("44") est impossible).
    TYPE_COMPLIANT: float = 1.0 - 1e-15

    # --- 6. ERREUR DE TYPE (Le "Chaos" absolu) ---
    ANYTHING: float = 1.0
    
    @staticmethod
    def describe(value: float) -> str:
        """Retourne une description textuelle pour le debug."""
        if value <= Tolerance.STRICT: return "STRICT (Identité)"
        if value <= Tolerance.PRECISE: return "PRECISE (Logique)"
        if value <= Tolerance.FLEXIBLE: return "FLEXIBLE (Intention)"
        if value <= Tolerance.CREATIVE: return "CREATIVE (Thématique)"
        if value == Tolerance.ANYTHING: return "ANYTHING (Chaos)"

        return "TYPE_COMPLIANT (Tout tant que le type est respecté)"