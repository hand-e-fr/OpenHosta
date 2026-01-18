# src/OpenHosta/semantics/scalars.py
import re
import ast

from enum import Enum
from typing import Any, Tuple, Type

from .primitives import GuardedPrimitive, SemanticType

class SemanticInt(int, SemanticType):
    """
    Entier sémantique.
    Accepte : 42, "42", "quarante-deux", "42.0" (si entier), "1 000".
    """
    __hash__ = GuardedPrimitive.__hash__
    
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


class SemanticFloat(float, SemanticType):
    """
    Nombre flottant sémantique.
    Accepte : 3.14, "3,14", "Pi environ", "10k".
    """
    __hash__ = GuardedPrimitive.__hash__

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


class SemanticBool(int, SemanticType):
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


class SemanticStr(str, SemanticType):
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
    
    class SemanticEnumWrapper(enum_cls, GuardedPrimitive):
        _type_en = f"one of these values: {allowed_names}"
        _type_py = enum_cls.__name__
        _type_json = {"enum": allowed_values if all(isinstance(v, (str, int)) for v in allowed_values) else allowed_names}

        @classmethod
        def _parse_native(cls, value: Any) -> Tuple[bool, Any]:
            # 1. C'est déjà un membre de l'enum
            if isinstance(value, enum_cls):
                return True, value
            # 2. C'est la valeur (ex: 1)
            if value in allowed_values:
                return True, enum_cls(value)
            # 3. C'est le nom (ex: "STATUS_OK")
            if isinstance(value, str) and value in allowed_names:
                return True, enum_cls[value]
            return False, None

        @classmethod
        def _parse_heuristic(cls, value: Any) -> Tuple[bool, Any]:
            # Nettoyage basique (ex: " STATUS_OK " -> "STATUS_OK")
            if isinstance(value, str):
                cleaned = value.strip().strip('"').strip("'")
                # Essai par nom
                if cleaned in allowed_names:
                    return True, enum_cls[cleaned]
                # Essai par valeur stringifiée
                for m in members:
                    if str(m.value) == cleaned:
                        return True, m
            return False, None
            
        # Bypass __new__ de GuardedPrimitive car Enum a son propre métaclass magic
        def __new__(cls, value, description=""):
             # On utilise attempt() manuellement pour valider/caster
             res = cls.attempt(value, description)
             if not res.is_success:
                 raise ValueError(res.error_message)
             return res.value 

    SemanticEnumWrapper.__name__ = f"Semantic_{enum_cls.__name__}"
    return SemanticEnumWrapper


# ==============================================================================
# 6. SEMANTIC LITERAL (Valeurs Constantes)
# ==============================================================================

def create_semantic_literal(literals: Tuple[Any]) -> Type[GuardedPrimitive]:
    """Gère typing.Literal['A', 'B']"""
    
    class SemanticLiteral(GuardedPrimitive):
        _allowed = literals
        _type_en = f"specifically one of: {literals}"
        _type_py = f"Literal{literals}"
        _type_json = {"enum": list(literals)}
        
        def __new__(cls, value, description=""):
             res = cls.attempt(value, description)
             if not res.is_success: raise ValueError(res.error_message)
             return res.value # Retourne la valeur brute (int ou str), pas une instance de classe

        @classmethod
        def _parse_native(cls, value: Any) -> Tuple[bool, Any]:
            return (True, value) if value in cls._allowed else (False, None)

        @classmethod
        def _parse_heuristic(cls, value: Any) -> Tuple[bool, Any]:
            if isinstance(value, str):
                v = value.strip().strip("'").strip('"')
                if v in cls._allowed: return True, v
                # Tentative de conversion numérique si le literal contient des nombres
                try:
                    if int(v) in cls._allowed: return True, int(v)
                except: pass
            return False, None

    SemanticLiteral.__name__ = f"Literal_{len(literals)}"
    return SemanticLiteral

# ==============================================================================
# 7. TYPES AVANCÉS (Complex, Bytes, Range)
# ==============================================================================

class SemanticComplex(complex, GuardedPrimitive):
    """
    Nombre complexe.
    Accepte : 1+2j, "1+2j", "(1+2j)".
    """
    _type_en = "a complex number (real + imaginary parts, e.g., 1+2j)"
    _type_py = "complex"
    _type_json = {"type": "string", "pattern": "^[\\d\\+\\-\\.j\\(\\)\\s]+$"}

    @classmethod
    def _parse_native(cls, value: Any) -> Tuple[bool, Any]:
        if isinstance(value, complex):
            return True, value
        return False, None

    @classmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[bool, Any]:
        if isinstance(value, str):
            # Nettoyage
            v = value.strip().replace(" ", "")
            try:
                # complex("1+2j") fonctionne nativement en Python
                return True, complex(v)
            except ValueError:
                pass
        return False, None


class SemanticBytes(bytes, GuardedPrimitive):
    """
    Séquence d'octets immuable.
    Accepte : b'hello', "b'hello'", ou une string brute (encodée en utf-8 par défaut).
    """
    _type_en = "a bytes object (e.g., b'data')"
    _type_py = "bytes"
    _type_json = {"type": "string"}

    @classmethod
    def _parse_native(cls, value: Any) -> Tuple[bool, Any]:
        if isinstance(value, bytes):
            return True, value
        return False, None

    @classmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[bool, Any]:
        if isinstance(value, str):
            # Cas 1 : Représentation littérale Python "b'abc'"
            # C'était le comportement via eval() dans type_converter.py
            if value.strip().startswith("b'") or value.strip().startswith('b"'):
                try:
                    res = ast.literal_eval(value.strip())
                    if isinstance(res, bytes):
                        return True, res
                except:
                    pass
            
            # Cas 2 : String brute -> Encodage UTF-8 (Fallback utile)
            return True, value.encode("utf-8")
            
        if isinstance(value, (bytearray, memoryview)):
            return True, bytes(value)
            
        return False, None


class SemanticByteArray(bytearray, GuardedPrimitive):
    """
    Séquence d'octets mutable.
    """
    _type_en = "a mutable bytearray"
    _type_py = "bytearray"
    _type_json = {"type": "string"}

    @classmethod
    def _parse_native(cls, value: Any) -> Tuple[bool, Any]:
        if isinstance(value, bytearray):
            return True, value
        return False, None

    @classmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[bool, Any]:
        # On réutilise la logique de SemanticBytes
        valid, val = SemanticBytes._parse_heuristic(value)
        if valid:
            return True, bytearray(val)
        return False, None


class SemanticMemoryView(GuardedPrimitive):
    """
    Vue mémoire.
    Nécessite un objet bytes ou bytearray sous-jacent.
    Note: memoryview n'est pas subclassable en Python, on retourne donc
    l'objet memoryview natif directement.
    """
    _type_en = "a memoryview of bytes"
    _type_py = "memoryview"
    _type_json = {"type": "string"}

    def __new__(cls, value: Any, description: str = ""):
        # memoryview n'est pas subclassable, on retourne donc directement
        # l'objet memoryview natif validé par attempt().
        # NOTE : On perdra les attributs _confidence/_source sur l'objet retourné
        # car 'memoryview' est un type built-in immuable et "fermé" en C.
        result = cls.attempt(value, description)
        if not result.is_success:
            raise ValueError(result.error_message)
        return result.value

    @classmethod
    def _parse_native(cls, value: Any) -> Tuple[bool, Any]:
        if isinstance(value, memoryview):
            return True, value
        return False, None

    @classmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[bool, Any]:
        # On essaie de convertir en bytes d'abord
        valid, val = SemanticBytes._parse_heuristic(value)
        if valid:
            return True, memoryview(val)
        return False, None


class SemanticRange(GuardedPrimitive): 
    # Attention: range n'est pas subclassable facilement comme int ou str.
    # On hérite de GuardedPrimitive mais on ne peut pas hériter de 'range'.
    # On va simuler le comportement ou retourner un objet range natif via __new__.
    
    _type_en = "a range object (start, stop, step)"
    _type_py = "range"
    _type_json = {"type": "string", "pattern": "^range\\(\\d+(, \\d+)*\\)$"}

    def __new__(cls, value: Any, description: str = ""):
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
    def _parse_native(cls, value: Any) -> Tuple[bool, Any]:
        if isinstance(value, range):
            return True, value
        return False, None

    @classmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[bool, Any]:
        if isinstance(value, str):
            clean = value.strip()
            # Support du format "range(1, 10)" ou "range(1, 10, 2)"
            # C'est ce que faisait eval() dans type_converter.py
            if clean.startswith("range(") and clean.endswith(")"):
                try:
                    # On parse les arguments à l'intérieur des parenthèses
                    content = clean[6:-1]
                    parts = [int(x.strip()) for x in content.split(",") if x.strip()]
                    return True, range(*parts)
                except:
                    pass
        
        # Support liste/tuple [0, 10] -> range(0, 10)
        if isinstance(value, (list, tuple)) and 1 <= len(value) <= 3:
            try:
                args = [int(v) for v in value]
                return True, range(*args)
            except:
                pass
                
        return False, None
