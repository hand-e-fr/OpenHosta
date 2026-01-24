import json

from typing import Any, Tuple, Type, Dict, List, Union, Optional

from ..guarded.primitives import GuardedPrimitive
from ..guarded.scalars import GuardedUtf8 # Type par défaut

# ==============================================================================
# 1. SEMANTIC LIST (La Liste Intelligente)
# ==============================================================================

def create_semantic_list(inner_type: Type[GuardedPrimitive]) -> Type['SemanticList']:
    """
    Factory qui génère une classe de Liste typée sémantiquement.
    Ex: create_semantic_list(SemanticInt) -> Classe qui valide [1, 2, 3]
    """

    class ConcreteSemanticList(SemanticList):
        _inner_semantic_type = inner_type
        
        # --- Configuration Dynamique ---
        # Le LLM reçoit une description récursive : "une liste de [description de l'entier]"
        _type_en = f"a list of {inner_type._type_en}s"
        _type_py = f"List[{inner_type._type_py}]"
        
        # Schema JSON pour forcer la structure ARRAY
        _type_json = {
            "type": "array",
            "items": inner_type._type_json
        }

        @classmethod
        def _parse_native(cls, value: Any) -> Tuple[bool, Any]:
            # Pour être valide nativement, ça doit être un itérable (list, tuple)
            if not isinstance(value, (list, tuple)):
                return False, None
            
            validated_items = []
            for item in value:
                # Validation récursive : on demande au type interne de vérifier l'item
                # Note: On utilise _parse_native du type enfant pour éviter de re-déclencher le LLM
                # sur chaque item si la liste est déjà partiellement propre.
                is_valid, val = inner_type._parse_native(item)
                
                if not is_valid:
                    # Si un seul item est invalide, la liste entière est rejetée "nativement"
                    # Cela forcera le pipeline à passer en mode Heuristique ou LLM global
                    return False, None
                
                validated_items.append(val)
                
            return True, validated_items

        def __init__(self, value: Any, description: str = ""):
            # value est ici la liste brute validée (ex: [1, 2, 3])
            # On transforme chaque élément en Instance Sémantique (ex: SemanticInt(1))
            # pour qu'il porte ses propres métadonnées.
            semantic_items = [self._inner_semantic_type(item) for item in value]
            super().__init__(semantic_items)
            self._description = description

    # Nommage pour le debug (ex: SemanticList_SemanticInt)
    ConcreteSemanticList.__name__ = f"SemanticList_{inner_type.__name__}"
    return ConcreteSemanticList


class SemanticList(list, GuardedPrimitive):
    """
    Classe de base pour les listes.
    Permet la syntaxe: MyList = SemanticList[SemanticInt]
    """
    
    # Par défaut (si utilisé sans crochets), c'est une liste de String
    _inner_semantic_type = GuardedUtf8
    
    _type_en = "a list of text items"
    _type_py = "List[str]"
    _type_json = {"type": "array", "items": {"type": "string"}}

    @classmethod
    def __class_getitem__(cls, item_type):
        """Intercepte SemanticList[Type]"""
        # Import local pour éviter cycle avec resolver.py
        from ..guarded.resolver import TypeResolver
        
        resolved_type = TypeResolver.resolve(item_type)
        return create_semantic_list(resolved_type)

    @classmethod
    def _parse_native(cls, value: Any) -> Tuple[bool, Any]:
        # Implémentation par défaut (List[str])
        if isinstance(value, list):
            return True, [str(v) for v in value]
        return False, None

    @classmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[bool, Any]:
        """Tente de parser une string JSON '[...]'."""
        if isinstance(value, str):
            value = value.strip()
            if value.startswith("[") and value.endswith("]"):
                try:
                    data = json.loads(value)
                    if isinstance(data, list):
                        # On repasse par parse_native pour valider le contenu typé
                        return cls._parse_native(data)
                except json.JSONDecodeError:
                    pass
        return False, None


# ==============================================================================
# 2. SEMANTIC DICT (Le Dictionnaire Flou)
# ==============================================================================

def create_semantic_dict(key_type: Type[GuardedPrimitive], val_type: Type[GuardedPrimitive]) -> Type['SemanticDict']:
    
    class ConcreteSemanticDict(SemanticDict):
        _key_semantic_type = key_type
        _val_semantic_type = val_type
        
        _type_en = f"a dictionary where keys are {key_type._type_en} and values are {val_type._type_en}"
        _type_py = f"Dict[{key_type._type_py}, {val_type._type_py}]"
        
        _type_json = {
            "type": "object",
            "additionalProperties": val_type._type_json
        }

        @classmethod
        def _parse_native(cls, value: Any) -> Tuple[bool, Any]:
            if not isinstance(value, dict):
                return False, None
            
            validated_dict = {}
            for k, v in value.items():
                # Validation Clé
                k_ok, k_val = key_type._parse_native(k)
                if not k_ok: return False, None
                
                # Validation Valeur
                v_ok, v_val = val_type._parse_native(v)
                if not v_ok: return False, None
                
                validated_dict[k_val] = v_val
                
            return True, validated_dict

        def __init__(self, value: Any, description: str = ""):
            # Instanciation sémantique des clés et valeurs
            # Note: On stocke des objets sémantiques. 
            # Si key_type est SemanticType, attention au hashage !
            # SemanticDict gère ça via sa propre logique de lookup.
            super().__init__()
            for k, v in value.items():
                sem_k = self._key_semantic_type(k)
                sem_v = self._val_semantic_type(v)
                self[sem_k] = sem_v
            
            self._description = description

    ConcreteSemanticDict.__name__ = f"SemanticDict_{key_type.__name__}_{val_type.__name__}"
    return ConcreteSemanticDict


class SemanticDict(dict, GuardedPrimitive):
    """
    Dictionnaire sémantique.
    Syntaxe: SemanticDict[GuardedUtf8, SemanticInt]
    
    Feature Clé: Recherche sémantique.
    Si d["cle"] échoue, on cherche une clé k telle que k == "cle" (égalité sémantique).
    """
    
    _key_semantic_type = GuardedUtf8
    _val_semantic_type = GuardedUtf8
    
    _type_en = "a dictionary (key-value pairs)"
    _type_py = "Dict[str, str]"
    _type_json = {"type": "object"}

    @classmethod
    def __class_getitem__(cls, params):
        from ..guarded.resolver import TypeResolver
        
        # Gestion SemanticDict[KeyType, ValType] vs SemanticDict[ValType] (implied Str key)
        if not isinstance(params, tuple):
            params = (GuardedUtf8, params)
            
        K, V = params
        return create_semantic_dict(TypeResolver.resolve(K), TypeResolver.resolve(V))

    @classmethod
    def _parse_native(cls, value: Any) -> Tuple[bool, Any]:
        if isinstance(value, dict):
            return True, value
        return False, None

    @classmethod
    def _parse_heuristic(cls, value: Any) -> Tuple[bool, Any]:
        """Tente de parser du JSON '{...}'."""
        if isinstance(value, str):
            value = value.strip()
            if value.startswith("{") and value.endswith("}"):
                try:
                    data = json.loads(value)
                    if isinstance(data, dict):
                        return cls._parse_native(data)
                except json.JSONDecodeError:
                    pass
        return False, None

    def __getitem__(self, key):
        """
        Recherche intelligente (Semantic Lookup).
        1. Essaie le hash exact (O(1)).
        2. Si échec, itère sur les clés pour trouver une égalité sémantique (O(N)).
        """
        # 1. Tentative Standard (Rapide)
        try:
            return super().__getitem__(key)
        except (KeyError, TypeError):
            pass

        # 2. Tentative Sémantique (Lente mais puissante)
        # On ne le fait que si la clé passée est compatible (str ou SemanticType)
        found_key = None
        
        # On parcourt toutes les clés existantes
        for existing_key in self.keys():
            # L'opérateur == déclenche la logique hybride (Vecteurs ou LLM)
            # définie dans SemanticType.__eq__
            if existing_key == key:
                found_key = existing_key
                break
        
        if found_key is not None:
            return super().__getitem__(found_key)
            
        raise KeyError(f"Key '{key}' not found (even semantically).")
    
# ==============================================================================
# 3. SEMANTIC SET (L'Ensemble Unique avec Clustering Sémantique)
# ==============================================================================

class SemanticSet:
    """
    Ensemble sémantique avec détection de doublons par similarité vectorielle.
    
    Contrairement à un set Python natif, SemanticSet:
    - Détecte les doublons SÉMANTIQUES (pas juste les doublons exacts)
    - Regroupe les éléments similaires en "clusters"
    - Génère automatiquement un label synthétique pour chaque cluster
    
    Usage:
        tasks = SemanticSet(type=SemanticType(str, "Tâche ménagère"))
        tasks.add("Laver le sol")
        tasks.add("Passer la serpillière")  # Détecté comme doublon sémantique
        print(tasks)  # {"Nettoyage des sols"}
    """
    
    def __init__(self, type=None, tolerance: float = 0.15):
        """
        Args:
            type: SemanticType définissant le type des éléments (optionnel).
                  Ex: SemanticType(str, "Tâche ménagère")
            tolerance: Seuil de similarité (0.0 = strict, 1.0 = tout accepter).
                       Par défaut 0.15 (FLEXIBLE).
        """
        self._inner_type = type
        self._tolerance = tolerance
        # Clusters = liste de dicts {'label': str, 'members': list, 'centroid': vector}
        self._clusters: List[Dict[str, Any]] = []
    
    @classmethod
    def __class_getitem__(cls, item_type):
        """Support de la syntaxe SemanticSet[Type] pour rétrocompatibilité."""
        from ..guarded.resolver import TypeResolver
        return create_semantic_set(TypeResolver.resolve(item_type))
    
    def _wrap_item(self, item: Any) -> Any:
        """Convertit un item brut en type sémantique si un type est défini."""
        if self._inner_type is not None:
            # If _inner_type is a class, use it directly
            if isinstance(self._inner_type, type):
                # Check if item is already an instance of this type
                if isinstance(item, self._inner_type):
                    return item
                # Otherwise instantiate
                return self._inner_type(item)
            else:
                # _inner_type is an instance - use its class
                if isinstance(item, type(self._inner_type)):
                    return item
                return type(self._inner_type)(item)
        return item
    
    def _get_vector(self, item: Any) -> List[float]:
        """Récupère le vecteur d'embedding d'un item, incluant le contexte sémantique."""
        from ..core.engine import get_embedding
        
        # Si l'item a déjà un vecteur (SemanticType), on l'utilise
        if hasattr(item, 'vector'):
            return item.vector
        
        # Build text with context if available
        text = str(item)
        
        # Add semantic context from the type if available
        if self._inner_type is not None:
            context = None
            if isinstance(self._inner_type, type):
                context = getattr(self._inner_type, '_description_default', None)
            else:
                context = getattr(self._inner_type, '_description', None)
            
            if context:
                # Prepend context to help disambiguate (e.g., "Fruit: orange" vs "Couleur: orange")
                text = f"{context}: {text}"
        
        return get_embedding(text)
    
    def _cosine_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        """Calcule la similarité cosinus entre deux vecteurs."""
        import math
        
        if not vec_a or not vec_b:
            return 0.0
            
        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot_product / (norm_a * norm_b)
    
    def _tolerance_to_threshold(self, tolerance: float) -> float:
        """Convertit la tolérance utilisateur en seuil de similarité."""
        # Get MIN_SIM from model (model-specific value)
        from ..defaults import config
        MIN_SIM = getattr(config.DefaultModel, 'embedding_similarity_min', 0.30)
        MAX_SIM = 0.99
        # Tolérance 0.0 -> Seuil MAX_SIM (très strict)
        # Tolérance 1.0 -> Seuil MIN_SIM (très permissif)
        return MAX_SIM - (tolerance * (MAX_SIM - MIN_SIM))
    
    def _find_matching_cluster(self, item_vector: List[float]) -> Optional[int]:
        """
        Trouve le cluster le plus proche si la similarité dépasse le seuil.
        Retourne l'index du cluster ou None.
        """
        threshold = self._tolerance_to_threshold(self._tolerance)
        best_idx = None
        best_sim = 0.0
        
        for idx, cluster in enumerate(self._clusters):
            # Comparer avec le centroïde du cluster
            if 'centroid' in cluster and cluster['centroid']:
                sim = self._cosine_similarity(item_vector, cluster['centroid'])
                if sim >= threshold and sim > best_sim:
                    best_sim = sim
                    best_idx = idx
        
        return best_idx
    
    def _update_centroid(self, cluster: Dict[str, Any]) -> None:
        """Recalcule le centroïde d'un cluster (moyenne des vecteurs)."""
        vectors = [self._get_vector(m) for m in cluster['members']]
        if not vectors or not vectors[0]:
            return
            
        dim = len(vectors[0])
        centroid = [0.0] * dim
        
        for vec in vectors:
            for i, v in enumerate(vec):
                centroid[i] += v
        
        n = len(vectors)
        cluster['centroid'] = [c / n for c in centroid]
    
    def _synthesize_label(self, members: List[Any]) -> str:
        """Génère un label synthétique représentant le concept commun."""
        from ..core.engine import synthesize_label
        
        member_strs = [str(m) for m in members]
        context = ""
        if self._inner_type is not None and hasattr(self._inner_type, '_description'):
            context = self._inner_type._description
        
        return synthesize_label(member_strs, context)
    
    def add(self, item: Any) -> None:
        """
        Ajoute un élément au set.
        
        Si un élément sémantiquement similaire existe déjà, l'item rejoint
        le cluster existant et le label est recalculé.
        Sinon, un nouveau cluster est créé.
        """
        # 1. Convertir en type sémantique si nécessaire
        semantic_item = self._wrap_item(item)
        
        # 2. Calculer le vecteur de l'item
        item_vector = self._get_vector(semantic_item)
        
        # 3. Chercher un cluster existant
        matching_idx = self._find_matching_cluster(item_vector)
        
        if matching_idx is not None:
            # Ajouter au cluster existant
            cluster = self._clusters[matching_idx]
            cluster['members'].append(semantic_item)
            self._update_centroid(cluster)
            # Recalculer le label
            cluster['label'] = self._synthesize_label(cluster['members'])
        else:
            # Créer un nouveau cluster
            new_cluster = {
                'label': str(semantic_item),
                'members': [semantic_item],
                'centroid': item_vector
            }
            self._clusters.append(new_cluster)
    
    def __contains__(self, item: Any) -> bool:
        """Vérifie si un item (ou similaire) est dans le set."""
        item_vector = self._get_vector(item)
        return self._find_matching_cluster(item_vector) is not None
    
    def __len__(self) -> int:
        """Retourne le nombre de clusters (concepts uniques)."""
        return len(self._clusters)
    
    def __iter__(self):
        """Itère sur les labels des clusters."""
        for cluster in self._clusters:
            yield cluster['label']
    
    def __repr__(self) -> str:
        """Affiche le set avec les labels synthétisés."""
        labels = [cluster['label'] for cluster in self._clusters]
        return "{" + ", ".join(f'"{label}"' for label in labels) + "}"
    
    def members(self, label: str = None) -> List[Any]:
        """
        Retourne les membres.
        
        Args:
            label: Si spécifié, retourne les membres de ce cluster uniquement.
                   Sinon, retourne tous les membres de tous les clusters.
        """
        if label is not None:
            for cluster in self._clusters:
                if cluster['label'] == label:
                    return cluster['members']
            return []
        
        # Tous les membres
        all_members = []
        for cluster in self._clusters:
            all_members.extend(cluster['members'])
        return all_members
    
    def clusters(self) -> List[Dict[str, Any]]:
        """Retourne la liste des clusters avec leurs labels et membres."""
        return [
            {'label': c['label'], 'members': c['members']} 
            for c in self._clusters
        ]


# Factory pour la syntaxe SemanticSet[Type] (rétrocompatibilité)
def create_semantic_set(inner_type: Type[GuardedPrimitive]) -> Type['_LegacySemanticSet']:
    """Factory pour SemanticSet[Type] - Syntaxe bracket."""
    
    class _LegacySemanticSet(SemanticSet):
        """Version bracket de SemanticSet pour rétrocompatibilité."""
        
        def __init__(self, value: Any = None, description: str = ""):
            super().__init__(type=inner_type)
            if value is not None:
                # Si on passe une collection initiale
                if isinstance(value, (list, tuple, set, frozenset)):
                    for item in value:
                        self.add(item)
    
    _LegacySemanticSet.__name__ = f"SemanticSet_{inner_type.__name__}"
    return _LegacySemanticSet


# ==============================================================================
# 4. SEMANTIC TUPLE (Le Tuple Structuré)
# ==============================================================================

def create_semantic_tuple(item_types: List[Type[GuardedPrimitive]], variable_length: bool = False) -> Type['SemanticTuple']:
    """
    Gère Tuple[int, str] (Fixed) ET Tuple[int, ...] (Variable)
    """
    
    class ConcreteSemanticTuple(SemanticTuple):
        _item_types = item_types
        _is_variable = variable_length
        
        # Construction de la documentation dynamique
        if variable_length:
            _type_en = f"a tuple of variable length containing {item_types[0]._type_en}s"
            _type_py = f"Tuple[{item_types[0]._type_py}, ...]"
            _type_json = {"type": "array", "items": item_types[0]._type_json}
        else:
            names = [t._type_py for t in item_types]
            _type_en = f"a fixed tuple of elements: {', '.join(names)}"
            _type_py = f"Tuple[{', '.join(names)}]"
            _type_json = {
                "type": "array", 
                "prefixItems": [t._type_json for t in item_types],
                "minItems": len(item_types),
                "maxItems": len(item_types)
            }

        @classmethod
        def _parse_native(cls, value: Any) -> Tuple[bool, Any]:
            if not isinstance(value, (list, tuple)): return False, None
            
            # Cas Tuple Variable: Tuple[int, ...]
            if cls._is_variable:
                target_type = cls._item_types[0]
                validated = []
                for item in value:
                    ok, val = target_type._parse_native(item)
                    if not ok: return False, None
                    validated.append(val)
                return True, tuple(validated)
            
            # Cas Tuple Fixe: Tuple[int, str]
            if len(value) != len(cls._item_types): return False, None
            
            validated = []
            for item, target_type in zip(value, cls._item_types):
                ok, val = target_type._parse_native(item)
                if not ok: return False, None
                validated.append(val)
            return True, tuple(validated)

        def __init__(self, value: Any, description: str = ""):
            final_list = []
            if self._is_variable:
                 # Variable logic
                 target_t = self._item_types[0]
                 final_list = [target_t(v) for v in value]
            else:
                # Fixed logic
                for v, target_t in zip(value, self._item_types):
                    final_list.append(target_t(v))
            
            super().__init__(tuple(final_list)) # Init du tuple natif
            self._description = description

    ConcreteSemanticTuple.__name__ = f"SemanticTuple_Fixed" if not variable_length else f"SemanticTuple_Var_{item_types[0].__name__}"
    return ConcreteSemanticTuple

class SemanticTuple(tuple, GuardedPrimitive):
    _type_en = "a tuple"
    _type_py = "tuple"
    _type_json = {"type": "array"}
    
    @classmethod
    def _parse_native(cls, v): return (True, tuple(v)) if isinstance(v, (list, tuple)) else (False, None)
    
    @classmethod
    def _parse_heuristic(cls, v):
         if isinstance(v, str) and v.startswith("("):
            try:
                import ast
                val = ast.literal_eval(v)
                if isinstance(val, tuple): return cls._parse_native(val)
            except: pass
         return False, None