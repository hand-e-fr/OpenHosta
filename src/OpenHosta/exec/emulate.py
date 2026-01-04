from __future__ import annotations

from typing import Any, List, Optional

import os
import math
import time
import asyncio

from ..core.inspection import Inspection, get_caller_frame, get_hosta_inspection
from ..core.base_model import ModelCapabilities, Model
from ..core.config import config

from ..pipelines import OneTurnConversationPipeline

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

def find_next_node(nodes:List, best_porba_found=0):

    nodes.sort(key=lambda n: n["selected_proportion"], reverse=True)
    # Nodes with Children that is empty list is a termination node
    candidates_nodes = [n for n in nodes if n["selected_proportion"] >= best_porba_found and n["children"] is None]         
    nodes_to_explore = [n for n in nodes if n["selected_proportion"] >= best_porba_found and n["children"] is not None and len(n["children"]) > 0]

    # print(f"Nodes to explore: {len(nodes_to_explore)}, Candidates: {len(candidates_nodes)}, Best porba: {best_porba_found}")

    if len(candidates_nodes) > 0:
        candidate_node = candidates_nodes[0]
        new_best_porba_found = candidate_node["selected_proportion"]
        # print(f"Candidates {len(candidates_nodes)} with new new_best_porba_found: {new_best_porba_found} and text: {candidate_node.get('text', '<empty_string>')}")
    else:
        candidate_node = None
        new_best_porba_found = best_porba_found
        # print("No candidate here. Give a chance to exploration...")
    
    if len(nodes_to_explore) == 0:
        if candidate_node is None:
            return None
        # print(f"Using candidate as there is no node to explore: {candidate_node.get('text', '<empty_string>')}, Porba: {candidate_node.get('selected_proportion', 0)}")
        return candidate_node
    else:
        # Recursively find the best node in the children of the best candidate
        for next_node in nodes_to_explore:
            best_children_node = find_next_node(
                next_node["children"], 
                best_porba_found=new_best_porba_found)
            
            if best_children_node is not None:
                # print(f"From: {next_node.get('text', '<empty_string>'):10s}, Node found: {best_children_node.get('text', '<empty_string>'):10s}, Proba: {best_children_node["selected_proportion"]}")
                return best_children_node
    
    if candidate_node is None:
        return None
    # print(f"Using candidate: {candidate_node.get('text', '<empty_string>')}, Porba: {candidate_node.get('selected_proportion', 0)}")
    return candidate_node
        

def travel_branches_from_node(inspection: Inspection, messages: List, min_probability=1e-4, force_llm_args = {}):
    
    model:Model = inspection.model
    model.capabilities |= {ModelCapabilities.LOGPROBS}
    branches = [
        {
            "token": "",
            "text": "",
            "step_probability": 1,
            "selected_proportion": 1,
            "above_threshold_branches": 1, 
            "logprob": 0.0, 
            "children":None
            }
    ]
        
    # Look for the most probable alternative with "children" is None (not yet explored) from the root
    next_node = {}
    while next_node is not None:            
        
        next_node = find_next_node(branches, best_porba_found=min_probability)
        # print(next_node)
        if next_node is not None:
            val = fill_nodes(
                inspection=inspection,
                messages=messages,
                current_node=next_node,
                min_probability=min_probability,
                force_llm_args=force_llm_args
                )
            if val is not None:
                yield val
                
    
def fill_nodes(
    inspection,
    messages,
    current_node,
    min_probability,
    force_llm_args
    ):

    result = None
    model:Model = inspection.model

    if current_node["children"] is not None:
        raise ValueError("Node already has children")
    else:
        current_node["children"] = []
    
        # Make sure we have an assistant message at the end    
        if messages[-1]["role"] != "assistant":
            messages.append({"role": "assistant", "content": current_node["text"]})
        else:
            messages[-1]["content"] = current_node["text"]
    
        response_dict = model.api_call(messages, inspection.force_llm_args | force_llm_args | {"logprobs": True, "top_logprobs": 20, "max_tokens": 10})    


        if not "logprobs" in response_dict["choices"][0]:
            # Most likely an empty answer: terminal node
            return current_node["text"], current_node["selected_proportion"], response_dict
        else:
            response_logprobs = response_dict["choices"][0]["logprobs"]["content"]
        
        # 2. Iterate through tokens to identify branching options
        max_depth_on_this_path = len(response_logprobs)
        above_threshold_branches = current_node["above_threshold_branches"]
        for depth, token_data in enumerate(response_logprobs):
            
            top_logprobs = token_data.get("top_logprobs", [])
            
            total_mass = sum(math.exp(t["logprob"]) for t in top_logprobs)

            likely_alternatives = [p for p in top_logprobs if p.get('logprob', -float('inf')) >= math.log(min_probability)]
            above_threshold_branches *= max(len(likely_alternatives), 1)
            
            for p in likely_alternatives:

                valid_mass = sum(math.exp(t["logprob"]) for t in top_logprobs if p["token"].startswith(t['token']))
                    
                step_probability = 1.0 if total_mass == 0 else valid_mass / total_mass
                selected_proportion = current_node["selected_proportion"]*step_probability
                text = current_node["text"]+p["token"]
                                  
                #print(f"{depth:03d} {selected_proportion:0.10f} {step_probability:0.10f} [{p["token"]:10s}] {text}")
                                
                node = {
                    "token": p["token"],
                    "text": text,
                    "step_probability": step_probability,
                    "selected_proportion": selected_proportion,
                    "above_threshold_branches": above_threshold_branches, 
                    "logprob": p.get("logprob"), 
                    "children": None 
                }
                
                if depth >= max_depth_on_this_path-1 and p["token"] == token_data["token"]:
                    node["children"] = []
                    result = (text, selected_proportion, response_dict)
                
                current_node["children"].append(node)
            
            current_nodes = [n for n in  current_node["children"] if n['token'] == token_data["token"]]
            if len(current_nodes) == 0:
                print("No generation with proba above threshold:", token_data["token"], "in", [n["token"] for n in current_node["children"]], "at depth", depth)
                break
            current_node = current_nodes[0]
            current_node["children"] = []    

    return result

def emulate_iterator(
    pipeline : OneTurnConversationPipeline = config.DefaultPipeline,
    max_generation = 50,
    min_probability = 1e-4,
    force_llm_args: Optional[dict] = {}):

    # You can retrive this frame using get_last_frame(your_emulated_function) in interactive mode
    frame = get_caller_frame()

    # Get everything about the function you are emulating
    # inspection = country_name.hosta_inspection
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
        results = []
        # Convert the inspection to a prompt
        messages = pipeline.push(inspection)
        
        branches_iterator = travel_branches_from_node(
            inspection=inspection,
            messages=messages, 
            min_probability=min_probability,
            force_llm_args=force_llm_args)
        
        counted_generations = max_generation
        for text, proba, response_dict in branches_iterator:
            # print("--> ", text, proba)
            
            counted_generations -= 1               
    
            if proba >= min_probability:
                response_dict["choices"][0]["message"]["text"] = text
                # Convert the model response to a python object according to expected types
                try:
                    response_data = pipeline.pull(inspection, response_dict)
                except ValueError as e:
                    if counted_generations <= 0:
                        break                    
                    continue
                
                is_new_answer = response_data not in results
                results.append(response_data)
                
                if is_new_answer:
                    yield response_data
            else:
                # We went to far and got lost in low probabilities
                pass
            
            if counted_generations <= 0:
                break
                                        
    return _iterator()
