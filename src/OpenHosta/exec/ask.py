from __future__ import annotations

from typing import Any, Optional

from ..defaults import Model, config

from ..core.meta_prompt import MetaPrompt
    
def ask(
    user_message: str,
    *unnamed_other_args,
    system: Optional[str] = "You are a helpful assistant.",
    model: Optional[Model] = None,
    force_json_output=False,
    force_llm_args: Optional[dict] = {},
    **named_other_args,
) -> Any:

    if model is None:
        # Create a dummy inspection to detect required capabilities
        from ..core.inspection import Inspection
        from ..core.analizer import AnalyzedFunction
        
        # We simulate a function that takes the extra args to detect images
        dummy_analyse = AnalyzedFunction(name="ask", args=[], type=str, doc=user_message)
        # Add args for image detection
        from ..core.analizer import AnalyzedArgument
        for i, arg in enumerate(unnamed_other_args):
            dummy_analyse.args.append(AnalyzedArgument(name=f"arg{i}", value=arg, type=None))
        for key, arg in named_other_args.items():
            dummy_analyse.args.append(AnalyzedArgument(name=key, value=arg, type=None))
            
        dummy_inspection = Inspection(None, None, dummy_analyse)
        model = config.DefaultPipeline.push_choose_model(dummy_inspection)

    message = _build_ask_message(user_message, unnamed_other_args, named_other_args, system)

    force_llm_args["force_json_output"] = force_json_output

    response_dict = model.api_call(messages=message,
        llm_args=force_llm_args
    )

    response = model.get_response_content(response_dict)

    # No type detection
    answer = response

    return answer
    

async def ask_async(
    user_message: str,
    *unnamed_other_args,
    system: Optional[str] = "You are a helpful assistant.",
    model: Optional[Model] = None,
    force_json_output=False,
    force_llm_args: Optional[dict] = {},
    **named_other_args,
) -> Any:

    if model is None:
        # Create a dummy inspection to detect required capabilities
        from ..core.inspection import Inspection
        from ..core.analizer import AnalyzedFunction
        from ..core.analizer import AnalyzedArgument
        
        dummy_analyse = AnalyzedFunction(name="ask", args=[], type=str, doc=user_message)
        for i, arg in enumerate(unnamed_other_args):
            dummy_analyse.args.append(AnalyzedArgument(name=f"arg{i}", value=arg, type=None))
        for key, arg in named_other_args.items():
            dummy_analyse.args.append(AnalyzedArgument(name=key, value=arg, type=None))
            
        dummy_inspection = Inspection(None, None, dummy_analyse)
        model = config.DefaultPipeline.push_choose_model(dummy_inspection)

    message = _build_ask_message(user_message, unnamed_other_args, named_other_args, system)

    force_llm_args["force_json_output"] = force_json_output

    response_dict = await model.api_call_async(
        messages=message,
        llm_args=force_llm_args
    )

    response = model.get_response_content(response_dict)
    
    # No type detection
    answer = response

    return answer


def _build_ask_message(
    user_message: str,
    unnamed_other_args,
    named_other_args: dict,
    system: Optional[str],
) -> list:
    """Shared message-building logic for ask_stream / ask_stream_async."""
    message = []
    if system is not None:
        message.append({"role": "system", "content": [{"type": "text", "text": system}]})

    message.append({"role": "user", "content": [{"type": "text", "text": user_message}]})

    named_other_args = dict(named_other_args)
    for i, arg in enumerate(unnamed_other_args):
        named_other_args[f"arg{i}"] = arg

    for key, arg in named_other_args.items():
        try:
            import PIL.Image, base64, io
            pil_ok = True
        except ImportError:
            pil_ok = False

        if pil_ok and isinstance(arg, PIL.Image.Image):
            buffered = io.BytesIO()
            arg.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
            message[-1]["content"].append(
                {"type": "image_url", "image_url": {"url": "data:image/png;base64," + img_str}}
            )
        else:
            if len(message) == 1:
                message = [{"role": "system", "content": [{"type": "text", "text": ""}]}] + message
            message[0]["content"][0]["text"] += f"\n{key}:\n{str(arg)}\n"

    return message


def ask_stream(
    user_message: str,
    *unnamed_other_args,
    system: Optional[str] = "You are a helpful assistant.",
    model: Optional[Model] = None,
    interval_ms: float = 50,
    force_llm_args: Optional[dict] = {},
    **named_other_args,
):
    """
    Yields text chunks from the LLM as they stream in, grouped by time window.

    Tokens are accumulated for up to `interval_ms` milliseconds, then yielded
    together as a single str chunk.  On end-of-stream, any remaining tokens are
    flushed immediately without waiting for the next window.

    Parameters
    ----------
    user_message : str
        The question or prompt to send to the model.
    interval_ms : float
        Maximum time (in milliseconds) to accumulate tokens before yielding.
        Default: 50 ms.  Set to 0 to yield every token individually.
    model : Model, optional
        Override the default model.  Must support ModelCapabilities.STREAMING.
    force_llm_args : dict, optional
        Extra arguments forwarded to the LLM API.
    """
    import time as _time
    from ..core.base_model import ModelCapabilities

    if model is None:
        from ..core.inspection import Inspection
        from ..core.analizer import AnalyzedFunction, AnalyzedArgument
        dummy_analyse = AnalyzedFunction(name="ask", args=[], type=str, doc=user_message)
        for i, arg in enumerate(unnamed_other_args):
            dummy_analyse.args.append(AnalyzedArgument(name=f"arg{i}", value=arg, type=None))
        for key, arg in named_other_args.items():
            dummy_analyse.args.append(AnalyzedArgument(name=key, value=arg, type=None))
        dummy_inspection = Inspection(None, None, dummy_analyse)
        model = config.DefaultPipeline.push_choose_model(dummy_inspection)

    message = _build_ask_message(user_message, unnamed_other_args, named_other_args, system)
    llm_args = dict(force_llm_args)

    interval_s = interval_ms / 1000.0
    buffer = ""
    window_start = _time.monotonic()

    for chunk in model.generate_stream(message, **llm_args):
        if interval_s > 0 and (_time.monotonic() - window_start) >= interval_s:
            if buffer:
                yield buffer
                buffer = ""
                window_start = _time.monotonic()
        buffer += chunk
        if interval_s <= 0:
            yield buffer
            buffer = ""
            window_start = _time.monotonic()

    # Flush any remaining tokens immediately on end-of-stream
    if buffer:
        yield buffer


async def ask_stream_async(
    user_message: str,
    *unnamed_other_args,
    system: Optional[str] = "You are a helpful assistant.",
    model: Optional[Model] = None,
    interval_ms: float = 50,
    force_llm_args: Optional[dict] = {},
    **named_other_args,
):
    """
    Async version of ask_stream.  Use with ``async for chunk in ask_stream_async(...)``.

    Tokens are accumulated for up to `interval_ms` ms, then yielded as a single chunk.
    The last chunk is always flushed immediately on end-of-stream.
    """
    import asyncio as _asyncio
    import time as _time
    from ..core.base_model import ModelCapabilities

    if model is None:
        from ..core.inspection import Inspection
        from ..core.analizer import AnalyzedFunction, AnalyzedArgument
        dummy_analyse = AnalyzedFunction(name="ask", args=[], type=str, doc=user_message)
        for i, arg in enumerate(unnamed_other_args):
            dummy_analyse.args.append(AnalyzedArgument(name=f"arg{i}", value=arg, type=None))
        for key, arg in named_other_args.items():
            dummy_analyse.args.append(AnalyzedArgument(name=key, value=arg, type=None))
        dummy_inspection = Inspection(None, None, dummy_analyse)
        model = config.DefaultPipeline.push_choose_model(dummy_inspection)

    message = _build_ask_message(user_message, unnamed_other_args, named_other_args, system)
    llm_args = dict(force_llm_args)

    interval_s = interval_ms / 1000.0
    buffer = ""
    window_start = _time.monotonic()

    async for chunk in model.generate_stream_async(message, **llm_args):
        if interval_s > 0 and (_time.monotonic() - window_start) >= interval_s:
            if buffer:
                yield buffer
                buffer = ""
                window_start = _time.monotonic()
        buffer += chunk
        if interval_s <= 0:
            yield buffer
            buffer = ""
            window_start = _time.monotonic()

    if buffer:
        yield buffer