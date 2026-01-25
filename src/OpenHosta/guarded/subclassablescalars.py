# src/OpenHosta/semantics/scalars.py
import re

from typing import Any, Tuple, Optional

from .primitives import GuardedPrimitive, UncertaintyLevel, Tolerance

"""
Un semantic scaler dérive directement d'un GuardedPrimitive.

"""

class GuardedInt(GuardedPrimitive, int):
    """
    Entier sémantique.
    Accepte : 42, "42", "quarante-deux", "42.0" (si entier), "1 000".
    """    
    # --- 1. CONFIGURATION LLM ---
    _type_en = "an integer number (whole number)"
    _type_py = int
    _type_json = {"type": "integer"}

    # --- 2. VALIDATION NATIVE ---
    @classmethod
    def _parse_native(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        # Cas : Déjà un int (mais pas un bool, car True est un int en Python)
        if isinstance(value, int) and not isinstance(value, bool):
            return UncertaintyLevel(Tolerance.STRICT), value, None
            
        # Cas : String numérique propre "123"
        if isinstance(value, str) and value.isnumeric():
            return UncertaintyLevel(Tolerance.STRICT), int(value), None
             
        # Cas : Float rond (42.0) -> Accepté comme int
        if isinstance(value, float) and value.is_integer():
            return UncertaintyLevel(Tolerance.STRICT), int(value), None
            
        return UncertaintyLevel(Tolerance.ANYTHING), value, None

    # --- 3. NETTOYAGE HEURISTIQUE ---
    @classmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        if isinstance(value, bool):
            return UncertaintyLevel(Tolerance.FLEXIBLE), int(value), None
        value = str(value)
            
        # Nettoyage : espaces, et devises courantes
        value = value.strip().replace(" ", "")
        
        # Gestion des séparateurs de milliers (ex: 1,000 -> 1000)
        # On enlève les virgules si la chaîne contient uniquement des chiffres et des virgules
        if "," in value and "." not in value:
             value = value.replace(",", "")

        # Gestion des nombres négatifs et validation finale
        # Regex: Optionnel '-', suivi de chiffres
        if re.fullmatch(r'-?\d+', value):
            return UncertaintyLevel(Tolerance.FLEXIBLE), int(value), None
            
        return UncertaintyLevel(Tolerance.ANYTHING), value, None        
        

class GuardedFloat(GuardedPrimitive, float):
    """
    Nombre flottant sémantique.
    Accepte : 3.14, "3,14", "Pi environ", "10k".
    """
    _type_en = "a floating point number"
    _type_py = float
    _type_json = {"type": "number"}

    @classmethod
    def _parse_native(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        if isinstance(value, float):
            return UncertaintyLevel(Tolerance.STRICT), float(value), None
        if isinstance(value, int) and not isinstance(value, bool):
            return UncertaintyLevel(Tolerance.STRICT), float(value), None


        # Cas string propre "3.14"
        if isinstance(value, str):
            try:
                return UncertaintyLevel(Tolerance.STRICT), float(value), None
            except ValueError:
                pass
            
        return UncertaintyLevel(Tolerance.ANYTHING), value, None

    @classmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        value = str(value)
            
        value = value.strip().replace(" ", "")
        
        # Standardisation : Remplacer ',' par '.' (Format européen)
        value = value.replace(",", ".")
        slices = value.split(".")
        if len(slices) > 2:
            value = ''.join(slices[:-1])+ "." + slices[-1]
        
        try:
            return UncertaintyLevel(Tolerance.FLEXIBLE), float(value), None
        except ValueError as e:
            return UncertaintyLevel(Tolerance.ANYTHING), value, str(e)

    
class GuardedUtf8(GuardedPrimitive, str):
    """
    Chaîne de caractères sémantique.
    C'est le type par défaut. Son heuristique est très permissive,
    mais le LLM est utile pour corriger l'encodage, traduire, ou résumer.
    """
    _type_en = "a string of text"
    _type_py = str
    _type_json = {"type": "string"}

    @classmethod
    def _parse_native(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:

        if isinstance(value, str):
            return UncertaintyLevel(Tolerance.STRICT), value, None
            
        return UncertaintyLevel(Tolerance.ANYTHING), value, None
    
    @classmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:

        if isinstance(value, bytes):
            try:
                return UncertaintyLevel(Tolerance.STRICT), value.decode("utf-8"), None
            except UnicodeDecodeError as e:
                return UncertaintyLevel(Tolerance.ANYTHING), value, f"{e}"
            
        return UncertaintyLevel(Tolerance.ANYTHING), value, f"Expected str or bytes, got {type(value)}"
    

# ==============================================================================
# TYPES AVANCÉS (Complex, Bytes, ...)
# ==============================================================================

class GuardedComplex(GuardedPrimitive, complex):
    """Nombre complexe sémantique."""
    _type_en = "a complex number (e.g., 1+2j)"
    _type_py = complex
    _type_json = {"type": "string", "pattern": r"^[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?([+-](\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?j)?$"}

    @classmethod
    def _parse_native(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        if isinstance(value, complex):
            return UncertaintyLevel(Tolerance.STRICT), value, None
        return UncertaintyLevel(Tolerance.ANYTHING), value, None
    
    @classmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        try:
            return UncertaintyLevel(Tolerance.TYPE_COMPLIANT), complex(value), None
        except (ValueError, TypeError) as e:
            return UncertaintyLevel(Tolerance.ANYTHING), value, str(e)


class GuardedBytes(GuardedPrimitive, bytes):
    """Séquence d'octets immuable sémantique."""
    _type_en = "a bytes object (e.g., b'data')"
    _type_py = bytes
    _type_json = {"type": "string", "contentEncoding": "base64"}

    @classmethod
    def _parse_native(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        if isinstance(value, bytes):
            return UncertaintyLevel(Tolerance.STRICT), value, None
        return UncertaintyLevel(Tolerance.ANYTHING), value, None
    
    @classmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        if isinstance(value, str):
            # Attempt to encode string to bytes
            try:
                return UncertaintyLevel(Tolerance.PRECISE), value.encode('utf-8'), None
            except UnicodeEncodeError as e:
                return UncertaintyLevel(Tolerance.ANYTHING), value, str(e)
        try:
            # Attempt direct conversion (e.g., from bytearray, int iterable)
            return UncertaintyLevel(Tolerance.TYPE_COMPLIANT), bytes(value), None
        except (ValueError, TypeError) as e:
            return UncertaintyLevel(Tolerance.ANYTHING), value, str(e)


class GuardedByteArray(GuardedPrimitive, bytearray):
    """ByteArray sémantique."""
    _type_en = "a mutable sequence of bytes"
    _type_py = bytearray
    _type_json = {"type": "string", "contentEncoding": "base64"}

    @classmethod
    def _parse_native(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        if isinstance(value, bytearray):
            return UncertaintyLevel(Tolerance.STRICT), value, None
        return UncertaintyLevel(Tolerance.ANYTHING), value, None
    
    @classmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        if isinstance(value, str):
            return UncertaintyLevel(Tolerance.PRECISE), bytearray(value, 'utf-8'), None
        try:
            return UncertaintyLevel(Tolerance.TYPE_COMPLIANT), bytearray(value), None
        except (ValueError, TypeError) as e:
            return UncertaintyLevel(Tolerance.ANYTHING), value, str(e)
