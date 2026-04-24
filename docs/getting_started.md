# Getting Started with OpenHosta

Welcome to **OpenHosta**! OpenHosta is a **Python library** designed to facilitate the integration of **LLMs** into the developer's environment, adding an AI layer to Python without distorting it.

## First Steps

If you do not have access to any remote LLM and do not have an NVIDIA GPU, we recommend that you try **qwen3.5:4b** using Ollama locally. Follow the [installation guide](installation.md) to set up Ollama then configure `qwen3.5:4b`.

If you have a strong GPU (at least 32GB of VRAM), we recommend that you install **Mistral-small3.2** locally, or use the **OpenAI API**.

## Basic Setup
You can set your API key and default model via environment variables or directly in code.

```python
from OpenHosta import config

# Example for Local Ollama
config.DefaultModel.base_url = "http://localhost:11434/v1"
config.DefaultModel.model_name = "qwen3.5:4b"
config.DefaultModel.api_key = "not used by ollama local api"

# Tip: Disable reasoning/thinking to speed up Qwen
config.DefaultModel.api_parameters |= {"reasoning": {"effort": "none"}}
```

## Supported Environment Variables
```env
OPENHOSTA_DEFAULT_MODEL_API_KEY="your_api_key"
OPENHOSTA_DEFAULT_MODEL_BASE_URL="https://api.openai.com/v1" # Optional
OPENHOSTA_DEFAULT_MODEL_NAME="gpt-4.1"               # Default 
OPENHOSTA_DEFAULT_MODEL_TEMPERATURE=0.7              # Optional
OPENHOSTA_DEFAULT_MODEL_SEED=42                      # Optional. Deterministic for local LLMs
OPENHOSTA_RATE_LIMIT_WAIT_TIME=60                    # Optional
```

### *Legal Framework*
When deploying AI in production, always verify legal compliance (GDPR, AI Act) and implement security measures against injection attacks.
