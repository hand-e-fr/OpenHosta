import contextvars
from enum import Enum

from typing import Dict, List, Tuple, Any

from abc import ABC, abstractmethod

from ..models import Model, ModelCapabilities

from ..core.meta_prompt import MetaPrompt, EMULATE_META_PROMPT, USER_CALL_META_PROMPT
from ..core.analizer import encode_function
from ..core.type_converter import type_returned_data

from ..core.uncertainty import get_certainty, get_enum_logprobes, normalized_probs, UncertaintyError, ReproducibleSettings, reproducible_settings_ctxvar

MetaDialog = List[Tuple[str, MetaPrompt]]

class Pipeline(ABC):
    """
    Abstract base class defining the interface for model selection policies.

    This class provides a template for implementing different strategies
    for selecting and managing AI models.
    """
    def __init__(self):
        super().__init__()
        self.model_list:List[Model] = []
        self.llm_args = {}

    @abstractmethod
    def push(self, inspection) -> dict:
        """
        Convert fucntion inspection into a messages list ready for API.

        Returns:
            List of messages in the right format for the chosen model.
        """
        pass

    @abstractmethod
    def pull(self, inspection, response_dict) -> Any:
        """
        Convert the model response into a python object.

        Returns:
            The model response converted into the expected python object.
        """
        pass
    

    def print_last_decoding(self, inspection):
        """
        Print the last answer recived from the LLM when using function `function_pointer`.
        """
        if "rational" in inspection['logs']:
            print("[THINKING]")
            print(inspection['logs']["rational"])
        if "answer" in inspection['logs']:
            print("[ANSWER]")
            print(inspection['logs']["answer"])
        if "response_string" in inspection['logs']:
            print("[RESPONSE STRING]")
            print(inspection['logs']["response_string"])
        if "response_data" in inspection['logs']:
            print("[RESPONSE DATA]")
            print(inspection['logs']["response_data"])
        else:
            print("[UNFINISHED]")
            print("answer processing was interupted")
    

class OneTurnConversationPipeline(Pipeline):
    """
    This pipeline always use the default MetaPrompt with the default model
    in a one turn conversation.
    """

    def __init__(self, 
                 model_list:List[Model]=None,
                 emulate_meta_prompt:MetaPrompt=None,
                 user_call_meta_prompt:MetaPrompt=None):
        
        assert len(model_list) > 0, "You shall provide at least one model."

        super().__init__()
        
        self.image_size_limit = 1600  # pixels

        self.model_list:List[Model] = model_list
        
        if emulate_meta_prompt is not None:
            self.emulate_meta_prompt = emulate_meta_prompt
        else:
            self.emulate_meta_prompt = EMULATE_META_PROMPT.copy()
            
        if user_call_meta_prompt is not None:
            self.user_call_meta_prompt = user_call_meta_prompt
        else:
            self.user_call_meta_prompt = USER_CALL_META_PROMPT.copy()

    def push_detect_missing_types(self, inspection):
        """Python Level"""
        #TODO: improve type guessing and merge with closure type guessing
        if "type" not in inspection["analyse"] or inspection["analyse"]["type"] is None:
            Warning(f"No return type found for function {inspection["analyse"]["name"]}. Assuming str.")
            return_type = str
        else:
            return_type = inspection["analyse"]["type"]
        
        # Check each argument type
        for arg in inspection["analyse"]["args"]:
            if "type" not in arg or arg["type"] is None:
                Warning(f"No type found for argument {arg["name"]}. Assuming str.")
                arg["type"] = str    
                
        return inspection


    def push_choose_model(self, inspection):
        """OpenHosta Level"""
        
        # For now, we just take the first model
        chosen_model = self.model_list[0]
        inspection["model"] = chosen_model
        
        return chosen_model

    def push_encode_inspected_data(self, inspection):
        """Data & Schema Level"""
        
        model_capabilities: set[ModelCapabilities] = inspection["model"].capabilities
        analyse = inspection["analyse"]

        encoded_data = encode_function(analyse, model_capabilities)

        if hasattr(inspection["function"], "force_template_data"):
            print("[OneTurnConversationPipeline] Merging force_template_data into encoded_data: ", inspection["function"].force_template_data)
            encoded_data |= inspection["function"].force_template_data 
        
        inspection["data_for_metaprompt"] = encoded_data
        
        return encoded_data 

    def push_select_meta_prompts(self, inspection):
        """Prompt Level""" 
        
        try:
            # Find all images in args
            import PIL.Image
            pil_is_loaded = True
        except:
            image_list = []
            pil_is_loaded = False
                        
        if pil_is_loaded:
            import base64
            import io
            img_format = self.model_list[0].preferred_image_format if self.model_list[0].preferred_image_format else "png"
            size_limit = float(self.image_size_limit)

            image_list = []
            for arg in inspection["analyse"]["args"]:
                is_pil_img = isinstance(arg["value"], PIL.Image.Image)

                if is_pil_img:
                    img:PIL.Image.Image = arg["value"]
                    max_size = max(img.width, img.height)
                    ratio = min(1, size_limit/max_size)
                    if ratio == 1:
                        image_resized = img
                    else:
                        image_resized = img.resize([int(img.width*ratio),int(img.height*ratio)])
                        arg["value"] = image_resized
                    buffered= io.BytesIO()
                    image_resized.save(buffered, img_format)
                    img_string = base64.b64encode(buffered.getvalue()).decode("utf-8")
                    image_list.append(f"data:image/{img_format};base64,{img_string}")


        default_meta_conversation:MetaDialog = [
            ('system',self.emulate_meta_prompt, None),
            ('user',  self.user_call_meta_prompt, image_list),
        ]

        inspection["meta_prompts"] = default_meta_conversation

        return default_meta_conversation
    
    def push_check_uncertainty(self, inspection) -> Any:
        
        reproducible_settings:Dict[str, ReproducibleSettings] = reproducible_settings_ctxvar.get()
        
        if len(reproducible_settings) == 0:
            return inspection
        
        if inspection["model"].model_name in ["gpt-4o", "gpt-4o-mini", "gpt-4.1"] or \
           inspection["model"].capabilities & {ModelCapabilities.LOGPROBS}:
            inspection["force_llm_args"] |= {"logprobs": True, "top_logprobs": 20}
        else:
            raise UncertaintyError(f"Model {inspection['model'].model_name} does not support logprobs. Cannot compute uncertainty.")
    
        return inspection
    
    
    def pull_check_uncertainty(self, inspection) -> Any:
        
        reproducible_settings:Dict[str, ReproducibleSettings] = reproducible_settings_ctxvar.get()
        
        if len(reproducible_settings) == 0:
            return inspection

        analyse = inspection["analyse"]
        function_pointer = inspection["function"]
        result = inspection["logs"]["response_data"]
        
        if issubclass(analyse["type"], Enum):

            logprobes = get_enum_logprobes(function_pointer=function_pointer)
            inspection["logs"]["enum_logprobes"] = logprobes
                
            normalized_probability = normalized_probs(logprobes)                  
            uncertainty = sum([v for k,v in normalized_probability.items() if k != str(result.value)])

        else:

            selected_answer_certainty, above_random_branches = get_certainty(function_pointer)

            certainty = selected_answer_certainty
            uncertainty = 1 - certainty
            
            # Other possibles branches weighted by uncertainty
            # The weight is used to inhibit branches that are very close to random 
            not_generated_acceptable_answer_count = (above_random_branches - 1) * uncertainty 
            
            normalized_probability = {
                "unique_answer":selected_answer_certainty, 
                "multiple_answers":1-selected_answer_certainty, 
                }
            
            inspection["logs"]["uncertainty_counters"] = {
                "above_random_branches" : above_random_branches,
                "answer_count_estimation": 1 + not_generated_acceptable_answer_count
            }
        
        inspection["logs"]["enum_normalized_probs"] = normalized_probability
        inspection["logs"]["uncertainty"] = uncertainty

        prompt_hash = hash( str(inspection["logs"].get("llm_api_messages_sent", "")) )
        for v in reproducible_settings.values():
 
            v.cumulated_uncertainty += uncertainty
            v.trace.append( {
                "function_name":inspection["analyse"]["name"],
                "function_args":inspection["analyse"]["args"],
                "function_uncertainty": uncertainty} )
            
            if v.cumulated_uncertainty > v.acceptable_cumulated_uncertainty:
                # Find most uncertain function call in the trace
                trace_with_number = [ {"step": i, **x} for i, x in enumerate(v.trace)]
                most_uncertain_call = max(trace_with_number, key=lambda x: x["function_uncertainty"])
                raise UncertaintyError(f"""Uncertainty above threshold: {v.cumulated_uncertainty} > {v.acceptable_cumulated_uncertainty}). 
                    Risk of hallucination.
                    Most uncertain call: {most_uncertain_call}""")
                
        return inspection

    def pull_extract_messages(self, inspection, response_dict:dict) -> dict:
        """Prompt Level"""
        
        if 'reasoning' in response_dict.get("choices",[{}])[0].get("message", {}):
            inspection["logs"]["rational"] += str(response_dict["choices"][0]["message"]["reasoning"])

        # This is for gpt-oss-20b on vllm 0.11            
        if 'reasoning_content' in response_dict.get("choices",[{}])[0].get("message", {}):
            inspection["logs"]["rational"] += str(response_dict["choices"][0]["message"]["reasoning_content"])
        
        raw_response = inspection["model"].get_response_content(response_dict)
        
        return raw_response

    def pull_extract_data_section(self, inspection, raw_response:str) -> Any:
        """Data & Schema Level"""

        thinking, response_string = inspection["model"].get_thinking_and_data_sections(raw_response)

        inspection["logs"]["rational"] += thinking if thinking else ""
        inspection["logs"]["answer"] += response_string
        
        # Check if encapsulated in code block
        if response_string.endswith("```"):
            response_lines = response_string.split("\n")
            section_pos = [i for i,v in enumerate(response_lines) if v.startswith("```")]
            chunk = response_lines[(section_pos[-2]+1):section_pos[-1]]
            # Remove chunk language and parameters
            response_string = "\n".join(chunk)

        inspection["logs"]["clean_answer"] += response_string
        inspection["logs"]["response_string"] = response_string

        return response_string.strip()

    def pull_type_data_section(self, inspection, response:Any) -> Any:
        """Python Level"""
        l_ret_data = type_returned_data(response, inspection["analyse"]["type"])
        inspection["logs"]["response_data"] = l_ret_data

        return l_ret_data

    def push_build_messages(self, inspection, meta_messages:MetaDialog, encoded_data:dict) -> dict:
        messages = []
        
        inspection["logs"]["llm_api_messages_sent"] = messages
        
        for role, meta_prompt, images in meta_messages:
            
            message_content = [
                        {"type": "text",  "text" : meta_prompt.render(encoded_data) }
                    ]
            
            if images and len(images) > 0:
                for image in images:
                    message_content += [
                        {"type": "image_url", "image_url": {"url": image}}
                    ]

            messages += [{
                "role": role,
                "content": message_content
            }]
        return messages

    def push(self, inspection) -> dict:
        
        inspection["pipeline"] = self
        
        # reset pipe state for new usage
        inspection   = self.push_detect_missing_types(inspection)
        chosen_model = self.push_choose_model(inspection)
        inspection   = self.push_check_uncertainty(inspection)
        
        meta_messages  = self.push_select_meta_prompts(inspection)
        # This is after push_select_meta_prompts because we may have changed arg values (eg: resized images)
        encoded_data   = self.push_encode_inspected_data(inspection)
        messages       = self.push_build_messages(inspection, meta_messages, encoded_data)
        
        return messages
    
    def pull(self, inspection, response_dict ):
        inspection["logs"]["rational"] = ""
        inspection["logs"]["answer"] = ""
        inspection["logs"]["clean_answer"] = ""
        inspection["logs"]["llm_api_response"] = response_dict
        
        raw_response    = self.pull_extract_messages(inspection, response_dict)
        response_string = self.pull_extract_data_section(inspection, raw_response)
        response_data   = self.pull_type_data_section(inspection, response_string)
        inspection      = self.pull_check_uncertainty(inspection)
        
        return response_data
    

