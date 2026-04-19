# Parallel Processing and Batch Context

When dealing with a vast amount of documents, or extracting information continuously in a backend server context, OpenHosta provides built-in parallel processing features. Using `emulate_async` prevents UI blocking, and the `gather_data` module simplifies multi-processing workloads without manually tampering with event loops or explicit tasks.

## 1. Extracting Invoices Using Async Tasks

You can use `emulate_async` alongside `dataclasses` and standard `asyncio.gather` for highly concurrent validation. We define a data structure for invoice sender coordinates, and extract it instantly from multiple unstructured snippets.

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

## 2. Declarative Parallelism with gather_data

OpenHosta provides an elegant, explicit data processor called gather_data (and its async counterpart gather_data_async). This approach simplifies multi-processing workloads without manually tampering with event loops or explicit tasks. It scans standard Python data structures and resolves any pending asynchronous calls in-place.

```python
from OpenHosta import emulate_async
from OpenHosta import gather_data 

async def name_list(topic: str) -> list[str]:
    """Generates three names related to the topic."""
    return await emulate_async()
    
async def first_name(person: str) -> str:
    """Returns the first name of the famous person."""
    return await emulate_async()
    
async def alt_name(person: str) -> str:
    """Returns an alternative alias of the person."""
    return await emulate_async()

# Create a standard Python dictionary
my_data = {}

# Case A: Function inherently returning a list
my_data["A"] = name_list("Macron")

# Case B: Python Array encapsulating multiple separate Async Coroutines
my_data["B"] = [first_name("Trump"), alt_name("Trump")]

# Case C: Inserting strict generic static data
my_data["C"] = "Static Data"

# Resolves all pending coroutines in-place. 
# Batch size allows processing N queries in a sliding window to prevent rate limits.
gather_data(my_data, batch_size=10, max_delay=120)

# After the function call, dictionary items are completely resolved!
print("Final Result :", my_data)
# Output: {'A': ['Emmanuel', 'Jean', ...], 'B': ['Donald', 'The Don'], 'C': 'Static Data'}
```

> Note for Async Environments (FastAPI, Jupyter): If you are running inside an existing event loop, use the asynchronous version: `await gather_data_async(my_data, batch_size=10)`.

