# Example: Local OCR with Ollama

This example demonstrates how to perform Optical Character Recognition (OCR) locally without sending your sensitive documents to a remote API. We achieve this using OpenHosta alongside the `glm-ocr` model served locally via Ollama.

## prerequisites
Make sure you have Ollama installed and have pulled the model beforehand:

```bash
ollama run glm-ocr
```

## Code

```python
from OpenHosta import emulate, OpenAICompatibleModel, config
from PIL.Image import Image, open
import requests

# 1. Configure the Local Ollama Model targeting glm-ocr
ocr_model = OpenAICompatibleModel(
    model_name="glm-ocr",
    base_url="http://localhost:11434/v1",
    api_key="none"
)

# Set it globally so `emulate` uses it by default
config.DefaultModel = ocr_model

# 2. Define our OCR extraction function using PIL.Image
def read_invoice_total(invoice_image: Image) -> float:
    """
    Extracts the final total amount from an image of a scanned invoice.
    """
    return emulate()

# 3. Load an image (from a local file or URL)
url = "https://raw.githubusercontent.com/hand-e-fr/OpenHosta/main/tests/data/sample_receipt.jpg"
image_payload = open(requests.get(url, stream=True).raw)

# 4. Perform local OCR!
total_amount = read_invoice_total(image_payload)

print(f"Extracted Total: {total_amount}")
# e.g., Extracted Total: 145.20
```

This local execution means zero latency costs and complete data privacy, natively supporting image payloads sent straight into the OpenHosta runtime.
