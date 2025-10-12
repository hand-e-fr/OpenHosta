from OpenHosta.asynchrone import emulate
from OpenHosta import DefaultModel
from OpenHosta import reload_dotenv

from fastapi import FastAPI

app = FastAPI()

@app.get("/ask/{question}")
async def home(question: str = "Introduce yourself and say hello") -> str:
    """
    A simple FastAPI application that returns an answer to the question.
    """
    return await emulate()

@app.get("/reload_config")
async def reload_config():
    reload_dotenv()
    return {"status": "dotenv reloaded"}

@app.get("/")
async def root():
    return DefaultModel.api_parameters | {"model": DefaultModel.model_name} | {"base_url": DefaultModel.base_url}

async def produce_a_joke_about(topic: str) -> str:
    """
    Produce a joke about the given topic.
    """
    return await emulate()

@app.get("/joke/{topic}")
async def joke(topic: str) -> str:
    """
    A simple FastAPI application that returns a joke about the topic.
    """
    return await produce_a_joke_about(topic)

# To run: uvicorn simple_fastapi:app --reload

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)