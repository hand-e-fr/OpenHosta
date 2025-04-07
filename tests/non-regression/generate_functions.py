# -*- coding: utf-8 -*-
# pip install OpenHosta[predict]
# First install ollama
# then run ollama pull llama3.2:3b

import os
import asyncio

#########################################################
#
# Test model configuration
#
#########################################################

from OpenHosta import config

PORT=11434
#PORT=11436
MODEL_BASE_URL=os.environ.get("MODEL_BASE_URL", f"http://127.0.0.1:{PORT}/v1/chat/completions")
MODEL_API_KEY=os.environ.get("MODEL_API_KEY", "none")
MODEL_NAME = os.environ.get("MODEL_NAME", "gemma2-9b-it")

model=config.OpenAICompatibleModel(
    model=MODEL_NAME,
    max_async_calls=10,
    base_url=MODEL_BASE_URL,
    timeout=120, api_key="none",
    additionnal_headers={"Authorization":MODEL_API_KEY}
)

config.set_default_model(model)

#########################################################
#
# Test sync and async functions
#
#########################################################
# from OpenHosta import ask
# ask("hello")


def example_linear_regression(years : int, profession : str) -> float:
    """
    this function predict the salary based on the profession years.
    """
    pass

from OpenHosta import generate_data, generate_data_async

generator = generate_data(example_linear_regression,  10)

assert len(generator) == 10
assert type(generator.data[0].input[0]) is float

generator_aync = asyncio.run(generate_data_async(example_linear_regression,  10))

assert len(generator_aync) == 10
assert type(generator_aync.data[0].input[0]) is float