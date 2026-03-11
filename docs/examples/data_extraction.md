# Example: Data Extraction

When you need to extract highly reliable and structured data from an unstructured text, nothing beats combining OpenHosta's `emulate` with `Pydantic` and `dataclasses`.

## Code

```python
from OpenHosta import emulate
from dataclasses import dataclass

@dataclass
class Client:
    name: str
    surname: str
    company: str
    email: str
    town: str
    address: str

def extract_client_info(text: str) -> Client:
    """
    Parses an email text and extracts client contact information.
    """
    return emulate()

email_content = """
FROM: sebastien@somecorp.com
TO: shipment@hand-e.fr
Object: do not send mail support@somecorp.com

Hello bob, I am Sebastian from Paris, France. Could you send me a sample of your main product? 
My office address is 3 rue de la république, Lyon 1er
"""

client_info = extract_client_info(email_content)
print(client_info)
# Client(name='Sebastian', surname='None', company='somecorp.com', email='sebastien@somecorp.com', town='Lyon', address='3 rue de la république, Lyon 1er')
```
