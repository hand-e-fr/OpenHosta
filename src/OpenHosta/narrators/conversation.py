
from typing import Dict

from ..core.type_converter import apply_type
from ..models import DialogueModel


class Conversation:

    def __init__(self, 
                 inspection:Dict, 
                 model:DialogueModel, 
                 meta_conversation,
                 return_type:type=None,
                 llm_args={},
                 data={}):

        self.model:DialogueModel    = model
        self.inspection:Dict        = inspection
        self.meta_conversation      = meta_conversation
        self.return_type:type       = return_type
        self.llm_args:Dict          = llm_args
        self.data:Dict              = data

    def run(self, data=None):
        
        if data is None:
            data = self.data

        messages = [
                    {"role":role, "content":  meta_prompt.render(data)}
                        for role, meta_prompt in self.meta_conversation
                   ]
        
        response_dict = self.model.api_call(messages, self.llm_args)

        response_data = self.parse(response_dict)
        
        return response_data

    def parse(self, response_dict):
        untyped_response = self.model.response_parser(response_dict)
        response_data    = apply_type(untyped_response, self.return_type)

        return response_data
    
    # Print conversation at different level of abstraction
    def api_level(self):
        # TODO: return full api messages in a list of REQUEST, RESPONSE, ... 
        pass

    def message_level(self):
        # TODO: return only the message list with last response as user element
        pass

    def text_level(self):
        # TODO: return a textual conversation
        pass

    def python_level(self):
        # TODO: return a python code description of this interaction
        pass