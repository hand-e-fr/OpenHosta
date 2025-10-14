# OpenHosta 

v3.0 - Integrates Inria Comments

<br/>You can read the doc or directly have a look at [tests files](https://github.com/hand-e-fr/OpenHosta/tree/main/tests/) for multiples exemples.

OpenHosta is a powerful Python extension designed to seamlessly integrate semantic capabilities seen in Large Language Models (LLMs) into tradictional development environments, enabling AI-powered function emulation that maintains native Python syntax and paradigms. Its strength lies in its simplicity and flexibility, allowing developers to easily create AI-enhanced applications while maintaining clean, Pythonic code structure.

OpenHosta can run fully offline with a local model, or use a remote model via API key.

**- The future of development is human -**

For this project, we have adopted a [Code of Conduct](https://github.com/hand-e-fr/OpenHosta/blob/main/CODE_OF_CONDUCT.md) to ensure a respectful and inclusive environment for all contributors. Please take a moment to read it.

The simplest usage of OpenHosta is to allow semantic tests in your code, like this:

```python
from OpenHosta import test

sentence = "You are an nice person."
# You shall try with this too:
# sentence = "You are a stupid #@!!~uk."

if test(f"this contains an insult: {sentence}"):
    print("The sentence is considered an insult.")
else:
    print("The sentence is not considered an insult.")

# The sentence is not considered an insult.
```

But the most powerful feature of OpenHosta is the `emulate` function, which allows you to define a function with a docstring and let OpenHosta implement it for you using AI. The `emulate` function supports basic python types, dataclasses, pydantic, enums and Images. You can use all these types as input and output of the function (except for Images which can only be input).

```python
from OpenHosta import emulate

from enum import Enum
class DocumentType(Enum):
    OLD_BOOK = "old_book"
    ARTICLE = "article"
    REPORT = "report"
    THESIS = "thesis"

from PIL.Image import Image, open

def classify_document(page:Image)->DocumentType:
    """
    This function classifies the document based on the content of the page givent in parameter.
    
    Arguments:
    page: An image of the document page to classify.

    Returns:
    DocumentType: The type of the document
    """
    return emulate()

import requests
url=r"https://www.inria.fr/sites/default/files/2024-01/A_outil_innovant_caracte%CC%81riser_plantes_1827x1026_bonnier-2.png"
img = open(requests.get(url, stream=True).raw)

result = classify_document(img)

result
# <DocumentType.OLD_BOOK: 'old_book'>
```

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

We encourage you to use a virtual environment. You can create one with:
```sh
python -m venv .venv
source .venv/bin/activate # On Windows use `.venv\Scripts\activate`
```

Then you can install OpenHosta with one of the following commands:

```sh
pip install OpenHosta
```

or

```sh
pip install "git+https://github.com/hand-e-fr/OpenHosta.git"
```

or for a specific branch

```sh
pip install "git+https://github.com/hand-e-fr/OpenHosta.git@unstable" # for the latest unstable version
```

**See the full [installation guide](https://github.com/hand-e-fr/OpenHosta/blob/main/docs/installation.md)**

## Example

You shall set your API credentials either via environment variables or directly in your code.
For now we assume that you have an OpenAI API key and that you have set it in .env like this:

```env
# This is the content of your .env file to be placed in the root of your project
OPENHOSTA_DEFAULT_MODEL_NAME="gpt-4.1"
OPENHOSTA_DEFAULT_MODEL_API_KEY="put-your-api-key-here"
```

You can also use a local model using ollama. See [documentation](https://github.com/hand-e-fr/OpenHosta/blob/main/docs/installation.md#local-models).

```python
from OpenHosta import emulate

def translate(text:str, language:str)->str:
    """
    This function translates the text in the “text” parameter into the language specified in the “language” parameter.
    """
    return emulate()

result = translate("Hello World!", "French")

print(result)
# Bonjour le monde !
```

You check [OpenHosta's documentation](https://github.com/hand-e-fr/OpenHosta/blob/main/docs/doc.md) for more detailled informations or exemple

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
