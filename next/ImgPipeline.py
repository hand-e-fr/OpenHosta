from PIL.Image import Image as PILImageType
from enum import Enum
from OpenHosta import emulate, reload_dotenv
reload_dotenv()


class DocumentTypes(Enum):
    COMPTA="compta"
    TRAINING="training"
    INVOICE="invoice"
    PHOTO="photo"
    USER_MANUAL="user_manual"
    OTHER="other"

#TODO: do not forget to rotate the image if needed
from OpenHosta import closure
closure("how many degrees should I rotate the image to have the text upright")(Image.open('IMG_6506.jpg'))
closure("what type of document is it")(Image.open('IMG_6506.jpg').rotate(-90, expand=True))
closure("what is the title of the document on this photo")(Image.open('IMG_6506.jpg').rotate(-90, expand=True))

def FindDocumentType(img:PILImageType) -> DocumentTypes:
    """
    Detect the type of document in the image.
    """
    return emulate()

FindDocumentType(Image.open('IMG_6506.jpg').rotate(-90, expand=True))

from PIL import Image
img0=Image.open('IMG_6506.jpg')
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
