# Installation Guide

The `OpenHosta` python package contains multiple features which you can install via PyPI or GitHub.
Some features will be available only if you install additional packages like `pydantic` for advanced objects or `pillow` for image processing. You'll also need to set up a local model or configure an API key to a remote model if you do not have the right to install a model locally.

All this will be detailed in this document.

## Prerequisites

1. **Python 3.10 | 3.11 | 3.12 | 3.13**
   - Download and install Python from [python.org](https://www.python.org/downloads/).

2. **pip**
   - `pip` is generally included with Python. Verify its installation with:
     ```sh
     pip --version
     ```
     > You can also use `uv` that is a bit more modern: https://pypi.org/project/uv/

## OpenHosta Installation

### **Install using `pip`**:
  1. Install the package
  ```sh
  pip install -U OpenHosta
  ```
  2. Verify installation
  ```sh
  pip show OpenHosta
  ```
### **Install using `GitHub`**
  1. Clone the Git repository:

  ```sh
  pip install https://github.com/hand-e-fr/OpenHosta.git
  ```

  2. Verify installation

  ```sh
  python -c "import OpenHosta; print(OpenHosta.__version__)"
  ```

Installing OpenHosta with GitHub gives you access to all the source code, allowing you to take over the tool and perhaps contribute to the project, but the pip approach is simpler for classic OpenHosta use.

## Additional Dependencies

You can use additional dependencies to unlock more features.

```sh
# This will enable the image processing features (PIL.Image)
pip install pillow # tested with version 11.0.0
```

```sh
pip install pydantic # tested with version 2.11.7
```

### `tests`

In order to run the tests, you need to clone the repository and install additional packages.

Cloning the repository:
```sh
git clone https://github.com/hand-e-fr/OpenHosta.git OpenHosta.git
cd OpenHosta.git
```

Adds all the package used for executing the `OpenHosta`'s tests.

```sh
pip install .[tests] # Also only useful if you are in a cloned repo
```

## API Key Setup

1. Get API key from your favorite provider. As default model we use OpenAI `GPT-4.1`, you can get a key from https://platform.openai.com/account/api-keys
2. Then all you have to do is set a environment variable containing this API key:
   - Windows:
    ```sh
    setx OPENHOSTA_DEFAULT_MODEL_API_KEY "your-openai-api-key"
    ```
   - MacOS/Linux:
    ```sh
    # in your .bashrc or .zshrc
    export OPENHOSTA_DEFAULT_MODEL_API_KEY='your-anthropic-api-key'
    ```

We recommand to configure the default model in a .env file in your working directory or in any parent directory.
OpenHosta will automatically load it if present.

```env
OPENHOSTA_DEFAULT_MODEL_NAME="gpt-4.1"
OPENHOSTA_DEFAULT_MODEL_API_KEY="put-your-api-key-here"
```

## Local Models

You can use local models with OpenHosta using [Ollama](https://ollama.com/).

1. Install Ollama by following the instructions on their [official website](https://ollama.com/).
    ```sh
    # For MacOS or Linux
    curl -fsSL https://ollama.com/install.sh | sh
    ```

2. Download and install a model using Ollama. For example, to install the `mistral-small3.2` model, run:
   
   ```sh
   ollama pull mistral-small3.2
   ```

3. Set the model in your environment variables:
```sh
# under Linux or MacOS
export OPENHOSTA_DEFAULT_MODEL_NAME="mistral-small3.2"
export OPENHOSTA_DEFAULT_MODEL_BASE_URL="http://localhost:11434/v1"
export OPENHOSTA_DEFAULT_MODEL_API_KEY="none"
```

```
# Windows
setx OPENHOSTA_DEFAULT_MODEL_NAME "mistral-small3.2"
setx OPENHOSTA_DEFAULT_MODEL_BASE_URL "http://localhost:11434/v1"
setx OPENHOSTA_DEFAULT_MODEL_API_KEY "none"
```

or using a `.env` file in your working directory:
```env
# Recommended way as it will be loaded automatically by OpenHosta and is compatible with all OS
OPENHOSTA_DEFAULT_MODEL_NAME="mistral-small3.2"
OPENHOSTA_DEFAULT_MODEL_BASE_URL="http://localhost:11434/v1"
OPENHOSTA_DEFAULT_MODEL_API_KEY="none"
```

Verify that everything is working by running a simple script:

```python
from OpenHosta import ask
ask("Do you know what is your name as a model? If yes just answer with the name.")
# you should get 'Mistral Small 3.2' as an answer
```

## Common Issues

If you encounter a problem, try these few method that may fix it:

- Update pip: ``pip install --upgrade pip``
- Use virtual environment with `uv` or `venv`
- Try ``pip3`` instead of ``pip``
- Use ``sudo`` (Unix) or run as administrator (Windows) if permission errors occur

For more help and if the problem persist, please file an issue on GitHub.

## Where to go next?

it is time for you to check [OpenHosta's documentation](https://github.com/hand-e-fr/OpenHosta/blob/main/docs/doc.md) for more detailled informations or exemples.