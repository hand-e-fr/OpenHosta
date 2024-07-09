# OpenHosta 
v0.1.0 - Open-Source Project

**- The future of development is human -**

Welcome to the OpenHosta documentation, a powerful tool that facilitates the integration of specific functions into a project while allowing beginners to clearly understand the project. OpenHosta is used to emulate functions using AI, compare their results with coded functions, and generate detailed logs for each function call.

For this project, we have adopted a [Code of Conduct](CODE_OF_CONDUCT.md) to ensure a respectful and inclusive environment for all contributors. Please take a moment to read it.

## Table of Content

- [OpenHosta](#openhosta)
  - [Table of Content](#table-of-content)
  - [How to install OpenHosta ?](#how-to-install-openhosta-)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
  - [How to use OpenHosta ?](#how-to-use-openhosta-)
    - [Usage](#usage)
    - [Features](#features)
    - [Configuration](#configuration)
  - [Further information](#further-information)
    - [Contributing](#contributing)
    - [License](#license)
    - [Authors \& Contact](#authors--contact)

---

## How to install OpenHosta ?

### Prerequisites

1. **Python 3.8+**
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
   - **API Key**: Log in to your OpenAI account from [openai.com](https://openai.com/), then create your API key.

### Installation

1. Clone the **Git repository** to your local machine using the following command:

```bash
git clone git@github.com:hand-e-fr/OpenHosta-dev.git
```

2. Navigate to the **directory** of the cloned project:

```bash
cd OpenHosta-dev
```

3. Ensure you have installed the necessary **dependencies** before starting.

```bash
pip install -r requirements.txt
```

---

## How to use OpenHosta ?

### Usage

Make sure to import the library.

```python
import OpenHosta
```

Here is a simple usage example:

```python
llm = OpenHosta.emulator()    # You need to put your API key and the model as parameters

@llm.emulate                  # or "@llm.enhance"
def example(a:int, b:int)->int:  # Put your prompt in the docstrings
   """
   This is a very precise example prompt.  
   """
   pass                       # The function therefore contains no instructions

example(4, 2)                 # Call the function to activate the decorator      
```

### Features

```python
llm = emulator()
```

- `llm` contains three main decorators. Decorators in Python are functions that modify the behavior of other functions or methods, allowing for additional functionalities in a modular way:
  - `@llm.emulate`: Decorates a function to emulate its execution by an AI. You can choose the model using your API key.
  - `@llm.enhance`: Decorates a function and generates a Mermaid diagram to visualize and understand the model's reasoning, as well as a markdown help file to improve the function's prompt. Everything is stored in the `.openhosta` directory at the root of the working directory.

### Configuration

The `emulator` class can have four parameters:
   - `model`: LLM model to which the program will send its requests
   - `creativity` & `diversity`: Correspond to the "temperature" and "top_p" parameters of LLMs. These values range from 0 to 1 (inclusive). For more information, please refer to the official [OpenAI documentation](https://openai.com/)
   - `api_key`: Your own api-key to communicate with the llm

Example:
```python
llm = OpenHosta.emulator(
   model="gpt-4o", 
   api_key="This_is_my_api_key",
   creativity=0.7,
   diversity=0.5
)
```

---

## Further information

### Contributing

We warmly welcome contributions from the community. Whether you are an experienced developer or a beginner, your contributions are welcome.

If you wish to contribute to this project, please refer to our [Contribution Guide](CONTRIBUTING.md) and our [Code of Conduct](CODE_OF_CONDUCT.md).

Browse the existing [issues](https://github.com/hand-e-fr/OpenHosta-dev/issues) to see if someone is already working on what you have in mind or to find contribution ideas.

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
   - Merlin Devillard: UX designer, Prompt Engineer

---

Thank you for your interest in our project and your potential contributions!

**The OpenHosta Team**