

from PIL.Image import Image, open as pil_open
from pathlib import Path

from typing import List, Dict, Tuple

try:
    test_dir = Path(__file__).parent.parent
except NameError:
    print("In interactive mode, setting test_dir to current working directory. It shall be the tests folder.")
    test_dir = Path.cwd()
    
if (test_dir / "assets").exists():
    assets_dir = test_dir / "assets"
else:
    raise FileNotFoundError(f"Assets directory not found in {test_dir}. Cannot continue.")
    
from openhosta import emulate, emulate_async
from openhosta import ask, ask_async

from openhosta import test as oh_test
from openhosta import test_async as oh_test_async

img = pil_open(assets_dir / "test.jpg")


import PIL.Image

#def list_objects(img:PIL.Image) -> Dict[str, Tuple[int, int, int, int]]:
def list_objects(img:PIL.Image) -> Dict[str, Tuple]:
    """
    List visible objects by their names in french

    Arguments:
      img: image

    Return:
       dictionnary with key the object name and Tuple (top,left,height, width)
    """
    return emulate()

ret = list_objects(img)

from openhosta import print_last_prompt
print_last_prompt(list_objects)

#list_objects.hosta_inspection