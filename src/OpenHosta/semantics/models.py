# src/OpenHosta/semantics/models.py

import json
from typing import Any, Dict, Type, Optional, ClassVar, Union
from ..guarded.resolver import TypeResolver

# --- GESTION DE LA DÉPENDANCE PYDANTIC ---
try:
    from pydantic import BaseModel, ConfigDict, ValidationError
    HAS_PYDANTIC = True
    
    # Configuration de base pour accepter nos SemanticTypes
    # qui ne sont pas des types standards Pydantic
    BASE_CONFIG = ConfigDict(arbitrary_types_allowed=True)
    
except ImportError:
    HAS_PYDANTIC = False
    # Fallback : Classes "Dummy" pour éviter les crashs si Pydantic est absent
    class BaseModel:
        def model_dump(self): return self.__dict__
    class ConfigDict:
        def __init__(self, **kwargs): pass
    BASE_CONFIG = {}


class SemanticModel(BaseModel):
    """
    Classe de base pour les structures de données sémantiques.
    
    Mode d'emploi :
    1. Définissez vos champs avec des annotations de type.
    2. Instanciez avec des arguments nommés (validation) OU une phrase (extraction).
    
    Exemple:
        class User(SemanticModel):
            name: str
            age: SemanticInt
            
        # Extraction automatique
        u = User("Je m'appelle Alice et j'ai 30 ans")
    """
    
    if HAS_PYDANTIC:
        model_config = BASE_CONFIG

    def __init__(self, *args, **kwargs):
        """
        Constructeur intelligent.
        - __init__(raw_text="...") -> Extraction LLM
        - __init__(name="A", age=10) -> Validation standard
        """
        
        # 1. Cas "Extraction depuis texte brut"
        # L'utilisateur passe un seul argument positionnel string
        # ex: User("Alice, 30 ans")
        if args and isinstance(args[0], str) and len(args) == 1:
            raw_text = args[0]
            extracted_data = self._extract_from_text(raw_text)
            # On fusionne avec les kwargs éventuels (qui ont la priorité)
            kwargs = {**extracted_data, **kwargs}
            args = ()

        # 2. Cas "Extraction depuis kwargs" (ex: raw_text="...")
        elif "raw_text" in kwargs and len(kwargs) == 1:
            raw_text = kwargs.pop("raw_text")
            extracted_data = self._extract_from_text(raw_text)
            kwargs = extracted_data

        # 3. Initialisation & Validation des champs
        if HAS_PYDANTIC:
            # Pydantic va itérer sur les champs.
            # Si un champ est un SemanticType, sa méthode __get_pydantic_core_schema__
            # sera appelée par Pydantic pour gérer le parsing individuel.
            super().__init__(*args, **kwargs)
        else:
            # Fallback manuel si pas de Pydantic
            self._manual_init(kwargs)

    def _manual_init(self, data: Dict[str, Any]):
        """Simulation basique de Pydantic pour les utilisateurs sans la lib."""
        annotations = getattr(self, '__annotations__', {})
        
        for name, target_type in annotations.items():
            # Résolution du type sémantique (int -> SemanticInt)
            ResolvedClass = TypeResolver.resolve(target_type)
            
            value = data.get(name)
            
            # Instanciation (Déclenche GuardedPrimitive.__new__ -> LLM si besoin)
            # Si value est None, cela dépendra de la tolérance du type (souvent fail)
            if value is not None:
                try:
                    setattr(self, name, ResolvedClass(value, description=f"Field {name}"))
                except ValueError as e:
                    raise ValueError(f"Validation error for field '{name}': {e}")
            else:
                # Gestion très basique des optionnels manquants
                setattr(self, name, None)

    @classmethod
    def _extract_from_text(cls, text: str) -> Dict[str, Any]:
        """
        Appelle le moteur pour transformer du texte non structuré
        en dictionnaire correspondant aux champs du modèle.
        """
        # 1. Construction du Schema JSON cible
        # On demande au LLM : "Remplis ce JSON"
        target_schema = cls._generate_extraction_schema()
        
        # 2. Appel au moteur (engine.py)
        # On utilise une classe virtuelle pour porter la config JSON
        class ExtractionTarget:
            _type_en = f"a structured object matching this description: {cls.__doc__ or 'data object'}"
            _type_py = cls.__name__
            _type_json = target_schema
            
        # iterate_cast_type va utiliser le mode JSON pour extraire la donnée
        iterator = iterate_cast_type(
            value=text,
            target_cls=ExtractionTarget,
            user_desc="Extract information into the correct fields."
        )
        
        # 3. Récupération du meilleur candidat
        # Le moteur renvoie une string JSON, il faut la parser
        for candidate_json_str, uncertainty in iterator:
            try:
                data = json.loads(candidate_json_str)
                if isinstance(data, dict):
                    return data
            except json.JSONDecodeError:
                continue
                
        raise ValueError(f"Failed to extract meaningful data for {cls.__name__} from text.")

    @classmethod
    def _generate_extraction_schema(cls) -> Dict[str, Any]:
        """
        Génère un schéma JSON Schema (Draft 7) décrivant le modèle.
        Utilisé pour guider le LLM lors de l'extraction globale.
        """
        if HAS_PYDANTIC:
            # Pydantic sait déjà très bien faire ça
            return cls.model_json_schema()
        
        # Génération manuelle (Fallback)
        properties = {}
        required = []
        annotations = getattr(cls, '__annotations__', {})
        
        for name, py_type in annotations.items():
            resolved = TypeResolver.resolve(py_type)
            # On récupère le _type_json défini dans SemanticInt, SemanticStr...
            field_schema = getattr(resolved, '_type_json', {"type": "string"})
            properties[name] = field_schema
            required.append(name) # Par défaut tout est requis en mode manuel
            
        return {
            "type": "object",
            "properties": properties,
            "required": required,
            "additionalProperties": False
        }

    # --- Méthode de validation sémantique croisée (Hook) ---
    def validate_coherence(self):
        """
        À surcharger par l'utilisateur.
        Appelée après l'instanciation pour valider la logique entre les champs.
        Ex: Vérifier que 'salary' est cohérent avec 'job_title'.
        """
        pass