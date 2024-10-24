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
    loss: Optional[str] = None
    epochs: Optional[int] = None
    get_loss: float = 0.0
    batch_size: Optional[int] = None
    force_train: bool = False
    norm_max: Optional[float] = None
    norm_min: Optional[float] = None
    continue_training: bool = False
    normalization: bool = False
