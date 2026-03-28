import ast
import types
import inspect
from typing import Any, Tuple, Callable, Optional

# Assurez-vous d'avoir importé GuardedPrimitive
from .primitives import GuardedPrimitive, UncertaintyLevel, Tolerance, ProxyWrapper

class GuardedCode(GuardedPrimitive, ProxyWrapper):
    # TODO: implement using scalars.py as example
    _type_en = "the complete Python source code of the function (starting with 'def'), NOT its string representation (like <function...>)"
    _type_py = Callable
    _type_json = {"type": "string", "description": "Python source code of a function, do NOT output <function...> representations"}
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
            start_idx = -1
            end_idx = -1
            for i, line in enumerate(lines):
                if line.strip().startswith("```"):
                    if start_idx == -1:
                        start_idx = i
                    else:
                        end_idx = i
                        break
            
            if start_idx != -1 and end_idx != -1:
                # We found a code block, extract it
                cleaned_code = "\n".join(lines[start_idx + 1 : end_idx])

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
            # On exécute le code dans le scope global pour que les annotations
            # soient correctement résolues par Python lors de la définition.
            # TODO: better sandboxing
            exec(cleaned_code, local_scope)
            
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
            return UncertaintyLevel(Tolerance.ANYTHING), value, str(e)

def guarded_callable(*args):
    """
    Creates a dynamic subclass of GuardedCode.
    Injects the provided argument and return types into the `local_scope`
    so that `exec()` can access them when executing the generated string.
    """
    class GuardedCallableWrapper(GuardedCode):
        _type_knowledge = {"local_scope": {}}
        
    for arg in args:
        if arg is None or arg is type(None):
            continue
            
        # Extract the unified _native_class from the Guarded wrapper if available
        # fallback to _type_py or the primitive itself.
        native_type = getattr(arg, "_native_class", getattr(arg, "_type_py", arg))
            
        if hasattr(native_type, "__name__"):
            name = native_type.__name__
            GuardedCallableWrapper._type_knowledge["local_scope"][name] = native_type
            
    return GuardedCallableWrapper
