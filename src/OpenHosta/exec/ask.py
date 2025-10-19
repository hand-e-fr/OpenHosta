from __future__ import annotations

from typing import Any, Optional

from ..core.config import Model, config

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

    model = config.DefaultModel

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

    response = response_dict["choices"][0]["message"]["content"]

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

    model = config.DefaultModel

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

    response_dict = await model.api_call_async(messages=message,
        llm_args=force_llm_args
    )

    response = response_dict["choices"][0]["message"]["content"]
    
    # No type detection
    answer = response

    return answer
    