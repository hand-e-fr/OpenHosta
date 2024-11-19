# Installation Guide

The `OpenHosta` python package contains multiple features which you can install via PyPI or GitHub. However, you may need to install other packages depending on how you use `OpenHosta`. Indeed, some `OpenHosta` features require additional dependencies to be used. You'll also need to set up your API key for easier use.
All this will be detailed in this document.

## Prerequisites

1. **Python 3.10 | 3.11 | 3.12**
   - Download and install Python from [python.org](https://www.python.org/downloads/).

2. **pip**
   - `pip` is generally included with Python. Verify its installation with:
     ```sh
     pip --version
     ```

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
  git clone git@github.com:hand-e-fr/OpenHosta.git
  ```

  1. Navigate to the directory:

  ```sh
  cd OpenHosta
  ```

  3. Install the package.

  ```sh
  pip install .
  ```

  4. Verify installation

  ```sh
  python -c "import OpenHosta; print(OpenHosta.__version__)"
  ```

Installing OpenHosta with GitHub gives you access to all the source code, allowing you to take over the tool and perhaps contribute to the project, but the pip approach is simpler for classic OpenHosta use.

## Additional Dependencies

You can install additional dependencies to use deeper features of `OpenHosta`. You'll need to add the following options.

```sh
pip install -U OpenHosta[all] # With pip
```
*or* 
```sh
pip install .[all] # With GitHub
```

### `predict`

Adds the `predict` function and all its features.
```sh
pip install -U OpenHosta[predict]
```

### `pydantic`

Adds the `pydantic` compatibility with all functions.
```sh
pip install OpenHosta[pydantic]
```
*or*
```sh
pip install pydantic # Basically the same
```

### `dev`

*Not inclued in "all"*

Adds all the useful OpenHosta development tools for those who'd like to contribute.
```sh
pip install .[dev] # Useful only with the GitHub install, yon won't need it if you're not interested in contributing for OpenHosta 
```

### `tests`

*Not inclued in "all"*

Adds all the package used for executing the `OpenHosta`'s tests.
```sh
pip install .[tests] # Also only useful with the GitHub install
```

### Combining Options

All options can be combined as needed.

For example, if you're a contributor, it might be useful to install `dev` and `tests` packages:
```sh
pip install .[dev, tests]
```
Note that the `pydantic` and `predict` packages combined are the same as `all`.

## API Key Setup

1. Get API key from your favorite provider. As default model we use OpenAI `GPT-4o`, you can get a key from https://platform.openai.com/account/api-keys
2. Then all you have to do is set a environment variable containing this API key:
   - Windows:
    ```sh
    setx OPENAI_API_KEY "your-openai-api-key"
    ```
   - MacOS/Linux:
    ```sh
    # in your .bashrc or .zshrc
    export OPENAI_API_KEY='your-anthropic-api-key'
    ```

## Common Issues

If you encounter a problem, try these few method that may fix it:

- Update pip: ``pip install --upgrade pip``
- Use virtual environment
- Try ``pip3`` instead of ``pip``
- Use ``sudo`` (Unix) or run as administrator (Windows) if permission errors occur

For more help and if the problem persist, please file an issue on GitHub.
