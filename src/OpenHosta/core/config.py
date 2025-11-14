import os
import sys
import textwrap

try:
    from dotenv import load_dotenv
except Exception as e:
    sys.stderr.write("[OpenHosta/CONFIG_ERROR] python-dotenv is not installed. It is a good practice to install it and store your credentials in a .env file.\n")
    
from ..pipelines import OneTurnConversationPipeline
from ..models import Model, OpenAICompatibleModel

# Config shall be a class so that any reference to default model or default pipeline are updated during runtime
# (no copy)

class Config:
    def __init__(self):
        self._DefaultModel = OpenAICompatibleModel(
            model_name="gpt-4o",
            base_url="https://api.openai.com/v1"
        )
        
        self._DefaultPipeline = OneTurnConversationPipeline(
            model_list=[self._DefaultModel]
        )
        
    # Add getter and setter for DefaultModel and DefaultPipeline
    @property
    def DefaultModel(self) -> OpenAICompatibleModel:
        return self._DefaultModel

    @property
    def DefaultPipeline(self) -> OneTurnConversationPipeline:
        return self._DefaultPipeline
    
    @DefaultModel.setter
    def DefaultModel(self, model: OpenAICompatibleModel):
        if not isinstance(model, OpenAICompatibleModel):
            raise ValueError("DefaultModel must be an instance of OpenAICompatibleModel")
        
        # copy each attribute to avoid reference issues
        for name, value in vars(model).items():
            if  name[0] != '_':  # avoid copying private attributes
                setattr(self._DefaultModel, name, value)

    @DefaultPipeline.setter
    def DefaultPipeline(self, pipeline: OneTurnConversationPipeline):
        if not isinstance(pipeline, OneTurnConversationPipeline):
            raise ValueError("DefaultPipeline must be an instance of OneTurnConversationPipeline")
        self._DefaultPipeline.model_list = pipeline.model_list
        self._DefaultPipeline.llm_args = pipeline.llm_args
        self._DefaultPipeline.user_call_meta_prompt = pipeline.user_call_meta_prompt
        self._DefaultPipeline.emulate_meta_prompt = pipeline.emulate_meta_prompt
    
config = Config()  
        
def reload_dotenv(override: bool = True, dotenv_path="./.env"):
    def recursive_find_dotenv(path):
        if os.path.isfile(os.path.join(path, ".env")):
            return os.path.join(path, ".env")
        parent = os.path.dirname(path)
        if parent == path:  # Reached the root directory
            return None
        return recursive_find_dotenv(parent)
    dotenv_path = os.path.abspath(dotenv_path)
    dotenv_find_path = recursive_find_dotenv(os.path.dirname(dotenv_path))
    if dotenv_path == dotenv_find_path:
        # There is a .env file at the specified path. This is good for production
        pass
    elif dotenv_find_path is not None:
        # There is a .env file in a parent directory. This is good for development.
        sys.stderr.write(f"[OpenHosta/CONFIG_WARNING] .env file not found at {dotenv_path}. Using {dotenv_find_path} instead.\n")
        dotenv_path = dotenv_find_path
    else:
        # There is no .env file. This is bad.
        sys.stderr.write(f"[OpenHosta/CONFIG_WARNING] .env file not found at {dotenv_path} or in any parent directory.\n")
        sys.stderr.write(textwrap.dedent("""\
            [OpenHosta/CONFIG_ERROR] .env file not found. It is a good practice to store your credentials in a .env file.
            Example .env file:
            ------------------
            OPENHOSTA_DEFAULT_MODEL_API_KEY="your_api_key"
            OPENHOSTA_DEFAULT_MODEL_BASE_URL="https://api.openai.com/v1" # Optional
            OPENHOSTA_DEFAULT_MODEL_NAME="gpt-5"                 # Default to "gpt-4.1" 
            OPENHOSTA_DEFAULT_MODEL_TEMPERATURE=0.7                    # Optional
            OPENHOSTA_DEFAULT_MODEL_TOP_P=0.9                          # Optional
            OPENHOSTA_DEFAULT_MODEL_MAX_TOKENS=2048                    # Optional
            OPENHOSTA_DEFAULT_MODEL_SEED=42                            # Optional. If set with a local LLM your application will be deterministic.
            ------------------
            """))        
        return False
    
    if load_dotenv(dotenv_path=dotenv_path, override=override):
        config.DefaultModel.api_key = os.getenv("OPENHOSTA_DEFAULT_MODEL_API_KEY", None)
        config.DefaultModel.base_url = os.getenv("OPENHOSTA_DEFAULT_MODEL_BASE_URL", "https://api.openai.com/v1")
        config.DefaultModel.model_name = os.getenv("OPENHOSTA_DEFAULT_MODEL_NAME", "gpt-4.1")

        TEMPERATURE =       os.getenv("OPENHOSTA_DEFAULT_MODEL_TEMPERATURE", None)
        TOP_P =             os.getenv("OPENHOSTA_DEFAULT_MODEL_TOP_P", None)
        MAX_TOKENS =        os.getenv("OPENHOSTA_DEFAULT_MODEL_MAX_TOKENS", None)
        SEED =              os.getenv("OPENHOSTA_DEFAULT_MODEL_SEED", None)
        
        if TEMPERATURE is not None:
            config.DefaultPipeline.model_list[0].api_parameters |= {"temperature": float(TEMPERATURE)}
        if TOP_P is not None:
            config.DefaultPipeline.model_list[0].api_parameters |= {"top_p": float(TOP_P)}
        if MAX_TOKENS is not None:
            config.DefaultPipeline.model_list[0].api_parameters |= {"max_tokens": int(MAX_TOKENS)}
        if SEED is not None:
            config.DefaultPipeline.model_list[0].api_parameters |= {"seed": int(SEED)}
                    
        return True

    else:
        sys.stderr.write(f"[OpenHosta/CONFIG_ERROR] Failed to load .env file at {dotenv_path}.\n")
        return False

reload_dotenv(override=False)

