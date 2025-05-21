from typing import Dict, List, Tuple
from abc import ABC, abstractmethod

from ..models import Model
from ..core.meta_prompt import MetaPrompt, EMULATE_META_PROMPT, USER_CALL_META_PROMPT

from .conversation import Conversation

Flow = List[Tuple[str, MetaPrompt]]


class Pipeline(ABC):
    """
    Abstract base class defining the interface for model selection policies.

    This class provides a template for implementing different strategies
    for selecting and managing AI models.
    """

    @abstractmethod
    def outline(self, inspection) -> Conversation:
        """
        Retrieve the best prompt associated with this policy.

        Returns:
            MetaPrompt: The meta prompt to be used for this inspection.
        """
        pass


class OneTurnConversationPipeline(Pipeline):
    """
    This policy always use the default MetaPrompt with the default model
    """

    def __init__(self, 
                 default_model:Model=None,
                 default_llm_args={}):
        
        self.model:Model = default_model
        self.llm_args:Dict = default_llm_args

        self.default_meta_conversation:Flow = [
            ('system',EMULATE_META_PROMPT),
            ('user',  USER_CALL_META_PROMPT),
        ]

        self.data = {
            "use_json_mode":False,
            "allow_thinking":True
        }
    
    def outline(self, inspection) -> Conversation:
           
        return_type = inspection["analyse"]["type"]
        
        data = inspection["prompt_data"] | self.data

        conversation = Conversation(inspection,
                                    self.model, 
                                    self.default_meta_conversation,
                                    return_type,
                                    self.llm_args,
                                    data) 

        return conversation
