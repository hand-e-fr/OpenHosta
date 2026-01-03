import os
import time
import pytest
from dotenv import load_dotenv

load_dotenv()



from OpenHosta import emulate, safe
#from OpenHosta import emulate_iterator
from OpenHosta import OneTurnConversationPipeline, config


from OpenHosta.core.inspection import get_caller_frame, get_hosta_inspection
from OpenHosta.core.config import config
from OpenHosta.pipelines import OneTurnConversationPipeline

def emulate_iterator(pipeline : OneTurnConversationPipeline = config.DefaultPipeline, max_generation = 100, min_probability = 1e-8, *args, **kwargs):

    # You can retrive this frame using get_last_frame(your_emulated_function) in interactive mode
    frame = get_caller_frame()

    # Get everything about the function you are emulating
    inspection = get_hosta_inspection(frame)

    def _wrapper():
        
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
                
        # Convert the inspection to a prompt
        messages = pipeline.push(inspection)
        
        try:
            # This is the api call to the model, nothing more. Easy to debug and test.
            response_dict = inspection.model.api_call(messages, inspection["force_llm_args"])
        except RateLimitError as e:
            try:
                retry_delay = int(os.getenv("OPENHOSTA_RATE_LIMIT_WAIT_TIME", 60))
            except:
                retry_delay = 0

            print(f"[emulate] Rate limit exceeded. We wait for {retry_delay}s then retry.", e)

            if retry_delay == 0:
                raise e
            else:
                time.sleep(retry_delay)
                response_dict = inspection["model"].api_call(messages, inspection["force_llm_args"])
            
        # Convert the model response to a python object according to expected types
        response_data = pipeline.pull(inspection, response_dict)
        
        return response_data




    return _wrapper()


# Basic test to check if the emulate function works with a simple prompt
def test_generate_basic():
    """
    """
    
    def country_name() -> str:
        """
        This function returns the name of a country.

        Returns:
            str: The name of a county.
        """
        return emulate_iterator()

    country_name()    
    
    def get_capital(country: str) -> str:
        """
        This function returns the capital of a given country.
        """
        return emulate()
    
    response = get_capital("France")
    assert "Paris" in response, f"Expected 'Paris' in response, got: {response}"
