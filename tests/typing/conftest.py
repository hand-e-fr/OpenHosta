"""
pytest configuration for typing tests.

Adds CLI options to override the default OpenHosta model/pipeline:
    --endpoint-url      Base URL for the LLM endpoint
    --endpoint-api-key  API key (optional)
    --model-name        Model name to use for emulate() calls

These options are injected by build_compat_matrix_types.sh for each
(endpoint, model) pair. When not supplied, OpenHosta uses its own
default (env / .env / .models.yaml).
"""

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--endpoint-url",
        action="store",
        default=None,
        help="Base URL of the LLM endpoint (e.g. https://api.openai.com/v1)",
    )
    parser.addoption(
        "--endpoint-api-key",
        action="store",
        default=None,
        help="API key for the endpoint (optional)",
    )
    parser.addoption(
        "--model-name",
        action="store",
        default=None,
        help="Model name to use for all emulate() calls in this session",
    )


@pytest.fixture(scope="session", autouse=True)
def override_default_pipeline(request: pytest.FixtureRequest):
    """
    If --model-name (and optionally --endpoint-url / --endpoint-api-key) are
    provided, replace config.DefaultPipeline with a single-model pipeline so
    that all emulate() calls in this session use the specified model.

    This fixture is session-scoped and auto-used: no test modification needed.
    """
    model_name = request.config.getoption("--model-name")
    if model_name is None:
        # No override requested — use the default pipeline as-is.
        yield
        return

    endpoint_url = request.config.getoption("--endpoint-url") or "https://api.openai.com/v1"
    api_key = request.config.getoption("--endpoint-api-key") or None

    from OpenHosta.models import OpenAICompatibleModel
    from OpenHosta.pipelines import OneTurnConversationPipeline
    from OpenHosta import defaults

    model = OpenAICompatibleModel(
        model_name=model_name,
        base_url=endpoint_url,
        api_key=api_key,
    )

    # Build a fresh pipeline with only this model.
    new_pipeline = OneTurnConversationPipeline(model_list=[model])

    # Swap in-place so all emulate() calls pick it up.
    original_pipeline = defaults.config.DefaultPipeline
    # original_model = defaults.Config.DefaultModel
    defaults.config.DefaultPipeline = new_pipeline
    # defaults.config.DefaultModel = model

    yield

    # Restore original pipeline after the session (good practice for re-use
    # in interactive / watch mode).
    defaults.config.DefaultPipeline = original_pipeline
    # defaults.config.DefaultModel = original_model
