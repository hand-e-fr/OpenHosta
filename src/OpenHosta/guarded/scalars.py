# src/OpenHosta/semantics/scalars.py
import re
import ast

from enum import Enum
from typing import Any, Tuple, Type
from types import NoneType

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
    def _parse_native(cls, value: Any) -> Tuple[float, Any]:
        # Cas : Déjà un int (mais pas un bool, car True est un int en Python)
        if isinstance(value, int) and not isinstance(value, bool):
            return 1.0, value
            
        # Cas : String numérique propre "123"
        if isinstance(value, str) and value.isnumeric():
             return 1.0, int(value)
             
        # Cas : Float rond (42.0) -> Accepté comme int
        if isinstance(value, float) and value.is_integer():
            return 1.0, int(value)
            
        return False, None

    # --- 3. NETTOYAGE HEURISTIQUE ---
    @classmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[float, Any]:
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
            return 1.0, int(cleaned)
            
        return False, None


class GuardedFloat(GuardedPrimitive, float):
    """
    Nombre flottant sémantique.
    Accepte : 3.14, "3,14", "Pi environ", "10k".
    """
    _type_en = "a floating point number"
    _type_py = float
    _type_json = {"type": "number"}

    @classmethod
    def _parse_native(cls, value: Any) -> Tuple[float, Any]:
        if isinstance(value, float):
            return 1.0, value
        if isinstance(value, int) and not isinstance(value, bool):
            return 1.0, float(value)
        # Cas string propre "3.14"
        if isinstance(value, str):
            try:
                return 1.0, float(value)
            except ValueError:
                pass
        return False, None

    @classmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[float, Any]:
        if not isinstance(value, str):
            return False, None
            
        cleaned = value.strip().replace(" ", "")
        cleaned = re.sub(r'[€$£USD%]', '', cleaned, flags=re.IGNORECASE)
        
        # Standardisation : Remplacer ',' par '.' (Format européen)
        cleaned = cleaned.replace(",", ".")
        
        try:
            return 1.0, float(cleaned)
        except ValueError:
            return False, None

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
    def _parse_native(cls, value: Any) -> Tuple[float, Any]:
        if isinstance(value, str):
            return 1.0, value
        return False, None

    @classmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[float, Any]:
        # Heuristique simple : Convertir n'importe quoi en string
        # Sauf si c'est None
        if value is None:
            return False, None
        return 1.0, str(value)
    

class GuardedSet(GuardedPrimitive, set):
    pass

class GuardedDict(GuardedPrimitive, dict):
    pass


# ==============================================================================
# 7. TYPES AVANCÉS (Complex, Bytes, ...)
# ==============================================================================

class GuardedComplex(GuardedPrimitive, complex):
    """
    Nombre complexe.
    Accepte : 1+2j, "1+2j", "(1+2j)".
    """
    _type_en = "a complex number (real + imaginary parts, e.g., 1+2j)"
    _type_py = "complex"
    _type_json = {"type": "string", "pattern": "^[\\d\\+\\-\\.j\\(\\)\\s]+$"}

    @classmethod
    def _parse_native(cls, value: Any) -> Tuple[float, Any]:
        if isinstance(value, complex):
            return 1.0, value
        return False, None

    @classmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[float, Any]:
        if isinstance(value, str):
            # Nettoyage
            v = value.strip().replace(" ", "")
            try:
                # complex("1+2j") fonctionne nativement en Python
                return 1.0, complex(v)
            except ValueError:
                pass
        return False, None


class GuardedBytes(GuardedPrimitive, bytes):
    """
    Séquence d'octets immuable.
    Accepte : b'hello', "b'hello'", ou une string brute (encodée en utf-8 par défaut).
    """
    _type_en = "a bytes object (e.g., b'data')"
    _type_py = "bytes"
    _type_json = {"type": "string"}

    @classmethod
    def _parse_native(cls, value: Any) -> Tuple[float, Any]:
        if isinstance(value, bytes):
            return 1.0, value
        return False, None

    @classmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[float, Any]:
        if isinstance(value, str):
            # Cas 1 : Représentation littérale Python "b'abc'"
            # C'était le comportement via eval() dans type_converter.py
            if value.strip().startswith("b'") or value.strip().startswith('b"'):
                try:
                    res = ast.literal_eval(value.strip())
                    if isinstance(res, bytes):
                        return 1.0, res
                except:
                    pass
            
            # Cas 2 : String brute -> Encodage UTF-8 (Fallback utile)
            return 1.0, value.encode("utf-8")
            
        if isinstance(value, (bytearray, memoryview)):
            return 1.0, bytes(value)
            
        return False, None


class GuardedByteArray(GuardedPrimitive, bytearray):
    """
    Séquence d'octets mutable.
    """
    _type_en = "a mutable bytearray"
    _type_py = "bytearray"
    _type_json = {"type": "string"}

    @classmethod
    def _parse_native(cls, value: Any) -> Tuple[float, Any]:
        if isinstance(value, bytearray):
            return 1.0, value
        return False, None

    @classmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[float, Any]:
        # On réutilise la logique de SemanticBytes
        valid, val = SemanticBytes._parse_heuristic(value)
        if valid:
            return 1.0, bytearray(val)
        return False, None

# ==============================================================================
# 8. TYPES QUI NE PEUVENT PAS ÊTRE SUBCLASSES EN PYTHON (bool, Range, etc.)
# ==============================================================================

class SubclassImpossible:
    """
    This is a proxy for types that cannot be subclassed directly in Python.
    """
    def __new__(cls, value):
        instance = super().__new__(cls)
        return instance
         
    def __repr__(self):
        
        string = "None"
        if self._python_value is not None:
            string = self._python_value.__repr__()
            
        return string

class GuardedNone(GuardedPrimitive, SubclassImpossible):
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


class GuardedAny(GuardedPrimitive, SubclassImpossible):
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

class GuardedBool(GuardedPrimitive, SubclassImpossible):

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
        
class GuardedMemoryView(GuardedPrimitive, SubclassImpossible):
    """
    Vue mémoire.
    Nécessite un objet bytes ou bytearray sous-jacent.
    Note: memoryview n'est pas subclassable en Python, on retourne donc
    l'objet memoryview natif directement.
    """
    _type_en = "a memoryview of bytes"
    _type_py = memoryview
    _type_json = {"type": "string"}

    def __new__(cls, value: Any):
        # memoryview n'est pas subclassable, on retourne donc directement
        # l'objet memoryview natif validé par attempt().
        # NOTE : On perdra les attributs _confidence/_source sur l'objet retourné
        # car 'memoryview' est un type built-in immuable et "fermé" en C.
        result = cls.attempt(value)
        if not result.is_success:
            raise ValueError(result.error_message)
        return result.value

    @classmethod
    def _parse_native(cls, value: Any) -> Tuple[float, Any]:
        if isinstance(value, memoryview):
            return 1.0, value
        return False, None

    @classmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[float, Any]:
        # On essaie de convertir en bytes d'abord
        valid, val = SemanticBytes._parse_heuristic(value)
        if valid:
            return 1.0, memoryview(val)
        return False, None


class GuardedRange(GuardedPrimitive, SubclassImpossible): 
    # Attention: range n'est pas subclassable facilement comme int ou str.
    # On hérite de GuardedPrimitive mais on ne peut pas hériter de 'range'.
    # On va simuler le comportement ou retourner un objet range natif via __new__.
    
    _type_en = "a range object (start, stop, step)"
    _type_py = range
    _type_json = {"type": "string", "pattern": "^range\\(\\d+(, \\d+)*\\)$"}

    def __new__(cls, value: Any):
        # Astuce : GuardedPrimitive.__new__ essaie d'appeler super().__new__(cls, val)
        # Comme on ne peut pas subclasser range, on retourne directement le range natif
        # qui aura été validé par attempt().
        # NOTE : On perdra les attributs _confidence/_source sur l'objet retourné 
        # car 'range' est un type built-in immuable et "fermé" en C.
        result = cls.attempt(value, description)
        if not result.is_success:
            raise ValueError(result.error_message)
        return result.value

    @classmethod
    def _parse_native(cls, value: Any) -> Tuple[float, Any]:
        if isinstance(value, range):
            return 1.0, value
        return False, None

    @classmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[float, Any]:
        if isinstance(value, str):
            clean = value.strip()
            # Support du format "range(1, 10)" ou "range(1, 10, 2)"
            # C'est ce que faisait eval() dans type_converter.py
            if clean.startswith("range(") and clean.endswith(")"):
                try:
                    # On parse les arguments à l'intérieur des parenthèses
                    content = clean[6:-1]
                    parts = [int(x.strip()) for x in content.split(",") if x.strip()]
                    return 1.0, range(*parts)
                except:
                    pass
        
        # Support liste/tuple [0, 10] -> range(0, 10)
        if isinstance(value, (list, tuple)) and 1 <= len(value) <= 3:
            try:
                args = [int(v) for v in value]
                return 1.0, range(*args)
            except:
                pass
                
        return False, None


# ==============================================================================
# 5. SEMANTIC ENUM (Choix Restreint)
# ==============================================================================

def create_semantic_enum(enum_cls: Type[Enum]) -> Type[GuardedPrimitive]:
    """
    Wrappe un Enum Python existant dans une Semantic Primitive.
    """
    # Récupération des valeurs possibles
    members = list(enum_cls)
    allowed_values = [m.value for m in members]
    allowed_names = [m.name for m in members]
    
    class GuardedEnumWrapper(GuardedPrimitive, str):
        _type_en = f"one of these values: {allowed_names}"
        _type_py = enum_cls.__name__
        _type_json = {"enum": allowed_values if all(isinstance(v, (str, int)) for v in allowed_values) else allowed_names}

        @classmethod
        def _parse_native(cls, value: Any) -> Tuple[float, Any]:
            # 1. C'est déjà un membre de l'enum
            if isinstance(value, enum_cls):
                return 1.0, value
            # 2. C'est la valeur (ex: 1)
            if value in allowed_values:
                return 1.0, enum_cls(value)
            # 3. C'est le nom (ex: "STATUS_OK")
            if isinstance(value, str) and value in allowed_names:
                return 1.0, enum_cls[value]
            return False, None

        @classmethod
        def _parse_heuristic(cls, value: Any) -> Tuple[float, Any]:
            # Nettoyage basique (ex: " STATUS_OK " -> "STATUS_OK")
            if isinstance(value, str):
                cleaned = value.strip().strip('"').strip("'")
                # Essai par nom
                if cleaned in allowed_names:
                    return 1.0, enum_cls[cleaned]
                # Essai par valeur stringifiée
                for m in members:
                    if str(m.value) == cleaned:
                        return 1.0, m
            return False, None
            
        # Bypass __new__ de GuardedPrimitive car Enum a son propre métaclass magic
        def __new__(cls, value):
             # On utilise attempt() manuellement pour valider/caster
             res = cls.attempt(value)
             if not res.is_success:
                 raise ValueError(res.error_message)
             return res.value 

    GuardedEnumWrapper.__name__ = f"Semantic_{enum_cls.__name__}"
    return GuardedEnumWrapper
