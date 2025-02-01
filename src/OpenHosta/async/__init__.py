from ..exec.ask import ask_async as ask
from ..exec.emulate import emulate_async as emulate
from ..exec.thinkof import thinkof_async as thinkof

from ..utils.import_handler import is_predict_enabled

if is_predict_enabled:
    from ..exec.predict.predict import predict_async as predict
    from ..exec.generate_data import generate_data_async as generate_data

all = (
    "ask",
    "emulate",
    "thinkof",
    "predict",
    "generate_data",
)
