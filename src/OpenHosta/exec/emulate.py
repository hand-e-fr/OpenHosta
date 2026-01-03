from __future__ import annotations

from typing import Any, Optional

import os
import time
import asyncio

from ..core.inspection import get_caller_frame, get_hosta_inspection
from ..core.config import config
from ..pipelines import OneTurnConversationPipeline
from ..core.errors import RateLimitError

def emulate(
        *,
        pipeline: Optional[OneTurnConversationPipeline] = config.DefaultPipeline,
        force_llm_args: Optional[dict] = {},
        ) -> Any:
    """
    Emulates a function's behavior using a language model.

    This function uses a language model to emulate the behavior of a Python function
    based on its signature, docstring, and context.
    
    Args:
        - pipeline (Optional[OneTurnConversationPipeline]): The pipeline used for emulation. If None, uses the default one.
        - force_llm_args: Additional keyword arguments to pass to the language model.
    
    Returns:
        - Any: The emulated function's return value, processed by the model and optionally modified by post_callback.
    """
    # You can retrive this frame using get_last_frame(your_emulated_function) in interactive mode
    frame = get_caller_frame()

    # Get everything about the function you are emulating
    inspection = get_hosta_inspection(frame)
    
    # Convert the inspection to a prompt
    messages = pipeline.push(inspection)
    
    response_dict = inspection.model.api_call(messages, inspection.force_llm_args | force_llm_args)
        
    # Convert the model response to a python object according to expected types
    response_data = pipeline.pull(inspection, response_dict)
    
    return response_data


async def emulate_async(
        *,
        pipeline: Optional[OneTurnConversationPipeline] = config.DefaultPipeline,
        force_llm_args: Optional[dict] = {},
        ) -> Any:
    """
    Emulates a function's behavior using a language model.

    This function uses a language model to emulate the behavior of a Python function
    based on its signature, docstring, and context.
    
    Args:
        - pipeline (Optional[OneTurnConversationPipeline]): The pipeline used for emulation. If None, uses the default one.
        - force_llm_args: Additional keyword arguments to pass to the language model.
    
    Returns:
        - Any: The emulated function's return value, processed by the model and optionally modified by post_callback.
    """
    # You can retrive this frame using get_last_frame(your_emulated_function) in interactive mode
    frame = get_caller_frame()

    # Get everything about the function you are emulating
    inspection = get_hosta_inspection(frame)
    
    # Convert the inspection to a prompt
    messages = pipeline.push(inspection)
    
    # This is the api call to the model, nothing more. Easy to debug and test.
    response_dict = await inspection.model.api_call_async(messages, inspection.force_llm_args | force_llm_args)
        
    # Convert the model response to a python object according to expected types
    response_data = pipeline.pull(inspection, response_dict)
    
    return response_data

from ..core.uncertainty import safe
import math

def emulate_iterator(
    pipeline : OneTurnConversationPipeline = config.DefaultPipeline,
    max_generation = 100,
    min_probability = 1e-8,
    assistant_thinking_string = "",
    force_llm_args: Optional[dict] = {}):

    # You can retrive this frame using get_last_frame(your_emulated_function) in interactive mode
    frame = get_caller_frame()

    # Get everything about the function you are emulating
    inspection = get_hosta_inspection(frame)

    def _iterator():
        
        ## TODO: top_k = 1 pour génération avec le toplogprob n°1
        ## Check for Unertainty error. if raised, continue 
        ## - Yield avec (cumulated_prob, answer)
        ## - split à chaque fois qu'il y a des logprobes > average logprob
        ## - tri des branchements par proba
        ## - génération de la branche avec la plus haute probabilité (ajout dans messages pour assistant)
        ## !! si top_logprob[20] > average_logprob alors il faut raise un erreur qui indique que la génération est incomplete. Il faut ajouter une catégorie.
        ## !! que faut il faire si le toplogprob n+1 est un substring d'un toplogprob [0..n] ? => générer la branche complete et regarder si le segement suivant (jusqu'au branchage suivant) est est identique en str. si oui: merge de la proba avec le précédent, sinon branche accepté 
        
        ## TODO: test si les prob sont similaires lorsque l'ordre des catégories est inversé
        ## 
        
        with safe(acceptable_cumulated_uncertainty=100) as safe_context:
            # Convert the inspection to a prompt
            messages = pipeline.push(inspection)
            messages.append({"role":"assistant", "content":[]})
            response_dict = inspection.model.api_call(messages, inspection.force_llm_args | force_llm_args)
            response_data = pipeline.pull(inspection, response_dict)
            yield response_data
            
            response_logprobs = inspection.logs["llm_api_response"]["choices"][0]["logprobs"]["content"]
            
            vocabulary_size = 200000
            path = "'"
            for i, token_data in enumerate(response_logprobs):
                
                top_logprobs = token_data.get("top_logprobs", [])
                likely_alternatives = [
                    p for p in top_logprobs
                    if p.get('logprob', -float('inf')) > math.log(1 / vocabulary_size)
                ]

                print("I:", i, likely_alternatives)
                
                for token in likely_alternatives:
                    
                    print(token)
                    start = path + token["token"]
                    print(start)
                    messages[-1]["content"] = [{"type":"text", "text":assistant_thinking_string + start}]

                    response_dict = inspection.model.api_call(messages, inspection.force_llm_args | force_llm_args)
                    
                    # Most likely due to the fact that gpt-4.1 has very low probs for single letters tokens
                    answer = response_dict["choices"][0]["message"]["content"]
                    response_dict["choices"][0]["message"]["content"] = assistant_thinking_string + start + answer

                    # Convert the model response to a python object according to expected types
                    response_data = pipeline.pull(inspection, response_dict)
                    
                    print(safe_context.acceptable_cumulated_uncertainty)
                    
                    yield response_data
                    
                path += token_data['token']

    return _iterator()
