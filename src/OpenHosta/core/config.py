
import sys

from ..pipelines import OneTurnConversationPipeline
from ..models import Model, OpenAICompatibleModel

DefaultModel = OpenAICompatibleModel(
        model_name="gpt-4o", 
        base_url="https://api.openai.com/v1")

DefaultPipeline = OneTurnConversationPipeline(
    model_list=[DefaultModel]
)
     
def set_default_model(new):
    if isinstance(new, Model):
        DefaultPipeline.model = new
    else:
        sys.stderr.write("[CONFIG_ERROR] Invalid model instance.\n")

def set_default_apiKey(api_key:str=None):
    if api_key is not None or isinstance(api_key, str):
        DefaultPipeline.model.api_key = api_key
    else:
        sys.stderr.write("[CONFIG_ERROR] Invalid API key.")    

def set_default_api_parameters(api_parameters:dict):
    DefaultPipeline.model.api_parameters |= api_parameters
