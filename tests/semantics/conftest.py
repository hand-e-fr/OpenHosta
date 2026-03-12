"""Pytest configuration and fixtures for semantics tests."""

import pytest
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from dotenv import load_dotenv
load_dotenv()

from OpenHosta.models import OpenAICompatibleModel
from OpenHosta.core.base_model import ModelCapabilities
from OpenHosta.pipelines import OneTurnConversationPipeline


@pytest.fixture(scope="session")
def ollama_model():
    """Ollama model with logprobs + embedding support."""
    model = OpenAICompatibleModel(
        model_name="qwen3-vl:8b-instruct",
        base_url="http://localhost:11434/v1",
        embedding_model_name="nomic-embed-text",
    )
    model.capabilities |= {ModelCapabilities.LOGPROBS}
    return model


@pytest.fixture(scope="session")
def ollama_pipeline(ollama_model):
    """Pipeline wrapping the Ollama model."""
    return OneTurnConversationPipeline(model_list=[ollama_model])


@pytest.fixture(scope="session")
def animal_set(ollama_model, ollama_pipeline):
    """Pre-built SemanticSet for animals, shared across tests."""
    from OpenHosta.semantics import SemanticSet
    return SemanticSet(
        axis="Type d'animal",
        tolerance=0.25,
        model=ollama_model,
        pipeline=ollama_pipeline,
        n_examples=20,
    )


@pytest.fixture(scope="session")
def animal_dict(ollama_model, ollama_pipeline):
    """Pre-built SemanticDict for animals, shared across tests."""
    from OpenHosta.semantics import SemanticDict
    return SemanticDict(
        axis="Animal",
        tolerance=0.25,
        model=ollama_model,
        pipeline=ollama_pipeline,
        n_examples=20,
    )
