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
            
        dummy_inspection = Inspection(None, dummy_analyse)
        model = config.DefaultPipeline.push_choose_model(dummy_inspection)

    message = []
    if system is not None:
        message.append({"role": "system", "content": [{"type": "text", "text": system}]})
        
    message.append(
        {"role": "user", "content": [
            { "type": "text", "text": user_message }
        ]})

    for arg in unnamed_other_args:
        named_other_args["arg"+str(unnamed_other_args.index(arg))] = arg

    for key, arg in named_other_args.items():
        try:
            import PIL.Image
            import base64      
            import io      
            pil_image_supported = True
        except ImportError:
            pil_image_supported = False
            
        if pil_image_supported and isinstance(arg, PIL.Image.Image):
            buffered= io.BytesIO()
            arg.save(buffered, format="PNG")
            img_string = base64.b64encode(buffered.getvalue()).decode("utf-8")
            message[-1]["content"].append(
                {"type": "image_url", "image_url": {
                    "url": "data:image/png;base64," + img_string
                } 
                 })
        else:
            
            # Add a system message if missing
            if len(message) == 1:
                system_message = {"role": "system", "content": [{"type": "text", "text": ""}]}
                message = [system_message] + message
                
            message[0]["content"][0]["text"] += f"\n{key}:\n{str(arg)}\n"

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
            
        dummy_inspection = Inspection(None, dummy_analyse)
        model = config.DefaultPipeline.push_choose_model(dummy_inspection)

    message = []
    if system is not None:
        message.append({"role": "system", "content": [{"type": "text", "text": system}]})
        
    message.append(
        {"role": "user", "content": [
            { "type": "text", "text": user_message }
        ]})

    for arg in unnamed_other_args:
        named_other_args["arg"+str(unnamed_other_args.index(arg))] = arg

    for key, arg in named_other_args.items():
        try:
            import PIL.Image
            import base64      
            import io      
            pil_image_supported = True
        except ImportError:
            pil_image_supported = False
            
        if pil_image_supported and isinstance(arg, PIL.Image.Image):
            buffered= io.BytesIO()
            arg.save(buffered, format="PNG")
            img_string = base64.b64encode(buffered.getvalue()).decode("utf-8")
            message[-1]["content"].append(
                {"type": "image_url", "image_url": {
                    "url": "data:image/png;base64," + img_string
                } 
                 })
        else:
            
            # Add a system message if missing
            if len(message) == 1:
                system_message = {"role": "system", "content": [{"type": "text", "text": ""}]}
                message = [system_message] + message
                
            message[0]["content"][0]["text"] += f"\n{key}:\n{str(arg)}\n"

    force_llm_args["force_json_output"] = force_json_output

    response_dict = await model.api_call_async(
        messages=message,
        llm_args=force_llm_args
    )

    response = model.get_response_content(response_dict)
    
    # No type detection
    answer = response

    return answer
    