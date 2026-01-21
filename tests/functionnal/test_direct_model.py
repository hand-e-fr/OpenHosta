import os
import time
import pytest
from dotenv import load_dotenv

load_dotenv()

# To run these tests you need to set .env variables to define an LLM provider
# e.g. for OpenAI:
# OPENHOSTA_LLM_PROVIDER=openai
# OPENHOSTA_OPENAI_API_KEY=your_api_key

# you also need to install pytest and python-dotenv:
# pip install pytest python-dotenv

# To run the tests, use the command:
# pytest OpenHosta/tests/functionnalTests/test_emulate.py

from OpenHosta import emulate
from OpenHosta import OneTurnConversationPipeline, config


# Basic test to check if the emulate function works with a simple prompt
def test_assistant_force_answer():
    answer = "**"
    print(answer,  end="")
    for i in range(10):
        response = config.DefaultModel.api_call(
            llm_args={"max_tokens": 20},
            messages=[
                {"role": "user", "content": "What is the capital of France?"},
                {"role": "assistant", "content": answer}
                ])
        
        new_token = config.DefaultModel.get_response_content(response)
        answer += new_token
        print(new_token, end="", flush=True)
        
    
    
    