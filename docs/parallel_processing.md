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

---

## 3. Advanced Data Pipelines: Stream, Triage, and Gather

OpenHosta excels when dealing with massive data dumps by combining iterators, sanity checks, and asynchronous parallelism. This powerful architecture generally follows a 4-step pattern:

1. **Extraction (Iterator)**: Use `emulate` to yield single elements one-by-one from a large, unstructured text blob to avoid waiting for the entire parsing to complete.
2. **Sanity Checks**: Apply a mix of fast, pure Python logic (e.g., regex, keyword search) and robust LLM-based logic (via `emulate_async`) to validate each yielded element.
3. **Triage**: Group the elements into structured objects or separate lists (e.g., `valid_items` vs `rejected_items`).
4. **Gather & Execute**: Use `gather_data` to concurrently execute any pending async LLM calls nested inside your valid data structures, ensuring maximum throughput.

Here are three real-life implementations of this pattern.

### Example A: Legal Contract Analysis (Risk Assessment)

In this scenario, we stream clauses from a massive contract, apply Python sanity checks to filter out short boilerplate text, use an LLM check to see if the clause is legally binding, and finally assess the risk of all valid clauses concurrently.

```python
import asyncio
from typing import Iterator
from pydantic import BaseModel
from OpenHosta import emulate, emulate_async, gather_data

class Clause(BaseModel):
    title: str
    content: str
    
class RiskAssessment(BaseModel):
    clause_title: str
    risk_score: int
    reason: str

def extract_clauses(contract_text: str) -> Iterator[Clause]:
    """Yield every distinct liability or obligation clause from the contract."""
    return emulate()

async def is_legally_binding_async(clause_content: str) -> bool:
    """Return True if the clause contains legally binding obligations, False otherwise."""
    return await emulate_async()

async def score_legal_risk_async(clause_content: str, company_policy: str) -> RiskAssessment:
    """Evaluate the legal risk of this clause against the company policy."""
    return await emulate_async()

async def process_contract(contract_text: str, company_policy: str):
    valid_assessments = []
    rejected_clauses = []

    # 1. Extraction (Streamed)
    for clause in extract_clauses(contract_text):
        
        # 2. Mixed Sanity Checks
        # Fast Python Check
        if len(clause.content) < 50:
            rejected_clauses.append({"clause": clause, "reason": "Too short / Boilerplate"})
            continue
            
        # LLM Check
        is_binding = await is_legally_binding_async(clause.content)
        
        # 3. Triage
        if not is_binding:
            rejected_clauses.append({"clause": clause, "reason": "Not legally binding"})
        else:
            # Prepare the pending async task for the valid clause
            valid_assessments.append(score_legal_risk_async(clause.content, company_policy))

    # 4. Gather & Execute
    # The list contains pending coroutines. We resolve them all in parallel!
    gather_data(valid_assessments, batch_size=20)
    
    return {
        "assessments": valid_assessments,
        "rejected": rejected_clauses
    }

# Run the pipeline
# result = asyncio.run(process_contract(huge_contract_text, our_policy))
```

### Example B: Customer Support Triage (E-commerce)

Stream through a messy forum thread of user reviews, drop the 5-star reviews using standard Python logic, let the LLM decide if a complaint is actionable, and then concurrently route and draft apology emails for all actionable complaints.

```python
import asyncio
from typing import Iterator
from dataclasses import dataclass
from OpenHosta import emulate, emulate_async, gather_data

@dataclass
class Feedback:
    username: str
    rating: int  # 1 to 5
    text: str

@dataclass
class TicketDispatch:
    username: str
    assigned_department: str  # Pending async call
    draft_response: str       # Pending async call

def extract_feedback(forum_thread: str) -> Iterator[Feedback]:
    """Extract individual user reviews from the messy forum thread."""
    return emulate()

async def is_actionable_complaint_async(feedback_text: str) -> bool:
    """Determine if the feedback requires customer support intervention."""
    return await emulate_async()

async def assign_department_async(feedback_text: str) -> str:
    """Assign the ticket to: 'Shipping', 'Billing', 'Technical', or 'General'."""
    return await emulate_async()

async def draft_apology_async(feedback_text: str) -> str:
    """Draft a polite, empathetic apology email addressing the specific issue."""
    return await emulate_async()

def process_support_thread(forum_thread: str):
    dispatched_tickets = []
    ignored_feedback = []

    # 1. Extraction
    for fb in extract_feedback(forum_thread):
        
        # 2. Python Sanity Check
        if fb.rating == 5:
            ignored_feedback.append({"feedback": fb, "reason": "Positive Review"})
            continue
            
        # 3. LLM Check & Triage (Notice we use asyncio.run for the sync environment)
        is_actionable = asyncio.run(is_actionable_complaint_async(fb.text))
        
        if not is_actionable:
            ignored_feedback.append({"feedback": fb, "reason": "Not Actionable / Rant"})
        else:
            # We construct our complex data structure with nested pending coroutines
            dispatch = TicketDispatch(
                username=fb.username,
                assigned_department=assign_department_async(fb.text),
                draft_response=draft_apology_async(fb.text)
            )
            dispatched_tickets.append(dispatch)

    # 4. Gather & Execute
    # Automatically traverse the list of TicketDispatch objects and resolve the pending async strings
    gather_data(dispatched_tickets, batch_size=15)
    
    return dispatched_tickets, ignored_feedback
```

### Example C: Financial Earnings Call Analysis

Stream executive statements from a long transcript. Use Python keyword searches to drop irrelevant sentences. Use the LLM to verify if the statement is forward-looking. Finally, concurrently evaluate the predicted stock sentiment for all valid statements.

```python
import asyncio
from typing import Iterator
from pydantic import BaseModel
from OpenHosta import emulate, emulate_async, gather_data

class Statement(BaseModel):
    executive_name: str
    quote: str

class MarketSentiment(BaseModel):
    sentiment: str  # "Bullish", "Bearish", "Neutral"
    confidence_score: int # 1 to 100

def extract_statements(transcript: str) -> Iterator[Statement]:
    """Yield all distinct sentences spoken by executives in the transcript."""
    return emulate()

async def is_forward_looking_async(quote: str) -> bool:
    """Check if the quote discusses future expectations, guidance, or projections."""
    return await emulate_async()

async def predict_stock_sentiment_async(quote: str) -> MarketSentiment:
    """Analyze the potential market impact of this forward-looking statement."""
    return await emulate_async()

async def analyze_earnings_call(transcript: str):
    financial_keywords = ["revenue", "growth", "launch", "guidance", "margin", "loss"]
    
    analyzed_statements = {}
    archived_statements = []

    # 1. Extraction
    for stmt in extract_statements(transcript):
        
        # 2. Python Check: Keyword Filtering
        if not any(kw in stmt.quote.lower() for kw in financial_keywords):
            archived_statements.append({"quote": stmt.quote, "reason": "No financial keywords"})
            continue
            
        # 3. LLM Check & Triage
        if not await is_forward_looking_async(stmt.quote):
            archived_statements.append({"quote": stmt.quote, "reason": "Historical/Factual, not forward-looking"})
        else:
            # Store in a dictionary where values are pending coroutines
            analyzed_statements[stmt.quote] = predict_stock_sentiment_async(stmt.quote)

    # 4. Gather & Execute
    # Resolves all dictionary values in parallel
    await gather_data_async(analyzed_statements, batch_size=10)
    
    return {
        "impact_analysis": analyzed_statements,
        "archived": archived_statements
    }
```
