# Documentation
___

**You will find above a short desciption with examples to understand how OpenHosta works.Hope you will like it ! :)**

*if you want to test it move the `example.ipynb` file in `src`*

#### Import the emulator

```python
from OpenHosta import emulator

llm = emulator()
```

#### Let's create a new function. In fact, you need to place the decorator `llm.emulate` above the function. A decorator is used here to take the function as a parameter.

Your function should be prototyped like this

```python
@llm.emulate
def AI_find_occurence_of_a_word(word :str, text: str) -> int:
    """
    This function takes a word and a text and returns
    the number of times the word appears in the text.
    """
    pass

AI_find_occurence_of_a_word("hello", "hello world hello") # 2
```

output :
```bash
2
```
___

#### If you want to improve your prompt, see what's the AI understand and see a vizualizer of the reasonning please use the decorator `llm.enhance`
Your function should be prototiped like this : 

```python
@llm.enhance
def AI_find_occurence_of_a_word_enhance(word :str, text: str) -> int:
    """
    This function takes a word and a text and returns
    the number of times the word appears in the text.
    """
    pass

AI_find_occurence_of_a_word_enhance("hello", "hello world hello")
```

A directory `.openhosta` will appears and he will contain :

**A mermaid vizualizer**
```mermaid
graph LR
    A[Start] --> B[Receive inputs: word and text]
    B --> C{Are inputs valid?}
    C -- No --> D[Return error]
    C -- Yes --> E[Convert both inputs to lowercase]
    E --> F[Remove punctuation from text]
    F --> G[Split text into words]
    G --> H[Count exact matches of the word]
    H --> I[Return the count]
    I --> J[End]
```

**A understanding of the input prompt and an possible update version for more precision (*that you need to change manually if you agree this*).**
___
- **Enhanced prompt:**
This function takes two inputs: a word (string) and a text (string). It returns an integer representing the number of times the specified word appears in the given text. The function should be case-insensitive, meaning it should count occurrences of the word regardless of whether it is in uppercase or lowercase. Additionally, the function should handle punctuation properly, ensuring that words followed by punctuation marks are still counted correctly. The function should also include error handling to manage cases where the inputs are not strings or are empty.
- **How to improve your prompt:**
The prompt is clear but lacks specificity in handling edge cases and punctuation. It also doesn't specify how to handle different forms of the word, such as plural or possessive forms. Furthermore, it doesn't mention whether the function should count overlapping occurrences of the word. The prompt could benefit from more detailed requirements to ensure robustness and accuracy.
- **Improvemed prompt suggestion:**
This function takes two inputs: a word (string) and a text (string). It returns an integer representing the number of times the specified word appears in the given text. The function should be case-insensitive, meaning it should count occurrences of the word regardless of whether it is in uppercase or lowercase. It should handle punctuation properly, ensuring that words followed by punctuation marks are still counted correctly. The function should not count overlapping occurrences of the word. Additionally, the function should include error handling to manage cases where the inputs are not strings or are empty. It should also handle different forms of the word, such as plural or possessive forms, by considering only exact matches of the word.`
___

#### To receive information of the sequences you need to use the `llm.oracle` decorator (return a json file)
function should be prototyped like this

```python
@llm.oracle
def analyse_data(word :str, text: str) -> int:

    result_1 = AI_find_occurence_of_a_word(word, text)
    result_2 = text.count(word)
    dataset = [result_1, result_2]

    if result_1 == result_2:
        return dataset, 0 # Return 0 or True if the results are the same
    else:
        return dataset, 1 # Return 1 or False if the results are different

analyse_data("hello", "hello world hello")
```

**The Json looks like this**

```json
{
    "Version": 1.0,
    "Model used": "gpt-4o",
    "Id session": "fc4e1b32-b5ef-413f-9812-a3388945e844",
    "Timestamp": 1720448026,
    "func_call": "analyse_data(hello, hello world hello)",
    "func_hash": "7d6c10838b87595afcfc62402068bbc5",
    "Tag output": 0,
    "Data": [
        2,
        2
    ]
}
```