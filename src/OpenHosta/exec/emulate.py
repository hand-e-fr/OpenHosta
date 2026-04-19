from __future__ import annotations

from typing import Any, Optional

from ..defaults import config

from ..core.inspection import get_caller_frame, get_hosta_inspection

from ..pipelines import OneTurnConversationPipeline


def emulate(
        *,
        pipeline: Optional[OneTurnConversationPipeline] = config.DefaultPipeline,
        force_llm_args: Optional[dict] = {},
        ) -> Any:
    """
    Emulates a function's behavior using a language model.

    Automatically adapts to the calling context:

    - ``def f() -> T: return emulate()``
      Synchronous value — calls the LLM and returns the fully resolved value.

    - ``def f() -> Iterator[T]: yield emulate()``
      Synchronous generator — streams items from the LLM, yielding each typed
      item as its ```python``` block completes.

    Args:
        pipeline: The pipeline used for emulation. If None, uses the default one.
        force_llm_args: Additional keyword arguments to pass to the language model.

    Returns:
        Any: The emulated return value, or a generator of items in generator mode.
    """
    # You can retrieve this frame using get_last_frame(your_emulated_function)
    frame = get_caller_frame()

    # Get everything about the function you are emulating
    inspection = get_hosta_inspection(frame)

    # Detect whether the caller is a generator function
    is_generator = inspection.analyse.is_generator
    item_type = inspection.analyse.item_type

    if is_generator:
        # Return a sync generator; the caller yields it with `yield from emulate()`
        return pipeline.execute_stream(inspection, force_llm_args, item_type)
    else:
        # Existing behaviour — synchronous single value
        return pipeline.execute(inspection, force_llm_args)


async def emulate_async(
        *,
        pipeline: Optional[OneTurnConversationPipeline] = config.DefaultPipeline,
        force_llm_args: Optional[dict] = {},
        ) -> Any:
    """
    Emulates a function's behavior using a language model (async version).

    Automatically adapts to the calling context:

    - ``async def f() -> T: return await emulate_async()``
      Asynchronous value — awaits the LLM response and returns the resolved value.

    - ``async def f() -> AsyncIterator[T]: yield emulate_async()``
      Async generator — streams items via the async LLM API.

    Args:
        pipeline: The pipeline used for emulation. If None, uses the default one.
        force_llm_args: Additional keyword arguments to pass to the language model.

    Returns:
        Any: The emulated return value, or an async generator of items.
    """
    frame = get_caller_frame()
    inspection = get_hosta_inspection(frame)

    is_generator = inspection.analyse.is_generator
    item_type = inspection.analyse.item_type

    if is_generator:
        # Return an async generator; the caller does `async for x in await emulate_async(): yield x`
        return pipeline.execute_stream_async(inspection, force_llm_args, item_type)
    else:
        # Existing behaviour — async single value
        return await pipeline.execute_async(inspection, force_llm_args)
