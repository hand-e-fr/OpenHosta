# OpenHosta 
v2.1.4 - Open-Source Project

<a href="https://colab.research.google.com/github/hand-e-fr/OpenHosta/blob/main/docs/openhosta_phi4.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/> Basic Usage - Synthetic Data - local LLM (phi-4)</a>
<br/>
<a href="https://colab.research.google.com/github/hand-e-fr/OpenHosta/blob/main/docs/openhosta_agent.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/> Simple AI Agent with gpt-4o</a>


**- The future of development is human -**

Welcome to the OpenHosta documentation, a powerful tool that facilitates the integration LLM in the development environnement. OpenHosta is used to emulate functions using AI, while respecting Python's native paradygma and syntax.

For this project, we have adopted a [Code of Conduct](https://github.com/hand-e-fr/OpenHosta/blob/main/CODE_OF_CONDUCT.md) to ensure a respectful and inclusive environment for all contributors. Please take a moment to read it.

## Table of Content

- [OpenHosta](#openhosta)
  - [Table of Content](#table-of-content)
  - [How to install OpenHosta ?](#how-to-install-openhosta-)
  - [Example](#example)
  - [Further information](#further-information)
    - [Contributing](#contributing)
    - [License](#license)
    - [Authors \& Contact](#authors--contact)

---

## How to install OpenHosta ?

You can install OpenHosta either via pip or via GitHub.

```sh
pip install OpenHosta
```

or

```sh
git clone https://github.com/hand-e-fr/OpenHosta.git
```

**See the full installation guide [here](https://github.com/hand-e-fr/OpenHosta/blob/main/docs/installation.md)**

## Example

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
You check OpenHosta's [documentation](https://github.com/hand-e-fr/OpenHosta/blob/main/docs/doc.md) for more detailled informations or exemple

## Further information

### Contributing

We warmly welcome contributions from the community. Whether you are an experienced developer or a beginner, your contributions are welcome.

If you wish to contribute to this project, please refer to our [Contribution Guide](https://github.com/hand-e-fr/OpenHosta/blob/main/CONTRIBUTING.md) and our [Code of Conduct](https://github.com/hand-e-fr/OpenHosta/blob/main/CODE_OF_CONDUCT.md).

Browse the existing [issues](https://github.com/hand-e-fr/OpenHosta/issues) to see if someone is already working on what you have in mind or to find contribution ideas.

### License

This project is licensed under the MIT License. This means you are free to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the software, subject to the following conditions:

  - The text of the license below must be included in all copies or substantial portions of the software.

See the [LICENSE](https://github.com/hand-e-fr/OpenHosta/blob/main/LICENSE) file for more details.

### Authors & Contact

For further questions or assistance, please refer to partner hand-e or contact us directly via github.

**Authors**:
   - Emmanuel Batt: Manager and Coordinator, Founder of Hand-e
   - William Jolivet: DevOps, SysAdmin
   - Léandre Ramos: IA developer
   - Merlin Devillard: UX designer, Product Owner

GitHub: https://github.com/hand-e-fr/OpenHosta

---

Thank you for your interest in our project and your potential contributions!

**The OpenHosta Team**
