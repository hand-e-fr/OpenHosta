# ==============================================================================
# TYPES QUI NE PEUVENT PAS ÊTRE SUBCLASSES EN PYTHON (bool, Range, etc.)
# ==============================================================================

from typing import Any, Tuple
from types import NoneType

from .primitives import GuardedPrimitive, UncertaintyLevel, Tolerance, SubclassableWithProxy

class GuardedNone(GuardedPrimitive, SubclassableWithProxy):
    _type_en = "none value"
    _type_py = NoneType
    _type_json = {"type": "null"}
    _type_knowledge = {
        "NATURAL": ["null", "nothing", "rien", "aucun", "aucune"],
        "PROG": ["undefined", "empty", "null"]
    }
    
    @classmethod
    def _parse_native(cls, value: Any) -> Tuple[float, Any]:
        if value is None:
            return UncertaintyLevel(Tolerance.STRICT), None

        return UncertaintyLevel(Tolerance.ANYTHING), value
        
    @classmethod
    def _parse_heuristic(cls, value):
        value = str(value)
        
        value = value.strip(" \n\"\'")
        if value == 'None':
            return UncertaintyLevel(Tolerance.PRECISE), None
        
        value = value.lower()
        if value == "none":
            return UncertaintyLevel(Tolerance.FLEXIBLE), None
        
        if value in cls._type_knowledge["PROG"]:
            return UncertaintyLevel(Tolerance.CREATIVE), None
        
        return UncertaintyLevel(Tolerance.ANYTHING), value

    @classmethod
    def _parse_semantic(cls, value: Any) -> Tuple[float, Any]:

        if value is None:
            return UncertaintyLevel(Tolerance.STRICT), None
            
        value = str(value).strip().lower()
        if value in cls._type_knowledge["NATURAL"]:
            return UncertaintyLevel(Tolerance.CREATIVE), None
                
        return UncertaintyLevel(Tolerance.ANYTHING), value


class GuardedAny(GuardedPrimitive, SubclassableWithProxy):
    """
    Do not check the type of the value as it can be anything.
    """
    _type_en = "anything"
    _type_py = str
    _type_json = {"type": "string"}
    _tolerance = Tolerance.TYPE_COMPLIANT
    
    @classmethod
    def _parse_native(cls, value: Any) -> Tuple[float, Any]:
        return UncertaintyLevel(Tolerance.STRICT), value

class GuardedBool(GuardedPrimitive, SubclassableWithProxy):

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
    def _parse_native(cls, value: Any) -> Tuple[float, Any]:
        if isinstance(value, bool):
            # En interne on stocke 1 ou 0
            return UncertaintyLevel(Tolerance.STRICT), value

        return UncertaintyLevel(Tolerance.ANYTHING), value

    @classmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[float, Any]:

        if isinstance(value, (int, float, bool)):
            return UncertaintyLevel(Tolerance.STRICT), bool(value)
            
        if isinstance(value, str):
            v = value.strip().lower()
            if v in cls._type_knowledge[True]:
                return UncertaintyLevel(Tolerance.STRICT), True
            if v in  cls._type_knowledge[False]:
                return UncertaintyLevel(Tolerance.STRICT), False
                
        return UncertaintyLevel(0.5), False
        
class GuardedMemoryView(GuardedPrimitive, SubclassableWithProxy):
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


class GuardedRange(GuardedPrimitive, SubclassableWithProxy): 
    # Attention: range n'est pas subclassable facilement comme int ou str.
    # On hérite de GuardedPrimitive mais on ne peut pas hériter de 'range'.
    # On va simuler le comportement ou retourner un objet range natif via __new__.
    
    _type_en = "a range object (start, stop, step)"
    _type_py = range
    _type_json = {"type": "string", "pattern": "^range\\(\\d+(, \\d+)*\\)$"}

    # TODO: Implémenter les parseurs 
    pass

