r"""
Module :mod:`subclassablepydantic`

Définit un wrapper pour les modèles Pydantic (v2) afin de les intégrer dans le système Guarded.
Permet de construire des :class:`GuardedPydanticModel` qui encapsulent un :class:`pydantic.BaseModel` 
et en exposent le schéma de manière lisible dans les prompts.
"""

from typing import Type, Any, Dict, List, Optional
from .primitives import GuardedPrimitive, ProxyWrapper, Tolerance, UncertaintyLevel
from ..guarded import GuardedDict, GuardedUtf8

try:
    from pydantic import BaseModel, Field
    from pydantic_core import ValidationError
except ImportError:
    class BaseModel: pass
    Field = None
    ValidationError = Exception

# Cache pour éviter de reconstruire la même classe multiple fois
_PYDANTIC_GUARDED_CACHE: Dict[Type[BaseModel], Type[GuardedPrimitive]] = {}


def guarded_pydantic_model(model_cls: Type[BaseModel]) -> Type[GuardedPrimitive]:
    """
    Transforme un modèle Pydantic en type Guarded utilisable dans OpenHosta.

    Le type résultant peut :
    - Être appelé pour valider une entrée (str, dict…)
    - Être affiché dans un prompt avec une description riche des champs

    Args:
        model_cls: Une classe héritant de pydantic.BaseModel

    Returns:
        Une classe Guarded exécutable
    """
    if model_cls in _PYDANTIC_GUARDED_CACHE:
        return _PYDANTIC_GUARDED_CACHE[model_cls]

    def describe(model_cls: Type[BaseModel]):
        """
        Génère une description lisible du modèle Pydantic,
        incluant les champs, descriptions, alias, valeurs par défaut, etc.
        """
        schema = model_cls.model_json_schema()
        props = schema.get("properties", {})
        required_fields = schema.get("required", [])

        lines = []
        model_name = model_cls.__name__
        title = schema.get("title", model_name)
        desc = schema.get("description", "").strip()
        if desc:
            lines.append(f"{title}: {desc}")
        else:
            lines.append(f"{title}: structure structurée attendue")

        lines.append("")

        if not props:
            lines.append("  (Aucun champ spécifié)")
        else:
            for field_name, field_info in props.items():
                field_lines = []

                # Récupérer l'alias si présent
                alias = field_info.get("alias")
                display_name = alias if alias else field_name

                # Marquer si requis
                req_marker = "[Requis]" if field_name in required_fields else "[Optionnel]"

                # Description
                field_desc = field_info.get("description", "").strip()
                type_info = field_info.get("type", "unknown")

                # Type
                if "anyOf" in field_info:
                    types = [t.get("type", "unknown") for t in field_info["anyOf"] if "type" in t]
                    if "null" in [t.get("type") for t in field_info.get("anyOf", [])]:
                        union_type = " | ".join(t for t in types if t != "null")
                        type_label = f"Union[{union_type}, None]"
                    else:
                        type_label = " | ".join(set(types))
                elif "allOf" in field_info:
                    type_label = "Combined Object"
                elif "enum" in field_info:
                    enum_values = ", ".join([repr(v) for v in field_info["enum"]])
                    type_label = f"Enum[{enum_values}]"
                else:
                    type_label = type_info.capitalize()

                # Ligne principale
                field_lines.append(f"- {display_name} {req_marker} : {type_label}")
                if field_desc:
                    field_lines.append(f"    {field_desc}")

                # Exemples
                examples = field_info.get("examples")
                if not examples:
                    examples = field_info.get("example")
                if examples:
                    if not isinstance(examples, list):
                        examples = [examples]
                    ex_str = " | ".join(repr(ex) for ex in examples[:3])  # max 3
                    field_lines.append(f"    Exemple: {ex_str}")

                lines.extend(field_lines)

        return "\n".join(lines)

    class GuardedPydanticModel(GuardedPrimitive, ProxyWrapper):
        _type_en = f"an instance of {model_cls.__name__} dataclass"
        _type_py = model_cls
        _type_py_repr = describe(model_cls)
        _type_json = model_cls.schema()
        _tolerance = Tolerance.TYPE_COMPLIANT
        
        
        @classmethod  
        def _parse_heuristic(cls, value: Any):

            # We try to make it as a string if it's not already a string, to let the LLM try to parse it as a constructor call or dict
            value = str(value).strip("\"'").replace("\n", "")

            # Si c'est une string qui ressemble à un appel constructeur: Person(...)
            if isinstance(value, str) and (
                value.strip().startswith(cls.__name__ + "(") or
                value.strip().startswith("{")
            ):
                import ast
                tree = ast.parse(value.strip(), mode='eval')
                if isinstance(tree.body, ast.Call):
                    parsed_args = []
                    parsed_kwargs = {}
                    for arg in tree.body.args:
                        parsed_args.append(ast.literal_eval(arg))
                    for keyword in tree.body.keywords:
                        parsed_kwargs[keyword.arg] = ast.literal_eval(keyword.value)
                    
                    # Tenter d'instancier avec les args parsés
                    try:
                        # On crée l'instance directement via le constructeur
                        instance = model_cls(*tuple(parsed_args), **parsed_kwargs)
                        return UncertaintyLevel(Tolerance.PRECISE), instance, None

                    except Exception as e:
                        # Si échec instanciation directe, essayer via dict mode si possible ou fail
                        return UncertaintyLevel(Tolerance.ANYTHING), value, str(e)
                elif isinstance(tree.body, ast.Dict):
                    # Tenter d'instancier avec les args parsés
                    try:
                        native_instance = model_cls(**GuardedDict(GuardedUtf8(value)))
                        return UncertaintyLevel(Tolerance.PRECISE), native_instance, None

                    except Exception as e:
                        # Si échec instanciation directe, essayer via dict mode si possible ou fail
                        return UncertaintyLevel(Tolerance.ANYTHING), value, str(e)

                else:
                    return UncertaintyLevel(Tolerance.ANYTHING), value, "String format not recognized as constructor call or dict"

            return UncertaintyLevel(Tolerance.ANYTHING), value, f"Could not parse as {cls.__name__} dataclass: id of type {id(type(value))} with value {value}. id of cls {id(cls)}"


    _PYDANTIC_GUARDED_CACHE[model_cls] = GuardedPydanticModel

    return GuardedPydanticModel