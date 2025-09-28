#########################################################
#
# Test model configuration
#
#########################################################

import os
from dotenv import load_dotenv

load_dotenv()

# To run these tests you need to set .env variables to define an LLM provider
# e.g. for OpenAI:
# OPENHOSTA_LLM_PROVIDER=openai
# OPENHOSTA_OPENAI_API_KEY=your_api_key

# you also need to install pytest and python-dotenv:
# pip install pytest python-dotenv

# To run the tests, use the command:
# pytest OpenHosta/tests/functionnalTests/test_ask.py


from OpenHosta import config

config.DefaultModel.model_name = os.getenv("OPENHOSTA_MODEL_NAME", "gpt-4.1")
config.DefaultModel.base_url = os.getenv("OPENHOSTA_BASE_URL", "https://api.openai.com/v1")
config.DefaultModel.api_key = os.getenv("OPENHOSTA_OPENAI_API_KEY")


from dataclasses import dataclass
from OpenHosta import emulate

@dataclass
class Town:
    country:str
    long:float
    lat:float

def find_town(town_name:str, zip:int=None, *, size:int, alt:str=0, population=None) -> Town :
    """
    this function return the country and gps location of the town in parameter
    it also return the second word of alt
    """
    # global frame
    # frame = sys._getframe(0)
    return emulate()

r=find_town(town_name="glasgow", size="1M", alt="very long alt name for unused idea of value")
print(r)

@dataclass
class Client:
  name:str
  surname:str
  company:str
  email:str
  town:str
  address:str

def extract_client_name(text:str) -> Client:
    """
    This function translates the text in the “text” parameter into the language specified in the “language” parameter.
    """
    return emulate()

client1 = extract_client_name("FROM: sebastien@somecorp.com\nTO: shipment@hand-e.fr\nObject: do not send mail support@somecorp.com\n\nto Hello bob, I am Sebastian from Paris, france. Could you send me a sample of your main product? my office address is 3 rue de la république, Lyon 1er")
print(client1)

