r"""
Module :mod:`subclassablepydantic`

Définit un wrapper pour les modèles Pydantic (v2) afin de les intégrer dans le système Guarded.
Permet de construire des :class:`GuardedPydanticModel` qui encapsulent un :class:`pydantic.BaseModel` 
et en exposent le schéma de manière lisible dans les prompts.
"""

from typing import Type, Any, Dict, List, Optional
from .primitives import GuardedPrimitive, ProxyWrapper, Tolerance, UncertaintyLevel
from ..guarded import GuardedDict, GuardedUtf8
from .resolver import TypeResolver
from .type_hints import resolve_struct_hints

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
        _type_json = model_cls.model_json_schema()
        _tolerance = Tolerance.TYPE_COMPLIANT
        
        
        @classmethod
        def _parse_heuristic(cls, value: Any):

            # 1. Obtenir un dictionnaire de données
            data_dict = None
            if isinstance(value, dict):
                data_dict = value
            elif isinstance(value, str):
                v_strip = value.strip().strip("\"'").replace("\n", "")
                if v_strip.startswith(model_cls.__name__ + "(") or v_strip.startswith("{"):
                    import ast
                    try:
                        tree = ast.parse(v_strip, mode='eval')
                        if isinstance(tree.body, ast.Call):
                            parsed_args = [ast.literal_eval(arg) for arg in tree.body.args]
                            parsed_kwargs = {}
                            for kw in tree.body.keywords:
                                try: parsed_kwargs[kw.arg] = ast.literal_eval(kw.value)
                                except: parsed_kwargs[kw.arg] = ast.unparse(kw.value)
                            
                            # Convert args to kwargs
                            import inspect
                            sig = inspect.signature(model_cls)
                            bound = sig.bind(*parsed_args, **parsed_kwargs)
                            bound.apply_defaults()
                            data_dict = bound.arguments
                        elif isinstance(tree.body, ast.Dict):
                            try:
                                data_dict = ast.literal_eval(v_strip)
                            except:
                                import json
                                # Replace JSON literals with Python ones if needed (basic cases)
                                json_v = v_strip.replace('true', 'True').replace('false', 'False').replace('null', 'None')
                                try:
                                    data_dict = ast.literal_eval(json_v)
                                except:
                                    # Try real JSON
                                    try:
                                        data_dict = json.loads(v_strip)
                                    except:
                                        data_dict = None
                    except Exception as e:
                        # Final attempt with JSON if AST failed
                        import json
                        try:
                            data_dict = json.loads(v_strip)
                        except:
                            return UncertaintyLevel(Tolerance.ANYTHING), value, f"AST and JSON parsing failed: {e}"

            if data_dict is None:
                return UncertaintyLevel(Tolerance.ANYTHING), value, "Value not recognized as dict or constructor call"

            # 2. Résolution récursive des champs
            try:
                hints = resolve_struct_hints(model_cls)
                converted_kwargs = {}
                
                # On itère sur les champs du modèle (Pydantic v2)
                for field_name, field_info in model_cls.model_fields.items():
                    if field_name not in data_dict:
                        continue
                        
                    raw_val = data_dict[field_name]
                    expected_type = hints.get(field_name, field_info.annotation)
                    
                    if expected_type is None:
                        converted_kwargs[field_name] = raw_val
                        continue

                    guarded_type = TypeResolver.resolve(expected_type)
                    attempt_result = guarded_type.attempt(raw_val)
                    if not attempt_result.success:
                        return UncertaintyLevel(Tolerance.ANYTHING), value, f"Field '{field_name}': {attempt_result.error_message}"
                    
                    # We MUST use the native data for Pydantic constructor to avoid validation errors
                    converted_kwargs[field_name] = attempt_result.data

                # 3. Instanciation du modèle et unwrap
                instance = model_cls(**converted_kwargs)
                native_instance = cls._recursive_unwrap(instance)
                return UncertaintyLevel(Tolerance.PRECISE), native_instance, None

            except Exception as e:
                return UncertaintyLevel(Tolerance.ANYTHING), value, str(e)
    GuardedPydanticModel._native_class = model_cls
    _PYDANTIC_GUARDED_CACHE[model_cls] = GuardedPydanticModel

    return GuardedPydanticModel