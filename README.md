# OpenHosta 
v2.0-beta2 - Opensource Project

**- The future of development is human -**

Welcome to the OpenHosta documentation, a powerful tool that facilitates the integration LLM in the development environnement. OpenHosta is used to emulate functions using AI, while respecting Python's native paradygma and syntax.

For this project, we have adopted a [Code of Conduct](CODE_OF_CONDUCT.md) to ensure a respectful and inclusive environment for all contributors. Please take a moment to read it.

## Table of Content

- [OpenHosta](#openhosta)
  - [Table of Content](#table-of-content)
  - [How to install OpenHosta ?](#how-to-install-openhosta-)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
      - [Via pip](#via-pip)
      - [Via git (Developper version)](#via-git-developper-version)
    - [Example](#example)
  - [Further information](#further-information)
    - [Contributing](#contributing)
    - [License](#license)
    - [Authors \& Contact](#authors--contact)

---

## How to install OpenHosta ?

### Prerequisites

1. **Python 3.10 | 3.11 | 3.12**
   - Download and install Python from [python.org](https://www.python.org/downloads/).

2. **pip**
   - pip is generally included with Python. Verify its installation with:
     ```sh
     pip --version
     ```

3. **Git**
   - Download and install Git from [git-scm.com](https://git-scm.com/downloads).

4. **Virtual Environment (optional)**
   - Create and activate a virtual environment:
     ```bash
     python -m venv env
     ```
   - Activate the virtual environement:
      ```bash
      .\env\Scripts\activate # Windows
      source env/bin/activate # macOS/Linux
      ```

5. **API Key**
   - **API Key**: Log in to your OpenAI account from [openai.com](https://openai.com/), then create your API key. For further information, you can check this [tuto](https://help.openai.com/en/articles/4936850-where-do-i-find-my-openai-api-key).

### Installation

#### Via pip

1. Run the following command to install OpenHosta directly:
 
```sh
pip install openhosta
```

2. After the installation, you can verify that OpenHosta is installed correctly by running:

```sh
pip show openhosta
```

#### Via git (Developper version)

1. Clone the **Git repository** to your local machine using the following command:

```bash
git clone git@github.com:hand-e-fr/OpenHosta.git
```

2. Navigate to the **directory** of the cloned project:

```bash
cd OpenHosta
```

3. Ensure you have installed the necessary **dependencies** before starting.

```bash
pip install .
```

4. Check that you have the correct version from Python. 

```python
import OpenHosta

OpenHosta.__version__
```

This way you have all the documentation and source code to understand our project

### Example

```python
from OpenHosta import emulate, config

config.set_default_apiKey("put-your-api-key-here")

def translate(text:str, language:str)->str:
    """
    This function translates the text in the “text” parameter into the language specified in the “language” parameter.
    """
    return emulate()

result = translate("Hello World!", "French")
print(result)
```
You check OpenHosta's [documentation](doc/Docs.md) for more detailled informations or exemple

## Further information

### Contributing

We warmly welcome contributions from the community. Whether you are an experienced developer or a beginner, your contributions are welcome.

If you wish to contribute to this project, please refer to our [Contribution Guide](CONTRIBUTING.md) and our [Code of Conduct](CODE_OF_CONDUCT.md).

Browse the existing [issues](https://github.com/hand-e-fr/OpenHosta/issues) to see if someone is already working on what you have in mind or to find contribution ideas.

### License

This project is licensed under the MIT License. This means you are free to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the software, subject to the following conditions:

  - The text of the license below must be included in all copies or substantial portions of the software.

See the [LICENSE](LICENSE) file for more details.

### Authors & Contact

For further questions or assistance, please refer to partner hand-e or contact us directly via github.

**Authors**:
   - Emmanuel Batt: Manager and Coordinator, Founder of Hand-e
   - William Jolivet: DevOps, SysAdmin
   - Léandre Ramos: MLOps, IA developer
   - Merlin Devillard: UX designer, Product Owner

GitHub: https://github.com/hand-e-fr/OpenHosta

---

Thank you for your interest in our project and your potential contributions!

**The OpenHosta Team**
