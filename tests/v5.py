from openhosta import BackendModel, Guarded, guard_info

backend = BackendModel(
    provider="openai_compatible",
    model_name="gemma4:12b",
    base_url="http://192.168.1.188:11434/v1",
    api_key="none",
)

from typing import Iterator

@backend.infer(tags=[])
def tell_a_story() -> Iterator[str]:
    ...

st = tell_a_story()
g = guard_info(st)
