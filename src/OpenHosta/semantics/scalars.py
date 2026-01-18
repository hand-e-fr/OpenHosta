# src/OpenHosta/semantics/scalars.py
import re
from typing import Any, Tuple
from .primitives import GuardedPrimitive

class SemanticInt(int, GuardedPrimitive):
    """
    Entier sémantique.
    Accepte : 42, "42", "quarante-deux", "42.0" (si entier), "1 000".
    """
    
    # --- 1. CONFIGURATION LLM ---
    _type_en = "an integer number (whole number)"
    _type_py = "int"
    _type_json = {"type": "integer"}

    # --- 2. VALIDATION NATIVE ---
    @classmethod
    def _parse_native(cls, value: Any) -> Tuple[bool, Any]:
        # Cas : Déjà un int (mais pas un bool, car True est un int en Python)
        if isinstance(value, int) and not isinstance(value, bool):
            return True, value
            
        # Cas : String numérique propre "123"
        if isinstance(value, str) and value.isnumeric():
             return True, int(value)
             
        # Cas : Float rond (42.0) -> Accepté comme int
        if isinstance(value, float) and value.is_integer():
            return True, int(value)
            
        return False, None

    # --- 3. NETTOYAGE HEURISTIQUE ---
    @classmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[bool, Any]:
        if not isinstance(value, str):
            return False, None
            
        # Nettoyage : espaces, et devises courantes
        cleaned = value.strip().replace(" ", "")
        cleaned = re.sub(r'[€$£USD]', '', cleaned, flags=re.IGNORECASE)
        
        # Gestion des séparateurs de milliers (ex: 1,000 -> 1000)
        # On enlève les virgules si la chaîne contient uniquement des chiffres et des virgules
        if "," in cleaned and "." not in cleaned:
             cleaned = cleaned.replace(",", "")

        # Gestion des nombres négatifs et validation finale
        # Regex: Optionnel '-', suivi de chiffres
        if re.fullmatch(r'-?\d+', cleaned):
            return True, int(cleaned)
            
        return False, None


class SemanticFloat(float, GuardedPrimitive):
    """
    Nombre flottant sémantique.
    Accepte : 3.14, "3,14", "Pi environ", "10k".
    """

    _type_en = "a floating point number"
    _type_py = "float"
    _type_json = {"type": "number"}

    @classmethod
    def _parse_native(cls, value: Any) -> Tuple[bool, Any]:
        if isinstance(value, float):
            return True, value
        if isinstance(value, int) and not isinstance(value, bool):
            return True, float(value)
        # Cas string propre "3.14"
        if isinstance(value, str):
            try:
                return True, float(value)
            except ValueError:
                pass
        return False, None

    @classmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[bool, Any]:
        if not isinstance(value, str):
            return False, None
            
        cleaned = value.strip().replace(" ", "")
        cleaned = re.sub(r'[€$£USD%]', '', cleaned, flags=re.IGNORECASE)
        
        # Standardisation : Remplacer ',' par '.' (Format européen)
        cleaned = cleaned.replace(",", ".")
        
        try:
            return True, float(cleaned)
        except ValueError:
            return False, None


class SemanticBool(int, GuardedPrimitive):
    """
    Booléen sémantique.
    Note : Hérite de int car bool n'est pas subclassable en Python.
    Accepte : True, "True", "Yes", "Oui", "Vrai", "1", "Active".
    """

    _type_en = "a boolean value (true or false)"
    _type_py = "bool"
    _type_json = {"type": "boolean"}

    def __new__(cls, value: Any, description: str = ""):
        # On force la valeur à 0 ou 1 pour respecter le comportement booléen
        instance = super().__new__(cls, value, description)
        if instance not in (0, 1):
             # Si le cast a renvoyé autre chose (ex: un int 42), on normalise
             instance = super().__new__(cls, 1) # Tout sauf 0 est True
        return instance

    def __repr__(self):
        return "True" if self == 1 else "False"

    def __str__(self):
        return "True" if self == 1 else "False"

    @classmethod
    def _parse_native(cls, value: Any) -> Tuple[bool, Any]:
        if isinstance(value, bool):
            # En interne on stocke 1 ou 0
            return True, 1 if value else 0
        return False, None

    @classmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[bool, Any]:
        if isinstance(value, (int, float)):
            if value == 1: return True, 1
            if value == 0: return True, 0
            
        if isinstance(value, str):
            v = value.strip().lower()
            if v in ("true", "yes", "y", "oui", "vrai", "on", "1"):
                return True, 1
            if v in ("false", "no", "n", "non", "faux", "off", "0"):
                return True, 0
                
        return False, None


class SemanticStr(str, GuardedPrimitive):
    """
    Chaîne de caractères sémantique.
    C'est le type par défaut. Son heuristique est très permissive,
    mais le LLM est utile pour corriger l'encodage, traduire, ou résumer.
    """

    _type_en = "a string of text"
    _type_py = "str"
    _type_json = {"type": "string"}

    @classmethod
    def _parse_native(cls, value: Any) -> Tuple[bool, Any]:
        if isinstance(value, str):
            return True, value
        return False, None

    @classmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[bool, Any]:
        # Heuristique simple : Convertir n'importe quoi en string
        # Sauf si c'est None
        if value is None:
            return False, None
        return True, str(value)