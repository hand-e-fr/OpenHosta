from dataclasses import dataclass, field
from typing import Any, List, Dict, Optional

@dataclass
class PredictConfig:
    encoder: Optional[Any] = None
    decoder: Optional[Any] = None
    verbose: bool = False
    prediction: List[Any] = field(default_factory=list)
    complexity: Optional[int] = None
    config: Optional[Dict[str, Any]] = None
    optimizer: Optional[str] = None
    loss_method: Optional[str] = None
    loss_value: float = 0.0
    epochs: Optional[int] = None
    batch_size: Optional[int] = None
    force_train: bool = False
    norm_max: Optional[float] = None
    norm_min: Optional[float] = None
    continue_training: bool = False
    normalization: bool = False
