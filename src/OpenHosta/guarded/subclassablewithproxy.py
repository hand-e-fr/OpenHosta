# ==============================================================================
# TYPES QUI NE PEUVENT PAS ÊTRE SUBCLASSES EN PYTHON (bool, Range, etc.)
# ==============================================================================

from typing import Any, Tuple, Optional
from types import NoneType

from .primitives import GuardedPrimitive, UncertaintyLevel, Tolerance, ProxyWrapper

class GuardedNone(GuardedPrimitive, ProxyWrapper):
    _type_en = "none value"
    _type_py = NoneType
    _type_json = {"type": "null"}
    _type_knowledge = {
        "NATURAL": ["null", "nothing", "rien", "aucun", "aucune"],
        "PROG": ["undefined", "empty", "null"]
    }
    
    @classmethod
    def _parse_native(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        if value is None:
            return UncertaintyLevel(Tolerance.STRICT), None, None

        if value == 'None':
            # For union type, we accept 'None' as a valid value
            return UncertaintyLevel(Tolerance.STRICT), None, None

        return UncertaintyLevel(Tolerance.ANYTHING), value, None
        
    @classmethod
    def _parse_heuristic(cls, value) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        cleaned = cls._clean_llm_response(value)
        
        cleaned = cleaned.strip(" \"\'")
        if cleaned == 'None':
            return UncertaintyLevel(Tolerance.FLEXIBLE), None, None
        
        cleaned = cleaned.lower()
        if cleaned == "none":
            return UncertaintyLevel(Tolerance.FLEXIBLE), None, None
        
        if cleaned in cls._type_knowledge["PROG"]:
            return UncertaintyLevel(Tolerance.CREATIVE), None, None
        
        return UncertaintyLevel(Tolerance.ANYTHING), cleaned, None

    @classmethod
    def _parse_semantic(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:

        if value is None:
            return UncertaintyLevel(Tolerance.STRICT), None, None
            
        value = str(value).strip().lower()
        if value in cls._type_knowledge["NATURAL"]:
            return UncertaintyLevel(Tolerance.CREATIVE), None, None
                
        return UncertaintyLevel(Tolerance.ANYTHING), value, None


class GuardedAny(GuardedPrimitive, ProxyWrapper):
    """
    Do not check the type of the value as it can be anything.
    """
    _type_en = "anything"
    _type_py = str
    _type_json = {"type": "string"}
    _tolerance = Tolerance.TYPE_COMPLIANT
    
    @classmethod
    def _parse_native(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        # Basic heuristic inference for Any (smart Any)
        if isinstance(value, str):
            v_lower = value.strip().lower()
            if v_lower == 'none':
                return UncertaintyLevel(Tolerance.PRECISE), None, None
            if v_lower == 'true':
                return UncertaintyLevel(Tolerance.PRECISE), True, None
            if v_lower == 'false':
                return UncertaintyLevel(Tolerance.PRECISE), False, None
            
            # Try numbers
            try:
                if '.' in value:
                     return UncertaintyLevel(Tolerance.PRECISE), float(value), None
                return UncertaintyLevel(Tolerance.PRECISE), int(value), None
            except:
                pass

        return UncertaintyLevel(Tolerance.STRICT), value, None

class GuardedBool(GuardedPrimitive, ProxyWrapper):

    _type_en = "a boolean value (true or false)"
    _type_py = bool
    _type_json = {"type": "boolean"}
    _type_knowledge = {
        True: ["true", "yes", "oui", "vrai", "1", "active", "enabled"],
        False: ["false", "no", "non", "faux", "0", "inactive", "disabled"]
    }
            
    def __bool__(self):
        # Get value from GuardedPrimitive
        if type(self._python_value) is bool:
            return self._python_value
        else:
            return False
    
    @classmethod
    def _parse_native(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        if isinstance(value, bool):
            # En interne on stocke 1 ou 0
            return UncertaintyLevel(Tolerance.STRICT), value, None

        return UncertaintyLevel(Tolerance.ANYTHING), value, None

    @classmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:

        if isinstance(value, (int, float, bool)):
            return UncertaintyLevel(Tolerance.STRICT), bool(value), None
            
        if isinstance(value, str) or value is not None:
            v = cls._clean_llm_response(value).lower()
            if v in cls._type_knowledge[True]:
                return UncertaintyLevel(Tolerance.STRICT), True, None
            if v in  cls._type_knowledge[False]:
                return UncertaintyLevel(Tolerance.STRICT), False, None
                
        return UncertaintyLevel(0.5), False, None
        
class GuardedMemoryView(GuardedPrimitive, ProxyWrapper):
    """
    Vue mémoire.
    Nécessite un objet bytes ou bytearray sous-jacent.
    Note: memoryview n'est pas subclassable en Python, on retourne donc
    l'objet memoryview natif directement.
    """
    _type_en = "a memoryview of bytes"
    _type_py = memoryview
    _type_json = {"type": "string"}

    # TODO: Implémenter les parseurs 
    pass


class GuardedRange(GuardedPrimitive, ProxyWrapper): 
    # Attention: range n'est pas subclassable facilement comme int ou str.
    # On hérite de GuardedPrimitive mais on ne peut pas hériter de 'range'.
    # On va simuler le comportement ou retourner un objet range natif via __new__.
    
    _type_en = "a range object (start, stop, step)"
    _type_py = range
    _type_json = {"type": "string", "pattern": "^range\\(\\d+(, \\d+)*\\)$"}

    @classmethod
    def _parse_native(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        if isinstance(value, range):
            return UncertaintyLevel(Tolerance.STRICT), value, None
        return UncertaintyLevel(Tolerance.ANYTHING), value, None

    @classmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        if isinstance(value, str) or value is not None:
            cleaned = cls._clean_llm_response(value)
            # range(start, stop[, step])
            if cleaned.startswith("range(") and cleaned.endswith(")"):
                try:
                    content = cleaned[6:-1]
                    parts = [int(x.strip()) for x in content.split(",") if x.strip()]
                    return UncertaintyLevel(Tolerance.PRECISE), range(*parts), None
                except Exception:
                    pass
        
        return UncertaintyLevel(Tolerance.ANYTHING), value, "Invalid range format"

