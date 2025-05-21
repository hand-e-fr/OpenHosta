from typing import Dict, List, Tuple, Any
from abc import ABC, abstractmethod
import json

from ..models import Model
from ..core.meta_prompt import MetaPrompt, EMULATE_META_PROMPT, USER_CALL_META_PROMPT

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
    
    def push(self, inspection) -> dict:
        
        # reset pipe state for new usage
        self.pipe_state = {}

        inspection    = self.push_detect_missing_types(inspection)
        model         = self.push_chose_model(inspection)
        schema, data  = self.push_encode_types(inspection, model)
        meta_messages = self.push_select_meta_prompts(inspection)

        # in case the user wants ti use it by itself
        self.model = model

        # This where your prompt is. You could also call `conversation.run(data)`
        messages = [
            {
                "role": role, "content": [
                        {"type": "text",  "text" : meta_prompt.render(schema | data) }
                    ] + [
                        {"type": "image_url", "image_url": image} if image else []
                    ]
            }
            for role, meta_prompt, image in meta_messages
        ]
            
        return messages


    def push_detect_missing_types(self, inspection):
        """Python Level"""
        return_type = inspection["analyse"]["type"]

    def push_chose_model(self, inspection):
        """OpenHosta Level"""
        self.model = self.model_list[0]

    def push_encode_types(self, inspection):
        """Data & Schema Level"""
        data = inspection["prompt_data"] | self.data
        schema = ""

        return schema, data

    def push_select_meta_prompts(self, inspection):
        """Prompt Level""" 
        
        default_meta_conversation:Flow = [
            ('system',EMULATE_META_PROMPT, None),
            ('user',  USER_CALL_META_PROMPT, None),
        ]
        return default_meta_conversation

    def pull(self,response_dict ):
        self.pull_extract_messages(response_dict)
        self.pull_extract_data_section(response_dict)
        self.pull_verify_llm_capability(response_dict)
        response_data = self.pull_type_data_section(response_dict)

        return response_data

    def pull_extract_messages(self, response_dict:dict) -> dict:
        """Prompt Level"""
        return self.model.pull_extract_messages(response_dict)
        pass

    def pull_extract_data_section(self, messages:dict) -> Any:
        """Data & Schema Level"""

        untyped_response = self.model.response_parser(messages)

        if True: # output contains coded data
            response = self.extract_data_section(untyped_response)
        else:
            # Simple text not expected, response = untyped_response
            response = untyped_response

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

    
        response_data    = apply_type(untyped_response, self.return_type)
        pass


    def extract_data_section(self, 
                        response:str, 
                        reasoning_start_and_stop_tags = ["<think>", "</think>"]) -> tuple[str, str]:
        """
        This function split response into rational and answer.

        Special prompt may ask for chain-of-thought or models might be trained to reason first.

        Args:
            response (str): response from the model.

        Returns:
            tuple[str, str]: rational and answer.
        """
        response = response.strip()

        if reasoning_start_and_stop_tags[0] in response and reasoning_start_and_stop_tags[1] in response:
            chunks = response[8:].split(reasoning_start_and_stop_tags[1])
            rational = chunks[0]
            answer = reasoning_start_and_stop_tags[1].join(chunks[1:]) # in case there are multiple </think> tags
        else:
            rational, answer = "", response
        
        return rational, answer
