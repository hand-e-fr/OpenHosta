from typing import Dict, List, Tuple, Any
from abc import ABC, abstractmethod

from ..models import Model, ModelCapabilities

from ..core.meta_prompt import MetaPrompt, EMULATE_META_PROMPT, USER_CALL_META_PROMPT
from ..core.analizer import encode_function
from ..core.type_converter import type_returned_data

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

        return chosen_model

    def push_encode_inspected_data(self, inspection, model_capabilities: set[ModelCapabilities]):
        """Data & Schema Level"""
        
        analyse = inspection["analyse"]

        snippets = encode_function(analyse, model_capabilities)

        return snippets 

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
        return default_meta_conversation

    def push(self, inspection) -> dict:
        
        # reset pipe state for new usage
        inspection     = self.push_detect_missing_types(inspection)
        inspection["model"] = self.push_choose_model(inspection)
        
        inspection["pipeline"] = self

        meta_messages       = self.push_select_meta_prompts(inspection)

        # This is after push_select_meta_prompts because we may have changed arg values (eg: resized images)
        encoded_data   = self.push_encode_inspected_data(inspection, inspection["model"].capabilities)

        inspection["data_for_metaprompt"] = encoded_data
        inspection["meta_prompts"] = meta_messages

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

    def pull_extract_messages(self, inspection, response_dict:dict) -> dict:
        """Prompt Level"""
        return inspection["model"].get_response_content(response_dict)

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
        
        return response_string.strip()

    def pull_type_data_section(self, inspection, response:Any) -> Any:
        """Python Level"""
        l_ret_data = type_returned_data(response, inspection["analyse"]["type"])

        return l_ret_data

    def pull(self, inspection, response_dict ):
        inspection["logs"]["rational"] = ""
        inspection["logs"]["answer"] = ""
        inspection["logs"]["clean_answer"] = ""
        
        inspection["logs"]["llm_api_response"] = response_dict
        
        raw_response = self.pull_extract_messages(inspection, response_dict)
        
        if 'reasoning' in response_dict.get("choices",[{}])[0].get("message", {}):
            inspection["logs"]["rational"] += response_dict["choices"][0]["message"]["reasoning"]
        
        response_string = self.pull_extract_data_section(inspection, raw_response)
        inspection["logs"]["response_string"] = response_string
        
        response_data = self.pull_type_data_section(inspection, response_string)
        inspection["logs"]["response_data"] = response_data
        
        return response_data
    

