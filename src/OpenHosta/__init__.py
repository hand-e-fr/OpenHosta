__version__ = "4.2.1"

from .defaults import config
from .defaults import reload_dotenv

from .core.logger import print_last_prompt, print_last_decoding
from .core.logger import print_last_probability_distribution, print_last_uncertainty
from .core.meta_prompt import MetaPrompt
from .core.uncertainty import safe
from .core.errors import UncertaintyError
from .core.cost_tracker import track_costs
from .core.audit import register_audit_callback, unregister_audit_callback

from .exec.ask import ask, ask_async, ask_stream, ask_stream_async
from .exec.emulate import emulate, emulate_async
from .exec.emulate_iterator import emulate_iterator
from .exec.closure import closure, closure_async
# from .semantics import SemanticSet, SemanticDict # Maybe in 5.0
from .semantics.operators import test, test_async

from .models import OpenAICompatibleModel as Model
from .models import OpenAICompatibleModel

from .pipelines import Pipeline, OneTurnConversationPipeline

DefaultModel = config.DefaultModel
DefaultPipeline = config.DefaultPipeline

all = (
    "ask",
    "ask_async",
    "ask_stream",
    "ask_stream_async",
    "emulate",
    "emulate_async",
    "emulate_iterator", 
    "closure",
    "closure_async",
    "SemanticSet",
    "SemanticDict",
    "config",
    "reload_dotenv",
    "Model",
    "DefaultModel",
    "DefaultPipeline",
    "OpenAICompatibleModel",
    "MetaPrompt",
    "print_last_prompt",
    "print_last_decoding",
    "print_last_probability_distribution",
    "print_last_uncertainty",
    "Pipeline",
    "OneTurnConversationPipeline",
    "safe",
    "test",
    "test_async",
    "UncertaintyError",
    "track_costs",
    "register_audit_callback",
    "unregister_audit_callback",
)
