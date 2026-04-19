


garden_description= """
## Localisation
Ville: Göteborg, Suède
Orientation: Nord
Climat: Tempéré et océanique 
Sol: Tourbeux, peu de consistence, assez pauvre
Dimensions à déterminer
Humidité du climat, mais la terre retient peu l'eau
 
## Composition
Le jardin est en pente du haut (Nord-Ouest) vers la maison (Sud). 
Il est bordé au nord par des rochers, au nord-ouest par 5 arbres (érables et chênes),
au sud-ouest par une palissade, au sud-est par le jardin du voisin, au sud par la maison. 
Les zones proches de la maison et du jardin du voisin sont donc ombragées une partie de la journée, sauf en plein été quand le soleil est vraiment haut.
 
### Actuelle
deux plants de framboisiers vers les érables
"""

import os
os.environ["GTK_PATH"] = ""


from OpenHosta import emulate, ask
from OpenHosta import print_last_decoding, print_last_prompt

# ask("quel est ton nom de model ? quelle version et quelle data de fin d'entraienement ?")

import PIL
import PIL.Image
import pyautogui
import time

img = pyautogui.screenshot(region=(0,0,1920, 1080))

img.show()

ask("what is the title of the main window", img= img)

def get_bounding_box(element_name:str, img:PIL.Image.Image) -> tuple[int,int,int,int]:
    """
    This function will return the bounding box of the element in the image.
    
    Args:
       element_name (str): The name of the element to find in the image.
       img (PIL.Image.Image): The image to search in.
       
    Returns:
       tuple[int,int,int,int]: The bounding box of the element in the image. (x1, y1, x2, y2)
    """
    return emulate()

def what_is_the_python_module_for(action_description:str) -> str:
    """
    Identify the best python module to achieve the described action.
    
    Return the module name as a string, ready to be used when loading with import
    """
    return emulate()
    

from OpenHosta import config, MetaPrompt
config.DefaultModel.api_parameters["reasoning_effort"] = "low"
config.DefaultModel.api_parameters["max_tokens"] = 1000

config.DefaultPipeline.emulate_meta_prompt = MetaPrompt('''
    The user write its question to you formated as a python function call.
    Format your answer in the requested python type as if you are writing the outut in REPL.

    ```python    
    def {{ function_name }}({{ function_args }}) -> {{ function_return_type_name }}:
        """
        {{ function_doc | indent(4, true) }}
        """

        ...
        ...behavior to be simulated...
        ...

        return ...appropriate return value...
    ```
''')

t0 = time.time()
what_is_the_python_module_for("resize an image")
t1 = time.time()
print(f"Time taken: {t1-t0}")

print_last_prompt(what_is_the_python_module_for)

box = get_bounding_box("left menu (scaleway console)", img)
box = get_bounding_box("botton for validaton", img)


config.DefaultModel.api_parameters["reasoning_effort"] = "low"
config.DefaultModel.api_parameters["reasoning_effort"] = "high"
r=ask("quel est ton nom de model ? quelle version et quelle data de fin d'entraienement ?")

t0 = time.time()
box = get_bounding_box("View code model windows", img.reduce(4))
t1 = time.time()
print(f"Time taken: {t1-t0}")



from OpenHosta.core.inspection import Inspection
insp:Inspection = get_bounding_box.hosta_inspection

insp.model.api_parameters
insp.logs
img.size
win=img.reduce(4).crop(box)
win.show()