# Installation

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
  pip install -U OpenHosta[all]
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
  pip install .[all]
  ```

  4. Verify installation

  ```sh
  python -c "import OpenHosta; print(OpenHosta.__version__)"
  ```

Installing OpenHosta with GitHub gives you access to all the source code, allowing you to take over the tool and perhaps contribute to the project, but the pip approach is simpler for classic OpenHosta use.

## Additional Dependencies

### `predict`

### `pydantic`

### `dev`

### `tests`

## API Key Setup

## Common Issues

```
py -3.12 -m pip install
```

emulate en dehors du return 