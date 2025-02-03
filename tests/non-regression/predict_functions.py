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
PORT=11436
MODEL_BASE_URL=os.environ.get("MODEL_BASE_URL", f"http://127.0.0.1:{11436}/v1/chat/completions")
MODEL_API_KEY=os.environ.get("MODEL_API_KEY", "none")

#TODO: tester avec json_output = False
#TODO: tester models r1

model=config.Model(
    model="llama3.2:3b",
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

from OpenHosta import predict, predict_async

def example_linear_regression(years : int, profession : str) -> float:
    """
    this function predict the salary based on the profession years.
    """
    return predict(verbose=2)

print(example_linear_regression(1, "engineer"))
