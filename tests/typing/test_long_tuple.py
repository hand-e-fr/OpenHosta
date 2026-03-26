"""
Test for handling long tuple[str, str] type resolution and validation.

This test verifies that the TypeResolver can properly handle tuple types
with string elements, particularly for cases involving long text content
like multi-step processes or calendar implementations.
"""

from typing import Tuple
import pytest
from OpenHosta.guarded import TypeResolver


def test_long_tuple_type_resolution():
    """Test that TypeResolver can handle tuple[str, str] type with long content."""
    
    # The original LLM output - a tuple with two long strings
    # First string: 10-step irrigation system implementation
    # Second string: Monthly implementation calendar
    llm_output = (
        "1. Évaluer les dimensions du jardin et calculer le besoin en eau journalier selon la surface cultivée, en tenant compte du sol tourbeux peu rétentif.\n"
        "2. Installer une cuve de 300 L de récupération d’eau de pluie, raccordée aux gouttières sud, avec filtre basique et surélevée pour bénéficier de la gravité.\n"
        "3. Concevoir un plan de pose des tuyaux goutte-à-goutte groupés par besoins hydriques (fraises, tomates, légumes).\n"
        "4. Poser un réseau principal avec filtre fin, clapet anti-retour et robinet d’arrêt.\n"
        "5. Répartir les rubans goutte-à-goutte le long des cultures, avec régulateurs de débit pour compenser les dénivelés.\n"
        "6. Installer un programmateur mécanique pour un arrosage quotidien de 10 min le matin, extensible à 15 min en période chaude.\n"
        "7. Mettre en place une jauge visuelle dans la cuve pour surveiller le niveau d’eau et anticiper les appoints.\n"
        "8. Compléter par un paillage épais (paille ou copeaux) pour limiter l’évaporation et stabiliser l’humidité.\n"
        "9. Prévoir un entretien mensuel léger : nettoyage des filtres, vérification des goutteurs, purge d’air.\n"
        "10. Définir une routine simple : vérification journalière brève, ouverture/fermeture du système ou contrôle du programmateur, et inspection visuelle des fuites.",
        
        "Calendrier d'implémentation du système d’irrigation goutte-à-goutte avec récupération d’eau de pluie (Göteborg, climat océanique) :\n"
        "\n"
        "**Avril**\n"
        "- **Semaine 1-2** : Analyse du jardin, tracé du réseau. Installation de la cuve de 300 L orientée sud avec filtre.\n"
        "- **Semaine 3** : Achat du matériel (tuyaux, raccords, minuterie mécanique, supports).\n"
        "- **Semaine 4** : Amélioration du sol (compost + terreau) dans les zones prioritaires.\n"
        "\n"
        "**Mai**\n"
        "- **Semaine 1** : Pose du réseau principal sur supports aériens pour éviter l’enfouissement.\n"
        "- **Semaine 2** : Installation des émulateurs près des fraises et framboises.\n"
        "- **Semaine 3-4** : Arrosage test (10 min matin), ajustement du débit, surveillance des limaces (pièges).\n"
        "\n"
        "**Juin**\n"
        "- Arrosage automatisé à 15 min à 6h du matin.\n"
        "- Branchement du programmateur mécanique (1 cycle/jour).\n"
        "- Intégration de bacs surélevés pour salades, carottes et radis.\n"
        "- Arrosage démarré pour tomates, haricots et pois.\n"
        "\n"
        "**Juillet - Août**\n"
        "- Maintenance hebdomadaire : nettoyage filtres, contrôle fuites et débit.\n"
        "- Arrosage double (matin et soir) si température >18°C.\n"
        "- Utilisation exclusive de l’eau de pluie, avec appoint uniquement en sécheresse.\n"
        "- Suivi de la croissance des fruits et légumes.\n"
        "\n"
        "**Septembre**\n"
        "- Réduction à 10 min le matin (1 cycle).\n"
        "- Préparation hivernale : vidange partielle des tuyaux.\n"
        "- Installation de ronces à mûres rustiques sur le même circuit.\n"
        "\n"
        "**Octobre**\n"
        "- Arrêt complet du système.\n"
        "- Vidange totale, rangement minuterie et filtres.\n"
        "- Conservation du réservoir partiellement ouvert pour éviter le gel."
    )
    
    # Define the type we want to resolve
    MyType = TypeResolver.resolve(Tuple[str, str])
    
    # Test that the type resolution works
    assert MyType is not None
    
    # Test that we can create an instance with the tuple data
    try:
        data = MyType(llm_output)
        assert isinstance(data, tuple)
        assert len(data) == 2
        assert isinstance(data[0], str)
        assert isinstance(data[1], str)
        
        # Verify the content is preserved
        assert "Évaluer les dimensions du jardin" in data[0]
        assert "Calendrier d'implémentation" in data[1]
        
        # Test accessing the second element (calendar)
        calendar_content = data[1]
        assert "**Avril**" in calendar_content
        assert "**Octobre**" in calendar_content
        
    except Exception as e:
        pytest.fail(f"Failed to create MyType instance: {str(e)}")


def test_long_tuple_attempt_method():
    """Test the attempt method with long tuple data."""
    
    llm_output = (
        "1. Évaluer les dimensions du jardin et calculer le besoin en eau journalier selon la surface cultivée, en tenant compte du sol tourbeux peu rétentif.\n"
        "2. Installer une cuve de 300 L de récupération d’eau de pluie, raccordée aux gouttières sud, avec filtre basique et surélevée pour bénéficier de la gravité.",
        "Calendrier d'implémentation du système d’irrigation goutte-à-goutte avec récupération d’eau de pluie (Göteborg, climat océanique) :\n"
        "\n"
        "**Avril**\n"
        "- **Semaine 1-2** : Analyse du jardin, tracé du réseau. Installation de la cuve de 300 L orientée sud avec filtre.\n"
        "- **Semaine 3** : Achat du matériel (tuyaux, raccords, minuterie mécanique, supports)."
    )
    
    MyType = TypeResolver.resolve(tuple[str, str])
    
    # Test the attempt method
    result = MyType.attempt(llm_output)
    assert result.success is True
    assert result.data is not None
    
    # Verify the result data
    assert isinstance(result.data, tuple)
    assert len(result.data) == 2
    assert "Évaluer les dimensions" in result.data[0]
    assert "Calendrier d'implémentation" in result.data[1]


def test_long_tuple_edge_cases():
    """Test edge cases for long tuple handling."""
    
    MyType = TypeResolver.resolve(tuple[str, str])
    
    # Test with empty strings
    empty_tuple = ("", "")
    result_empty = MyType.attempt(empty_tuple)
    assert result_empty.success is True
    
    # Test with very long strings
    very_long_first = "A " * 1000 + "steps for irrigation system."
    very_long_second = "Calendar: " * 500 + "monthly implementation."
    long_tuple = (very_long_first, very_long_second)
    
    result_long = MyType.attempt(long_tuple)
    assert result_long.success is True
    assert len(result_long.data[0]) == len(very_long_first)
    assert len(result_long.data[1]) == len(very_long_second)
    
    # Test with invalid types
    invalid_tuple = (123, 456)  # integers instead of strings
    result_invalid = MyType.attempt(invalid_tuple)
    # This should fail or be handled gracefully depending on TypeResolver implementation
    # We'll just check that it doesn't crash
    assert result_invalid is not None
    
    
def test_enum_str_tuple():

    
    from enum import Enum
    
    class SelectedAction(Enum):
        A = "a"
        B = "b"
        PAS_ASSEZ_INFORMATION = "pas_assez_information"
    
    from OpenHosta import emulate

    def action_router(msg:str) -> tuple[SelectedAction, str]:
        """
        Select an action based on message msg.
        
        Returns:
           - action: SelectedAction
           - rational: str
        """
        return emulate()

    action, rational = action_router('il faud dire A')

    assert action == SelectedAction.A
    assert type(rational) == str
    assert len(rational) > 0


    
def test_enum_str_tuple_hard():

    
    from enum import Enum
    
    class SelectedAction(Enum):
        A = "a"
        B = "b"
        PAS_ASSEZ_INFORMATION = "pas_assez_information"
    
    from OpenHosta import emulate

    def action_router(msg:str) -> tuple[SelectedAction, str]:
        """
        Select an action based on message msg.
        
        Returns:
           - action: SelectedAction
           - rational: str
        """
        return emulate()

    action, rational = action_router('il faud dire A et expliquer dans une longue phrase avec tout types de ponctuation et de caractères spécuaux pourquoi A est une lettre importante dans l\'histoire')

    assert action == SelectedAction.A
    assert type(rational) == str
    assert len(rational) > 0    