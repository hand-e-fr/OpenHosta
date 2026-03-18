# Example: Text Classification

This example demonstrates how to use the `emulate` function combined with an Enum class. OpenHosta natively understands Enums, which restricts the choices an LLM can provide, making it an excellent tool for classification.

## Code

```python
from OpenHosta import emulate
from enum import Enum

class DocumentType(Enum):
    OLD_BOOK = "old_book"
    ARTICLE = "article"
    REPORT = "report"
    THESIS = "thesis"

def classify_document(text_preview: str) -> DocumentType:
    """
    Classifies the document based on the content of the text preview.
    """
    return emulate()

text = "This paper explores the theoretical underpinnings of semantic parsing..."
result = classify_document(text)

print(result) 
# <DocumentType.ARTICLE: 'article'>
```
