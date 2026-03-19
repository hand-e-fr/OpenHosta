# Example: Parallel Processing and Batch Context

When dealing with a vast amount of documents, or extracting information continuously in a backend server context, using `emulate_async` prevents UI blocking and increases thoroughput.

## 1. Extracting Invoices Using Async Tasks

This example demonstrates how to use `emulate_async` alongside `dataclasses` and `asyncio.gather` for highly concurrent validation. We define a data structure for invoice sender coordinates, and extract it instantly from multiple unstructured snippets.

```python
import asyncio
from dataclasses import dataclass
from OpenHosta import emulate_async

@dataclass
class InvoiceSender:
    company_name: str
    address: str
    city: str
    postal_code: str
    siret_number: str

async def extract_sender_coordinates(invoice_text: str) -> InvoiceSender:
    """
    Parses the invoice text to find the exact coordinates of the invoice sender.
    Does not extract the recipient!
    """
    return await emulate_async()

async def main():
    invoice_1 = "From: ACME Corp Ltd. 12 rue de la Paix, Paris, 75000. SIRET: 123456789. Billed to: John Doe."
    invoice_2 = "Facture envoyée le 12 Mars. Expéditeur: BricoPro. 5 impasse des artisans, 69002 Lyon. N° SIRET : 987654321."

    # Using asyncio.create_task or asyncio.gather allows both requests to be sent
    # to the API / Local model concurrently!
    tasks = [
        asyncio.create_task(extract_sender_coordinates(invoice_1)),
        asyncio.create_task(extract_sender_coordinates(invoice_2))
    ]

    results = await asyncio.gather(*tasks)

    for res in results:
        print(f"Company: {res.company_name} | City: {res.city} | SIRET: {res.siret_number}")

# Run the event loop
if __name__ == "__main__":
    asyncio.run(main())
```

## 2. The BatchDataContext Manager (Coming soon)

OpenHosta provides an elegant context manager under development `BatchDataContext` designed exclusively to simplify multi-processing workloads without manually tampering with event loops or explicit tasks.

```python
from OpenHosta import emulate_async
from OpenHosta import BatchDataContext 

async def name_list(topic: str) -> list[str]:
    """Generates three names related to the topic."""
    return await emulate_async()
    
async def first_name(person: str) -> str:
    """Returns the first name of the famous person."""
    return await emulate_async()
    
async def alt_name(person: str) -> str:
    """Returns an alternative alias of the person."""
    return await emulate_async()

# Batch size allows processing N queries in a sliding window
with BatchDataContext(batch_size=10) as my_data:
    # Case A: Function inherently returning a list
    my_data["A"] = name_list("Macron")
    
    # Case B: Python Array encapsulating multiple separate Async Coroutines
    my_data["B"] = [first_name("Trump"), alt_name("Trump")]
    
    # Case C: Inserting strict generic static data
    my_data["C"] = "Static Data"

# Block closes, wait occurs, then dictionary items are completely resolved!
print("Résultat final :", my_data)
```
