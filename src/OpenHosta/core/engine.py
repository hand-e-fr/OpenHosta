import json
import logging
import os
import math
import functools
import random
from typing import Any, Generator, Tuple, Dict, List, Optional
from .meta_prompt import MetaPrompt

# Logger pour ce module
logger = logging.getLogger(__name__)


def get_model():
    """Get the default model from config. Returns None if unavailable."""
    try:
        from .config import config
        return config.DefaultModel
    except Exception:
        return None

# Stratégie 1 : Extraction Textuelle Libre
PROMPT_CAST_TEXT = MetaPrompt("""\
You are a precise data extraction and conversion engine.
Your goal is to extract information from the input and convert it into the requested format strictly.

The target type is: {{ type_desc }}.

Input Data: '{{ value }}'
Context: {{ user_desc }}

Task: Convert or extract the data. Return ONLY the value, no explanation.
""")

# Stratégie 2 : Extraction JSON Schema
PROMPT_CAST_JSON = MetaPrompt("""\
You are a precise data extraction and conversion engine.
Your goal is to extract information from the input and convert it into the requested format strictly.

Output valid JSON matching this schema: {{ json_schema }}
Context: {{ user_desc }}

Input Data: '{{ value }}'

Task: Extract the value matching the schema. Return ONLY the JSON object.
""")

# Stratégie 3 : Vérification d'égalité (Hybride)
PROMPT_EQUALITY_CHECK = MetaPrompt("""\
Context: {{ context }}
Value A: '{{ value_a }}'
Value B: '{{ value_b }}'

Are Value A and Value B semantically equivalent or synonyms in this context?
Ignore minor typos or capitalization.

Answer strictly with YES or NO.
""")

def iterate_cast_type(
    value: Any, 
    target_cls: Any, 
    user_desc: str = ""
) -> Generator[Tuple[str, float], None, None]:
    """
    Orchestre la conversion en utilisant MetaPrompt et Model.
    """
    model = get_model()
    
    # 1. Préparation du Prompt via MetaPrompt
    json_schema = getattr(target_cls, '_type_json', None)
    type_desc = getattr(target_cls, '_type_en', 'unknown type')
    
    prompt_content = ""
    llm_args = {"temperature": 0.0, "logprobs": True}

    if json_schema:
        # STRATÉGIE JSON
        prompt_content = PROMPT_CAST_JSON.render(
            json_schema=json.dumps(json_schema),
            value=value,
            user_desc=user_desc
        )
        llm_args["response_format"] = "json_object"
    else:
        # STRATÉGIE TEXTE
        prompt_content = PROMPT_CAST_TEXT.render(
            type_desc=type_desc,
            value=value,
            user_desc=user_desc
        )

    # 2. Exécution via Model.api_call
    try:
        messages = [{"role": "user", "content": prompt_content}]
        
        response = model.api_call(messages, llm_args=llm_args)
        
        content = _clean_response(model.get_response_content(response))
        
        # Récupération spécifique des logprobs pour l'incertitude
        logprobs = None
        if hasattr(model, "get_logprobs"):
            logprobs = model.get_logprobs(response)
        
        uncertainty = _calculate_uncertainty(logprobs)
        
        yield content, uncertainty

    except Exception as e:
        logger.error(f"Engine execution failed: {e}")
        yield "", 1.0


def _clean_response(text: str) -> str:
    """Nettoie les blocs Markdown (```json ... ```)."""
    if not text: return ""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split('\n')
        if len(lines) >= 2:
            return "\n".join(lines[1:-1])
    return text


def _calculate_uncertainty(logprobs_obj) -> float:
    """
    Estime l'incertitude (0.0 = Sûr, 1.0 = Perdu).
    """
    if not logprobs_obj or not logprobs_obj.content:
        return 0.5

    total_logprob = 0.0
    count = 0
    
    for token_data in logprobs_obj.content:
        # On ignore les tokens de syntaxe JSON pure
        if token_data.token in ['{', '}', ':', '"', '\n']:
            continue
        total_logprob += token_data.logprob
        count += 1
        
    if count == 0: return 0.0
    
    avg_logprob = total_logprob / count
    probability = math.exp(avg_logprob)
    
    return 1.0 - probability


# ==============================================================================
# 5. EQUALITY & EMBEDDINGS
# ==============================================================================

@functools.lru_cache(maxsize=1024)
def get_embedding(text: str) -> List[float]:
    """
    Génère un vecteur pour le texte donné.
    Utilise la méthode embedding_api_call du modèle configuré.
    """
    model = get_model()
    
    if model is not None:
        try:
            text_cleaned = text.replace("\n", " ")
            embeddings = model.embedding_api_call([text_cleaned])
            if embeddings and len(embeddings) > 0:
                return embeddings[0]
        except Exception as e:
            logger.warning(f"Embedding API call failed: {e}, using mock fallback")
    
    # Mock fallback - deterministic based on text
    random.seed(hash(text) % (2**32))
    return [random.random() for _ in range(1536)]


def check_equality_llm(value_a: str, value_b: str, context: str, threshold: float) -> bool:
    """
    Vérification sémantique fine via LLM.
    """
    model = get_model()
    if not model:
        return value_a.lower() == value_b.lower()

    # Utilisation du MetaPrompt
    prompt_content = PROMPT_EQUALITY_CHECK.render(
        context=context,
        value_a=value_a,
        value_b=value_b
    )

    try:
        messages = [{"role": "user", "content": prompt_content}]
        response = model.api_call(
            messages, 
            llm_args={"max_tokens": 5, "temperature": 0.0}
        )
        answer = model.get_response_content(response).strip().upper()
        return "YES" in answer
    except Exception:
        return False


# ==============================================================================
# 6. LABEL SYNTHESIS (Pour SemanticSet clustering)
# ==============================================================================

PROMPT_SYNTHESIZE_LABEL = MetaPrompt("""\
Given these semantically related items:
{% for item in items %}- {{ item }}
{% endfor %}
{% if context %}Context: {{ context }}{% endif %}

Generate a single short label (2-4 words in the same language as the items) that represents the common concept or theme.
Return ONLY the label, nothing else.
""")


def synthesize_label(items: List[str], context: str = "") -> str:
    """
    Génère un label synthétique représentant le concept commun d'un groupe d'éléments.
    
    Args:
        items: Liste de strings représentant les éléments du cluster
        context: Description optionnelle du contexte (ex: "Tâche ménagère")
    
    Returns:
        Un label court représentant le concept commun (ex: "Nettoyage des sols")
    """
    # Cas trivial : un seul élément
    if len(items) == 1:
        return items[0]
    
    # Cas sans modèle : on retourne le premier élément
    model = get_model()
    if not model:
        logger.warning("Running in MOCK mode for synthesize_label.")
        return items[0]
    
    # Construction du prompt
    prompt_content = PROMPT_SYNTHESIZE_LABEL.render(
        items=items,
        context=context
    )
    
    try:
        messages = [{"role": "user", "content": prompt_content}]
        response = model.api_call(
            messages,
            llm_args={"max_tokens": 20, "temperature": 0.3}
        )
        label = model.get_response_content(response).strip()
        # Nettoyage des guillemets éventuels
        label = label.strip('"\'')
        return label if label else items[0]
    except Exception as e:
        logger.error(f"Label synthesis failed: {e}")
        return items[0]