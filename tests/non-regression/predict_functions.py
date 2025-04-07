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
from OpenHosta import ask
ask("hello")

from typing import Literal

Regions = Literal["center", "Nord", "Sud", "Est", "Ouest"]
Month = Literal["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]

from OpenHosta import predict, predict_async

def temperature_in_spain(month: Month, region: Regions) -> float:
    """
    this function returns the averge temperatire in °C.
    """
    return predict()

from OpenHosta import clear_training

# this force data generation and training
clear_training(temperature_in_spain)

prediction = temperature_in_spain("Janvier", "center")

assert type(prediction) is float

async def temperature_in_france(month: Month, region: Regions) -> float:
    """
    this function returns the averge temperatire in °C.
    """
    return await predict_async()

# this force data generation and training
clear_training(temperature_in_france)

prediction = asyncio.run(temperature_in_france("Mai", "paris"))

assert type(prediction) is float
assert prediction > 0
assert prediction < 35

import time
t0 = time.time()
for i in range(1000):
    prediction = temperature_in_france("Mai", "paris")
t1 = time.time()

assert t1-t0 < 50, f"Prediction time was surprinsingly long: {t1-t0}s. This is more than 50ms per call."
