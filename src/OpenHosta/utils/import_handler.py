from __future__ import annotations

all = (
    "is_pydantic"
    "is_predict"
)

is_pydantic = False
try:
    import pydantic
    is_pydantic = True
except ImportError:
    is_pydantic = False

is_predict = False
try:
    import torch
    import numpy
    is_predict = True
except ImportError:
    is_predict = False
