import ast
import types
import inspect
from typing import Any, Tuple, Callable

# Assurez-vous d'avoir importé GuardedPrimitive
from .primitives import GuardedPrimitive

class SemanticCode(GuardedPrimitive):
    """
    Code Python Exécutable.
    Prend une chaîne de caractères (définition de fonction), la compile,
    et retourne le pointeur vers la fonction compilée.
    """
    
    _type_en = "a valid python function definition (starting with 'def')"
    _type_py = "Callable"
    _type_json = {"type": "string", "description": "Python source code of a function"}

    def __new__(cls, value: Any, description: str = ""):
        # Comme pour SemanticRange, on retourne directement l'objet natif (la fonction)
        # car on ne peut pas hériter de 'function' en Python.
        result = cls.attempt(value, description)
        
        if not result.is_success:
            raise ValueError(
                f"Failed to generate executable code.\n"
                f"Input: {value}\n"
                f"Error: {result.error_message}"
            )
        
        # On retourne le pointeur de fonction (callable)
        return result.value

    @classmethod
    def _parse_native(cls, value: Any) -> Tuple[bool, Any]:
        # Si c'est déjà une fonction ou une méthode, c'est valide.
        if isinstance(value, (types.FunctionType, types.MethodType)) or callable(value):
            return True, value
        return False, None

    @classmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[bool, Any]:
        if not isinstance(value, str):
            return False, None

        # 1. Nettoyage du Markdown (```python ... ```)
        cleaned_code = value.strip()
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
        except SyntaxError:
            return False, None

        # 3. Compilation et Extraction du pointeur
        # ATTENTION : exec() exécute du code arbitraire.
        # Dans un contexte LLM contrôlé, c'est ce qu'on veut, mais c'est un risque de sécurité.
        try:
            local_scope = {}
            # On exécute le code dans un scope isolé
            exec(cleaned_code, {}, local_scope)
            
            # On cherche l'objet fonction créé dans le scope
            # On prend le dernier objet callable défini (convention)
            found_function = None
            for item in local_scope.values():
                if inspect.isfunction(item):
                    found_function = item
            
            if found_function:
                return True, found_function
                
        except Exception:
            pass

        return False, None