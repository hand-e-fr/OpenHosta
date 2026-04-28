
from dataclasses import dataclass
from OpenHosta import emulate_async
from OpenHosta import config

config.DefaultModel.model_name="qwen3.5:4b"
config.DefaultModel.base_url="http://localhost:11434"
config.DefaultModel.api_parameters |= {"reasoning": {"effort": "none"}}

@dataclass
class Step:
    id:int
    description:str
    parent_id:int|None

@dataclass
class Answer:
    hypothesis_with_uncertainty:list[tuple[str,float]]
    rational_steps:list[Step]
    conclusion:str

async def answer(question:str) -> Answer:
    """
    Answer a question using a well structured thinking
    In the hypothesis_with_uncertainty, import only hypothesis with uncertainty above 5%. All hypothesis used in the rational_steps must be included in the hypothesis_with_uncertainty.
    In rational_steps, having only one step is acceptable if there is only one hypothesis and answer is obviouse given that hypothesis.
    """
    return await emulate_async()

import asyncio
result = asyncio.run(answer("Quelle est la capitale de la France ?"))
print(result)