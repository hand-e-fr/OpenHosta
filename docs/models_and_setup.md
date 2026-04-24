# Models and Setup

This document explains advanced configuration, including model selection, custom LLM clients, and observability.

## OpenAICompatibleModel
Instantiate this class to handle many different models.

```python
from OpenHosta import OpenAICompatibleModel, config

my_model = OpenAICompatibleModel(
    model_name="gpt-4o", 
    base_url="https://api.openai.com/v1/chat/completions",
    api_key="your-api-key"
)

config.DefaultModel = my_model
```

## Model Agnosticism (Azure OpenAI & vLLM)
OpenHosta natively supports standard OpenAI endpoints for Azure and vLLM.

**Azure:**
```python
from OpenHosta import OpenAICompatibleModel

azure_model = OpenAICompatibleModel(

    model_name="deployment-name", 
    base_url="https://RESOURCE.openai.azure.com/openai/deployments/deployment-name",
    api_key="azure-key",
    additionnal_headers={"api-key": "azure-key"} 
)
```

**vLLM:**
```python
from OpenHosta import OpenAICompatibleModel

vllm_model = OpenAICompatibleModel(

    model_name="meta-llama/Meta-Llama-3-8B-Instruct", 
    base_url="http://localhost:8000/v1",
    api_key="EMPTY"
)
```

## Ollama & Local Models

When using [Ollama](https://ollama.com/), you can configure advanced parameters via `api_parameters`.

### Disabling Reasoning (e.g., Qwen)
Some models like **Qwen** include reasoning capabilities (thinking) by default. If you want to disable this to speed up responses or get direct output, you can set the `reasoning` effort to `none`:

```python
from OpenHosta import config

# Disable thinking for Qwen models in Ollama
config.DefaultModel.api_parameters |= {"reasoning": {"effort": "none"}}
```

## Changing the MetaPrompt
You can customize the prompt templates via `config.DefaultPipeline.user_call_meta_prompt` or create your own `MetaPrompt`.

## Observability & Audit Mode
Enable audit mode for detailed execution logs:
```python
from OpenHosta import config
config.AUDIT_MODE = True
```

For more details on audit events, compliance, and production deployment, see the **[Production & Auditing Guide](production.md)**.

## Cost Tracking
Use `track_costs` context manager to count tokens.
```python
from OpenHosta import emulate, track_costs

with track_costs() as tracker:
    # execution
    pass
print(tracker.total_tokens)
```
