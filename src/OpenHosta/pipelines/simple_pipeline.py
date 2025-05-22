from typing import Dict, List, Tuple, Any
from abc import ABC, abstractmethod
import json

from ..models import Model, ModelCapabilities

from ..core.meta_prompt import MetaPrompt, EMULATE_META_PROMPT, USER_CALL_META_PROMPT
from ..core.analizer import encode_function, get_thinking_and_data_sections
from ..core.type_converter import type_returned_data

Flow = List[Tuple[str, MetaPrompt]]

class Pipeline(ABC):
    """
    Abstract base class defining the interface for model selection policies.

    This class provides a template for implementing different strategies
    for selecting and managing AI models.
    """
    def __init__(self):
        super().__init__()
        self.model: Model = None

    @abstractmethod
    def push(self, inspection) -> dict:
        """
        Convert fucntion inspection into a messages list ready for API.

        Returns:
            List of messages in the right format for the chosen model.
        """
        pass

    @abstractmethod
    def pull(self, response_dict) -> Any:
        """
        Convert the model response into a python object.

        Returns:
            The model response converted into the expected python object.
        """
        pass

class OneTurnConversationPipeline(Pipeline):
    """
    This pipeline always use the default MetaPrompt with the default model
    in a one turn conversation.
    """

    def __init__(self, 
                 model_list:List[Model]=None):
        
        assert len(model_list) > 0, "You shall provide at least one model."

        self.model_list:List[Model] = model_list 
        self.pipe_state = {}
    

    def push__detect_missing_types(self, inspection):
        """Python Level"""
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


    def push__chose_model(self, inspection):
        """OpenHosta Level"""
        
        # For now, we just take the first model
        self.model = self.model_list[0]
        
        return self.model

    def push__encode_types(self, inspection, model_capabilities: set[ModelCapabilities]):
        """Data & Schema Level"""
        
        analyse = inspection["analyse"]

        snippets = encode_function(analyse, model_capabilities)

        return snippets

    def push__select_meta_prompts(self, inspection):
        """Prompt Level""" 
        
        default_meta_conversation:Flow = [
            ('system',EMULATE_META_PROMPT, None),
            ('user',  USER_CALL_META_PROMPT, None),
        ]
        return default_meta_conversation

    def push(self, inspection) -> dict:
        
        # reset pipe state for new usage
        inspection    = self.push__detect_missing_types(inspection)
        model         = self.push__chose_model(inspection)
        schema, data  = self.push__encode_types(inspection, model.capabilities)
        meta_messages = self.push__select_meta_prompts(inspection)

        # in case the user wants to use it by itself
        self.model = model
        self.return_schema = schema
        
        # For usage in pull phase
        self.inspection = inspection

        messages = [
            {
                "role": role, "content": [
                        {"type": "text",  "text" : meta_prompt.render(data) }
                    ] + [
                        {"type": "image_url", "image_url": image} if image else []
                    ]
            }
            for role, meta_prompt, image in meta_messages
        ]
            
        return messages


    def pull_extract_messages(self, response_dict:dict) -> dict:
        """Prompt Level"""
        return self.model.get_response_content(response_dict)

    def pull_extract_data_section(self, raw_response:str) -> Any:
        """Data & Schema Level"""

        thinking, untyped_response = get_thinking_and_data_sections(raw_response)
        
        if self.inspection["analyse"]["type"] is str: # output contains coded data
            # Simple text not expected, response = untyped_response
            response = untyped_response
        else:
            response = type_returned_data(untyped_response, self.inspection["analyse"]["type"])

        return response

    def pull_verify_llm_capability(self, data):
        """OpenHosta Level"""
        pass

    def pull_type_data_section(self, data:Any) -> Any:
        """Python Level"""
        
        if response.strip().endswith("```"):
            chuncks = response.split("```")
            last_chunk = chuncks[-2]
            if "{" in last_chunk and "}" in last_chunk:
                chunk_lines = last_chunk.split("\n")[1:]
                # find first line with { and last line with }
                start_line = next(i for i, line in enumerate(chunk_lines) if "{" in line)
                end_line = len(chunk_lines) - next(i for i, line in enumerate(reversed(chunk_lines)) if "}" in line) - 1
                response = "\n".join(chunk_lines[start_line:end_line + 1])

            else:
                # JSON not found in the response. (passthrough)"
                response = last_chunk
        
        try:
            if response.startswith("{"):
                l_ret_data = json.loads(response)
            else:
                l_ret_data = response
                
        except json.JSONDecodeError as e:
            # If not a JSON, use as is
            l_ret_data = response

        return l_ret_data


    def pull(self,response_dict ):
        self.pull_extract_messages(response_dict)
        self.pull_extract_data_section(response_dict)
        self.pull_verify_llm_capability(response_dict)
        response_data = self.pull_type_data_section(response_dict)

        return response_data
    

