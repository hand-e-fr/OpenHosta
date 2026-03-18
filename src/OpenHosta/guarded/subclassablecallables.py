import ast
import types
import inspect
from typing import Any, Tuple, Callable, Optional

# Assurez-vous d'avoir importé GuardedPrimitive
from .primitives import GuardedPrimitive, UncertaintyLevel, Tolerance, ProxyWrapper

class GuardedCode(GuardedPrimitive, ProxyWrapper):
    # TODO: implement using scalars.py as example
    _type_en = "a valid python function definition (starting with 'def')"
    _type_py = Callable
    _type_json = {"type": "string", "description": "Python source code of a function"}
    _type_knowledge = {"local_scope": {}}

    @classmethod
    def _parse_native(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:
        # Si c'est déjà une fonction ou une méthode, c'est valide.
        if isinstance(value, (types.FunctionType, types.MethodType)) or callable(value):
            return UncertaintyLevel(Tolerance.STRICT), value, None
        return UncertaintyLevel(Tolerance.ANYTHING), value, None

    @classmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[UncertaintyLevel, Any, Optional[str]]:

        # If it is not a string, how could we convert a python object that is not callable into a callable ? 
        if not isinstance(value, str):
            return UncertaintyLevel(Tolerance.ANYTHING), value, "Not a string"

        # 1. Nettoyage du Markdown (```python ... ```)
        cleaned_code = value.strip()
        if not cleaned_code:
            return UncertaintyLevel(Tolerance.ANYTHING), value, "Empty source code"

        if "```" in cleaned_code:
            lines = cleaned_code.splitlines()
            # On retire la première ligne si c'est ```python et la dernière si c'est ```
            if lines[0].strip().startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip().startswith("```"):
                lines = lines[:-1]
            cleaned_code = "\n".join(lines)

        # 2. Vérification Syntaxique (AST)
        try:
            ast.parse(cleaned_code)
        except SyntaxError as e:
            return UncertaintyLevel(Tolerance.ANYTHING), value, f"Syntax error: {e}"

        # 3. Compilation et Extraction du pointeur
        # ATTENTION : exec() exécute du code arbitraire.
        # Dans un contexte LLM contrôlé, c'est ce qu'on veut, mais c'est un risque de sécurité.
        try:
            local_scope = cls._type_knowledge["local_scope"]
            # On exécute le code dans un scope isolé
            # TODO: better sandboxing
            exec(cleaned_code, {}, local_scope)
            
            # On cherche l'objet fonction créé dans le scope
            # On prend le dernier objet callable défini (convention)
            found_function = None
            for item in local_scope.values():
                if inspect.isfunction(item):
                    found_function = item
            
            if found_function:
                return UncertaintyLevel(Tolerance.TYPE_COMPLIANT), found_function, None
            else:
                return UncertaintyLevel(Tolerance.ANYTHING), value, "No function found after eval"

        except Exception as e:
            return UncertaintyLevel(Tolerance.ANYTHING), value, e
