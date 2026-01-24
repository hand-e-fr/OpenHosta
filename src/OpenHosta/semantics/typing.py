

# ==============================================================================
# 6. SEMANTIC LITERAL (Valeurs Constantes)
# ==============================================================================

def create_semantic_literal(literals: Tuple[Any]) -> Type[GuardedPrimitive]:
    """Gère typing.Literal['A', 'B']"""
    
    class GuardedLiteral(GuardedPrimitive):
        _allowed = literals
        _type_en = f"specifically one of: {literals}"
        _type_py = Literal[literals]
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

    GuardedLiteral.__name__ = f"Literal_{len(literals)}"
    return GuardedLiteral