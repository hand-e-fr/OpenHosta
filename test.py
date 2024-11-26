import PIL.Image
from OpenHosta import emulate, Model
import PIL

mymodel = Model(
    model="",
    base_url="https://api.openai.com/v1/images/generations",
    api_key=""
)

def generate_image(query:str)->PIL.Image:
    """
    This function generate an image in the PIL format with the query in parameter.
    """
    return emulate()

print(generate_image("A cat"))