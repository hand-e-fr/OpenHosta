from __future__ import annotations
from ..utils.import_handler import is_pydantic_available

if is_pydantic_available:
    from pydantic import BaseModel # imported by other modules
    import inspect
    import pydantic
    from pydantic import Field
    from pydantic.fields import FieldInfo

    # --- Étape 1 : Générer dynamiquement la liste des arguments de Field ---

    def get_pydantic_field_kwargs() -> tuple:
        """
        Inspecte la signature de pydantic.Field pour en extraire
        tous les arguments possibles, en excluant ceux que nous traitons déjà
        spécialement ('default', 'default_factory').
        """
        # Récupère la signature de la fonction Field
        field_signature = inspect.signature(Field)
        
        # Récupère les noms de tous les paramètres
        all_params = field_signature.parameters.keys()
        
        # Filtre pour exclure ceux gérés séparément et retourne un tuple
        kwargs_to_check = [
            p for p in all_params if p not in ('default', 'default_factory')
        ]
        
        return tuple(kwargs_to_check)

    PYDANTIC_FIELD_KWARGS_AUTO = get_pydantic_field_kwargs()
    
    def reconstruct_pydantic_class_string_auto(cls: type[pydantic.BaseModel]) -> str:
        """
        Reconstruit la définition d'une classe Pydantic en une string
        en utilisant une liste d'arguments de Field() générée dynamiquement.
        """
        lines = []

        # 1. Définition de la classe
        base_classes = ', '.join(b.__name__ for b in cls.__bases__)
        lines.append(f"class {cls.__name__}({base_classes}):")

        # 2. Ajout du docstring
        if cls.__doc__:
            docstring = inspect.cleandoc(cls.__doc__)
            lines.append(f'    """\n    {docstring}\n    """')
            lines.append("")

        # 3. Itération sur les champs du modèle
        if not cls.model_fields:
            lines.append("    pass")
        else:
            for name, field_info in cls.model_fields.items():
                type_name = getattr(field_info.annotation, '__name__', str(field_info.annotation))
                field_args = []

                # A. Traitement du premier argument
                if field_info.default_factory is not None:
                    factory_name = getattr(field_info.default_factory, '__name__', '...')
                    field_args.append(f"default_factory={factory_name}")
                elif field_info.is_required():
                    field_args.append("...")
                else:
                    field_args.append(repr(field_info.default))

                # B. Traitement des arguments mots-clés (en utilisant la liste dynamique)
                for arg_name in PYDANTIC_FIELD_KWARGS_AUTO:
                    value = getattr(field_info, arg_name, None)

                    if value is not None:
                        field_args.append(f"{arg_name}={repr(value)}")
                
                field_str = f"Field({', '.join(field_args)})"
                lines.append(f"    {name}: {type_name} = {field_str}")

        return "\n".join(lines)


else:
    # If Pydantic is not available, define a dummy function that raises an error
    
    class BaseModel:
        """ Placeholder if Pydantic is not available. """
        pass 
    
    def reconstruct_pydantic_class_string_auto(cls: type) -> str:
        """
        Placeholder function if Pydantic is not available.
        """
        # See implementation above is Pydantic is available
        raise ImportError("Pydantic is not available. You should not call this function.")
    