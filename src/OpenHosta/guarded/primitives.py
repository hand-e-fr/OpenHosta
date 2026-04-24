# src/OpenHosta/guarded/primitives.py
"""
Module core du système de types Guarded.

Le système Guarded implémente un pipeline de validation à plusieurs niveaux
qui transforme des entrées arbitraires en types Python natifs avec métadonnées
de confiance et de traçabilité.

Pipeline de validation (du plus rapide au plus lent) :
1. **Native**    : Vérification de type direct (isinstance)
                   Coût: O(1), Uncertainty: 0.0 (STRICT)
                   
2. **Heuristic** : Nettoyage déterministe (regex, strip, cast)
                   Coût: O(n), Uncertainty: 0.05-0.15
                   
3. **Semantic**  : Conversion via LLM (non implémenté)
                   Coût: ~1s, Uncertainty: 0.15-0.30
                   
4. **Knowledge** : Consultation de base de connaissances
                   Coût: Variable, Uncertainty: 0.30+

Architecture :
    GuardedPrimitive (ABC)
    ├── Héritage Direct (types subclassables)
    │   ├── GuardedInt(int)
    │   ├── GuardedUtf8(str)
    │   ├── GuardedFloat(float)
    │   ├── GuardedList(list)
    │   ├── GuardedDict(dict)
    │   └── ...
    │
    └── ProxyWrapper (types non-subclassables)
        ├── GuardedBool
        ├── GuardedNone
        ├── GuardedRange
        └── GuardedEnum

Exemple d'utilisation :
    >>> from OpenHosta.guarded import GuardedInt
    >>> age = GuardedInt("42 ans")  # Heuristic cleaning
    >>> age
    42
    >>> age.uncertainty
    0.15
    >>> age.abstraction_level
    'heuristic'
    >>> age + 10
    52

Création de types personnalisés :
    >>> class CorporateEmail(GuardedUtf8):
    ...     _type_en = "a corporate email address"
    ...     _tolerance = Tolerance.PRECISE
    ...     
    ...     @classmethod
    ...     def _parse_heuristic(cls, value):
    ...         value = str(value).strip().lower()
    ...         if '@company.com' not in value:
    ...             return UncertaintyLevel(Tolerance.ANYTHING), value, "Invalid domain"
    ...         return UncertaintyLevel(Tolerance.PRECISE), value, None
    
    >>> email = CorporateEmail("John.Doe@COMPANY.COM")
    >>> email
    'john.doe@company.com'
"""

import re
from abc import ABC, ABCMeta
from typing import Any, Tuple, ClassVar, Dict, Optional, Literal
from dataclasses import dataclass, is_dataclass, fields


# Imports internes (Moteur & Incertitude)
from .constants import Tolerance, ToleranceLevel


AbstractionLevel = Literal["native", "heuristic", "semantic", "knowledge", "failed"]
UncertaintyLevel = float

@dataclass(frozen=True)
class GuardedCallInput:
    """Conteneur pour transporter plusieurs arguments dans le pipeline Guarded."""
    args: tuple[Any, ...]
    kwargs: dict[str, Any]


@dataclass
class CastingResult:

    success: bool
    
    data: Any    # La valeur convertie (ex: 23) ou None
    uncertainty: float   # Score de 0.0 à 1.0
    abstraction: AbstractionLevel 

    original_input: Any
    guarded_data: Any = None # Instance de GuardedPrimitive ou ProxyWrapper correspondent au type attendu
    python_type: Optional[type] = None

    error_message: Optional[str] = None
    

class GuardedPrimitiveMeta(ABCMeta):
    def __repr__(cls):
        if cls._type_py_repr is not NotImplemented:
            _type_py_repr = str(cls._type_py_repr)
        else:
            _type_py_repr = str(cls._type_py)

        return (
            f"# Description for guarded type '{cls.__name__}':\n"
            f"# Python Type: {_type_py_repr}\n"
            f"# English Description: {cls._type_en}\n"
        )


class GuardedPrimitive(ABC, metaclass=GuardedPrimitiveMeta):
    """
    Mixin abstrait qui implémente le pipeline de validation 'OpenHosta'.
    Il transforme une entrée arbitraire en type natif via :
    1. Check Natif (Instant)
    2. Heuristique (Rapide)
    3. LLM (Intelligent & Coûteux)
    4. Règles métier
    """

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        # Convention d'architecture OpenHosta:
        # GuardedPrimitive doit apparaître en première base explicite dès qu'il est
        # utilisé en héritage multiple. Cela garantit que son __new__ pilote bien
        # la construction via le MRO.
        direct_bases = getattr(cls, "__bases__", ())
        if len(direct_bases) > 1 and direct_bases[0] is not GuardedPrimitive:
            raise TypeError(
                f"Class {cls.__name__} must declare GuardedPrimitive as first base "
                f"to preserve Guarded MRO construction. Expected something like "
                f"'(GuardedPrimitive, ...)', got {direct_bases}."
            )

    # --- Interface Déclarative (À définir par les classes enfants) ---
    
    # 4 niveaux du plus générique au plus spécifique utilisables par les AbtractionLevels
    # - 1. Langage naturel (Anglais)
    # - 2. Type Python natif
    # - 3. Schéma JSON
    # - 4. Connaissances spécifiques (term métier dans une taxonomie ou un graph)
    
    _type_en: ClassVar[str] = NotImplemented
    _type_py_repr: ClassVar[str] = NotImplemented
    _type_py: ClassVar[type] = NotImplemented
    _type_json: ClassVar[Dict[str, Any]] = NotImplemented
    _type_knowledge: ClassVar[Dict | Any] = NotImplemented
    _tolerance: ClassVar[ToleranceLevel] = Tolerance.TYPE_COMPLIANT
    
    def __new__(cls, *args: Any, **kwargs: Any):
        """
        Le constructeur 'Magique'. Il ne crée l'objet que si le analyseur sémantique réussit.

        Si plusieurs arguments positionnels et/ou nommés sont fournis, ils sont
        encapsulés dans un GuardedCallInput et transmis comme valeur unique au pipeline.
        Le forçage de la tolérance se fait exclusivement via attempt() ou en
        surchargeant l'attribut de classe _tolerance.
        """

        # 0. Use docsting as type definition in natural language (_type_en) if not defined
        if cls._type_en == NotImplemented:
            cls._type_en = f"{cls.__doc__}"

        if cls._type_py is NotImplemented:
            for parent in cls.__mro__:
                if parent in (int, float, str, bool, list, dict, set, tuple):
                    cls._type_py = parent
                    break

        if len(args) == 1 and not kwargs:
            value = args[0]
        else:
            value = GuardedCallInput(args=args, kwargs=kwargs)

        # 1. Lancement du Pipeline (Template Method)
        result = cls.attempt(value)

        # Si l'appel vient de attempt() on peut déjà avoir l'instance prête
        if result.success and isinstance(result.guarded_data, cls):
            return result.guarded_data


        # 2. Gestion de l'échec
        if not result.success:
            raise ValueError(
                f"OpenHosta Casting Failed for type '{cls.__name__}'.\n"
                f"Input: '{value}'\n"
                f"Error: {result.error_message}"
            )

        # 3. Création de l'instance native (int, str, list...)
        # Note: Pour les types mutables (list, dict, set), super().__new__(cls) 
        # retourne une instance vide. On la remplira dans __init__.
        try:
            instance = super().__new__(cls, result.data)
        except TypeError:
            # Certains types ne prennent pas d'arguments dans __new__
            instance = super().__new__(cls)

        # 4. Injection des Métadonnées
        instance._input = value
        instance._uncertainty = result.uncertainty
        instance._abstraction_level = result.abstraction
        instance._python_value = result.data
        
        return instance

    def __init__(self, *args: Any, **kwargs: Any):
        """
        L'initialiseur est appelé après __new__.
        Pour les types mutables (list, dict, set), on doit s'assurer que
        l'instance est peuplée avec la valeur CONVERTIE, pas l'entrée originale.
        """
        # Si c'est un type mutable, on le vide et on le remplit avec la valeur convertie
        # Cela évite que list.__init__ soit appelé avec 'value' original
        python_value = getattr(self, "_python_value", None)
        
        if isinstance(self, list):
            if list(self) != python_value:
                self.clear()
                if python_value is not None:
                    self.extend(python_value)
        elif isinstance(self, dict):
            if dict(self) != python_value:
                self.clear()
                if python_value is not None:
                    self.update(python_value)
        elif isinstance(self, set):
            if set(self) != python_value:
                self.clear()
                if python_value is not None:
                    self.update(python_value)
        # Pour les types immuables (int, str...), __init__ ne fait rien car
        # la valeur a déjà été fixée dans __new__.

    @property
    def uncertainty(self) -> UncertaintyLevel:
        """Score de confiance de la conversion (0.0 à 1.0)."""
        return getattr(self, '_uncertainty', 1.0)

    @property
    def abstraction_level(self) -> str:
        """Niveau d'abstracton utilisé pour la conversion (native, heuristic, vectorial, llm)."""
        return getattr(self, '_abstraction_level', 'unknown')

    @staticmethod
    def _recursive_unwrap(value: Any, seen: set[int]|None = None) -> Any:
        if seen is None:
            seen = set()
            
        obj_id = id(value)
        if obj_id in seen:
            return value

        seen.add(obj_id)
        try:
            if hasattr(value, "unwrap") and callable(value.unwrap) and isinstance(value, GuardedPrimitive):
                
                unwrapped = getattr(value, "_python_value", None)
                if unwrapped is value:
                    if is_dataclass(value):
                        dataclass_type = type(value)
                        data = {
                            field.name: GuardedPrimitive._recursive_unwrap(
                                getattr(value, field.name), seen
                            )
                            for field in fields(value)
                        }
                        try:
                            return dataclass_type(**data)
                        except Exception:
                            return data
                    return value

                return GuardedPrimitive._recursive_unwrap(unwrapped, seen)

            if is_dataclass(value):
                dataclass_type = type(value)
                data = {
                    field.name: GuardedPrimitive._recursive_unwrap(
                        getattr(value, field.name), seen
                    )
                    for field in fields(value)
                }
                try:
                    return dataclass_type(**data)
                except Exception:
                    return data

            if isinstance(value, dict):
                return {
                    GuardedPrimitive._recursive_unwrap(k, seen): GuardedPrimitive._recursive_unwrap(v, seen)
                    for k, v in value.items()
                }
            if isinstance(value, list):
                return [GuardedPrimitive._recursive_unwrap(item, seen) for item in value]
            if isinstance(value, tuple):
                return tuple(GuardedPrimitive._recursive_unwrap(item, seen) for item in value)
            if isinstance(value, set):
                return {GuardedPrimitive._recursive_unwrap(item, seen) for item in value}
            if isinstance(value, frozenset):
                return frozenset(GuardedPrimitive._recursive_unwrap(item, seen) for item in value)
            return value
        finally:
            seen.discard(obj_id)


    def unwrap(self):
        """Méthode utilitaire pour récupérer la valeur native avec unwrapping récursif."""
        return self._recursive_unwrap(self)


    @classmethod
    def _clean_llm_response(cls, value: str) -> str:
        """
        Nettoie une réponse brute du LLM pour extraire la valeur utile.
        - Extrait le contenu des blocs de code Markdown (```python ... ```)
        - Supprime les commentaires Python (# ...)
        - Gère les commentaires non-standard (ex: * ...)
        - Supprime les explications textuelles avant/après l'expression
        """
        if not isinstance(value, str):
            return value

        cleaned = value.strip()

        # 1. Extraction des blocs de code Markdown
        # On cherche le premier bloc ```python ou ``` et on prend son contenu
        code_block_match = re.search(r"```(?:python)?\n?(.*?)\n?```", cleaned, re.DOTALL)
        if code_block_match:
            cleaned = code_block_match.group(1).strip()
        else:
            # 1.b Heuristique pour le bruit avant l'expression (ex: "Le résultat est : 42")
            # Si on n'a pas de bloc Markdown, on regarde s'il y a un séparateur ':'
            if ":" in cleaned and not (cleaned.startswith("{") or cleaned.startswith("[")):
                # On split au premier ':'
                parts = cleaned.split(":", 1)
                prefix = parts[0].strip()
                potential = parts[1].strip()
                
                # Si la partie après ':' commence par un caractère d'expression typique, on la garde
                is_expr = potential and (potential[0] in "[{('\"-0123456789" or 
                                       potential.lower().startswith(("true", "false", "none")) or
                                       re.match(r"^[A-Z][a-zA-Z0-9_]*\(", potential))
                if is_expr:
                    cleaned = potential

        # 2. Heuristique pour les explications après l'expression
        # On fait ça AVANT de supprimer les lignes vides, car on s'appuie sur \n\n
        if "\n\n" in cleaned:
            # On ne coupe que si la première partie semble être une expression complète
            potential_expr = cleaned.split("\n\n")[0].strip()
            
            # Heuristiques de complétude :
            # 1. Scalaire simple (int, float, bool, None, complex)
            is_simple_val = potential_expr.isnumeric() or \
                            potential_expr.replace(".","").replace("+","").replace("-","").replace("j","").isnumeric() or \
                            potential_expr.lower() in ("true", "false", "none")
            # 2. Chaîne quotée
            is_quoted = (potential_expr.startswith("'") and potential_expr.endswith("'")) or \
                        (potential_expr.startswith('"') and potential_expr.endswith('"'))
            # 3. Nom qualifié (Enum)
            is_qualified = re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)+", potential_expr)
            # 4. Parenthèses/Crochets/Accolades équilibrés
            is_balanced = (potential_expr.endswith(")") and potential_expr.count("(") == potential_expr.count(")")) or \
                          (potential_expr.endswith("]") and potential_expr.count("[") == potential_expr.count("]")) or \
                          (potential_expr.endswith("}") and potential_expr.count("{") == potential_expr.count("}"))
            
            if is_simple_val or is_quoted or is_qualified or is_balanced:
                cleaned = potential_expr

        # 3. Suppression des commentaires ligne par ligne
        lines = cleaned.split("\n")
        new_lines = []
        for line in lines:
            # Supprimer tout ce qui suit #
            line = line.split("#")[0]
            # Supprimer tout ce qui suit * s'il est précédé d'un espace ou en début de ligne
            if " *" in line:
                line = line.split(" *")[0]
            elif line.strip().startswith("*"):
                line = ""
            
            if line.strip():
                new_lines.append(line.rstrip())
        
        cleaned = "\n".join(new_lines).strip()

        return cleaned

    @classmethod
    def attempt(cls, value: Any, tolerance: ToleranceLevel|None = None) -> CastingResult:
        """
        Le SQUELETTE de l'algorithme (Template Method).
        Orchestre les tentatives du moins coûteux au plus coûteux.
        """

        if tolerance is None:
            tolerance = cls._tolerance
    
        errors = []
        # At each layer we have a chance to reduce uncertainty
        
        def return_success(cleaned_val, uncertainty, level, message):
            res = CastingResult(
                success=True, 
                data=cleaned_val, 
                uncertainty=uncertainty, 
                abstraction=level, 
                original_input=value, 
                python_type=cls._type_py, 
                error_message=message
            )
            try:
                # To avoid infinite recursion, we instantiate WITHOUT calling cls.__new__ again.
                if issubclass(cls, ProxyWrapper):
                    instance = object.__new__(cls)
                else:
                    base_type = cls._type_py if cls._type_py is not NotImplemented else object
                    try:
                        instance = base_type.__new__(cls, cleaned_val)
                    except TypeError:
                        instance = base_type.__new__(cls)

                instance._input = value
                instance._uncertainty = uncertainty
                instance._abstraction_level = level
                instance._python_value = cleaned_val
                
                if isinstance(instance, (list, set, dict)):
                    instance.clear()
                    if isinstance(instance, list): instance.extend(cleaned_val)
                    elif isinstance(instance, set): instance.update(cleaned_val)
                    elif isinstance(instance, dict): instance.update(cleaned_val)

                res.guarded_data = instance
            except Exception:
                pass
            return res

        uncertainty, cleaned_native_val, message = cls._parse_native(value)
        if uncertainty <= tolerance:
            return return_success(cleaned_native_val, uncertainty, 'native', message)
        errors.append(f"Native parsing failed: {message}")

        uncertainty, cleaned_heuristic_val, message = cls._parse_heuristic(cleaned_native_val)
        if uncertainty <= tolerance:
            return return_success(cleaned_heuristic_val, uncertainty, 'heuristic', message)
        errors.append(f"Heuristic parsing failed: {message}")

        uncertainty, cleaned_semantic_value, message = cls._parse_semantic(cleaned_heuristic_val)
        if uncertainty <= tolerance:
            return return_success(cleaned_semantic_value, uncertainty, 'semantic', message)
        errors.append(f"Semantic parsing failed: {message}")
        
        uncertainty, cleaned_knowledge_value, message = cls._parse_knowledge(cleaned_semantic_value)
        if uncertainty <= tolerance:
            return return_success(cleaned_knowledge_value, uncertainty, 'knowledge', message)
        errors.append(f"Knowledge parsing failed: {message}")

        def _get_best_error(errors_list):
            for err in errors_list:
                if err and "→" in err:
                    # On retire le préfixe "Native parsing failed: " ou "Heuristic..." s'il existe
                    if ":" in err and ("parsing failed" in err):
                        return err.split(":", 1)[1].strip()
                    return err
            return "\n".join(e for e in errors_list if e)

        best_message = _get_best_error(errors)
        return CastingResult(False, None, None, Tolerance.ANYTHING, 'failed', value, cls._type_py, best_message)
    
    # --- Hooks Abstraits (À implémenter par SemanticInt, SemanticUtf8...) ---
    
    @classmethod
    def _parse_native(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        """Retourne (uncertainty, value, error_message) si value est DÉJÀ valide."""
        if type(value) == cls._type_py:
            return UncertaintyLevel(Tolerance.STRICT), value, None
        
        return UncertaintyLevel(Tolerance.ANYTHING), value, None

    @classmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        """Tentative de nettoyage déterministe (Regex, Strip...).
        
        Retourne (uncertainty, cleaned_val, error_message) où uncertainty ∈ [0, 1]."""
        
        value = str(value)
        
        try:
            value = cls._type_py(value)
            return UncertaintyLevel(Tolerance.TYPE_COMPLIANT), value, None
        except Exception as e:
            pass
        
        return UncertaintyLevel(Tolerance.ANYTHING), value, None
        
    
    @classmethod
    def _parse_semantic(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        """
        Tentative de nettoyage via LLM.
        """
        return UncertaintyLevel(Tolerance.ANYTHING), value, None

        
    @classmethod
    def _parse_knowledge(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        """
        Tentative de nettoyage par une base de connaissance.
        """
        return UncertaintyLevel(Tolerance.ANYTHING), value, None


    ### Pydantic V2 Integration ###

    @classmethod
    def __get_pydantic_core_schema__(cls, _abstraction_level_type: Any, _handler: Any) -> Any:
        """
        Intègre GuardedPrimitive avec Pydantic V2.
        Permet la conversion automatique depuis n'importe quelle entrée.
        """
        from pydantic_core import core_schema
        
        return core_schema.with_info_before_validator_function(
            cls._pydantic_validate,
            core_schema.any_schema()
        )

    @classmethod
    def _pydantic_validate(cls, value: Any, _info: Any) -> Any:
        # Si c'est déjà une instance, on la garde
        if isinstance(value, cls):
            return value
        # Sinon on passe par le constructeur magique (pipeline)
        return cls(value)

    @classmethod
    def __get_pydantic_json_schema__(cls, _core_schema: Any, handler: Any) -> Any:
        """
        Retourne le schéma JSON du type pour Pydantic/OpenAPI.
        Utilise _type_json défini dans les sous-classes.
        """
        # On utilise le mapping _type_json s'il existe, sinon on délègue
        if cls._type_json is not NotImplemented:
            return cls._type_json
        return handler(_core_schema)

class ProxyWrapper:
    """
    Mixin pour types Python non-subclassables (bool, range, memoryview, NoneType).
    
    IMPORTANT:
    - Cette classe ne doit pas piloter la construction des objets.
    - `GuardedPrimitive` doit apparaître AVANT `ProxyWrapper` dans l'héritage
      multiple afin que son `__new__` soit utilisé (MRO).
    - `ProxyWrapper` fournit uniquement les comportements de délégation/proxy.
    
    Exemple correct:
        class GuardedBool(GuardedPrimitive, ProxyWrapper):
            ...
    """

    def unwrap(self):
        """Retourne la valeur Python native avec unwrapping récursif."""
        return GuardedPrimitive._recursive_unwrap(getattr(self, "_python_value", None))

    def __getattr__(self, name):

        """Délègue l'accès aux attributs à la valeur native."""
        return getattr(self._python_value, name)
    
    # Délégation des opérations de comparaison
    def __eq__(self, other):
        if isinstance(other, ProxyWrapper):
            return self._python_value == other._python_value
        return self._python_value == other
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __hash__(self):
        return hash(self._python_value)
    
    def __repr__(self):
        return repr(self._python_value) if self._python_value is not None else "None"
    
    def __str__(self):
        return str(self._python_value) if self._python_value is not None else "None"

    def __call__(self, *args, **kwargs):
        """Délègue l'appel à la valeur native si elle est callable."""
        if callable(self._python_value):
            return self._python_value(*args, **kwargs)
        raise TypeError(f"'{type(self).__name__}' object is not callable")

    def __len__(self):
        return len(self._python_value)

    def __iter__(self):
        return iter(self._python_value)

    def __contains__(self, item):
        return item in self._python_value

    def __getitem__(self, key):
        return self._python_value[key]
