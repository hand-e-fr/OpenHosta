### This is a file to test images with OpenHosta
### The function is integrated in the main codebase. 
### The main trick is that if default model does not support images, it allucinates a content. We should find a way to throw error
### Asking directly the model does not seem to work as the model does not know when it cannot see images.
### gpt-oss : 50% yes / 50% no
### qwen2.5vl : 100% no
### gemma3:4b : 20% yes / 80% no
### gemma3:1b : 20% yes / 80% no
### ... 
### maybe with logprobes on enums

from PIL.Image import Image as PILImageType
from PIL import Image
from enum import Enum
from OpenHosta import emulate, reload_dotenv
reload_dotenv()

from OpenHosta import print_last_prompt

class DocumentTypes(Enum):
    COMPTA="compta"
    TRAINING="training"
    INVOICE="invoice"
    PHOTO="photo"
    USER_MANUAL="user_manual"
    OTHER="other"

#TODO: do not forget to rotate the image if needed

# Tested with OPENHOSTA_DEFAULT_MODEL_NAME="mistral-small3.2:24b" on ollama 0.11.8-rc0
from OpenHosta import closure
img0= Image.open("/home/ebatt/Images/IMG_6461.jpg")
describe = closure("describe the image")
d = describe(img0)
print(d)
print_last_prompt(describe)
img0 = Image.open("/home/ebatt/Images/IMG_6461.jpg")
type(img0)
isinstance(img0, PILImageType)
print(describe.hosta_inspection["logs"]["llm_api_messages_sent"][1]["content"][0]["text"])
describe.hosta_inspection["logs"]["llm_api_messages_sent"][1]["content"][1]["image_url"].keys()
closure("how many degrees should I rotate the image to have the text upright")(img0)
closure("what type of document is it")(Image.open('IMG_6506.jpg').rotate(-90, expand=True))
closure("what is the title of the document on this photo")(Image.open('IMG_6506.jpg').rotate(-90, expand=True))

def FindDocumentType(img:PILImageType) -> DocumentTypes:
    """
    Detect the type of document in the image.
    """
    return emulate()

t=FindDocumentType(img0)

img2=img0.rotate(-90, expand=True)

# from OpenHosta import DefaultModel
# DefaultModel.model_name="gpt-4.1"

def convertToMarkdown(img:PILImageType) -> str:
    """
    Extract all text from a picture.
    """
    return emulate()

img = img2#.resize((640,480))

convertToMarkdown.hosta_inspection["model"].timeout=180
md=convertToMarkdown(img)
print(md)
from OpenHosta import print_last_prompt, print_last_decoding
print_last_prompt(convertToMarkdown)
print_last_decoding(convertToMarkdown)


from OpenHosta import DefaultModel
DefaultModel.model_name