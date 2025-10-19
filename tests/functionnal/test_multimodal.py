import pytest


from PIL.Image import Image, open
from pathlib import Path

from typing import List

try:
    test_dir = Path(__file__).parent.parent
except NameError:
    print("In interactive mode, setting test_dir to current working directory. It shall be the tests folder.")
    test_dir = Path.cwd()
    
if (test_dir / "assets").exists():
    assets_dir = test_dir / "assets"
else:
    raise FileNotFoundError(f"Assets directory not found in {test_dir}. Cannot continue.")
    
from OpenHosta import emulate

class TestMultiModal:
       
    def test_ImageInPrompt(self):
        
        def WhatCompanyLogo(logo:Image) -> str:
            """
            Identify the company name given the logo in parameter
            """
            return emulate()
        
        img = open(assets_dir / "hand_e_logo.jpeg")
        response = WhatCompanyLogo(img)
        assert "hand" in response.lower(), "We should have recognized hand-e logo"

    def test_ReadTableInImage(self):

        expected_lines = [
             'GUNOOLIONCSEHP',
             'AHWZMEREFAEVOS',
             'SOUSLMARINAPPI',
             'VYYCAMIONEAGGH',
             'RENARDAMIBILAU',
             'YEGICHÂTEAUBAD',
             'VOITUREIXRHYNV',
             'THLEYLDROBOTGV',
             'QAADSLIVREDPBK',
             'UTLTGRPDIFUSÉE',
             'ILUCHIENBLOUPE',
             'POULESOURSONTL',
             'PIRATECMUILOLM', 
             'CULBUTOIOPOINTS'
            ]
        
        def image_of_char_grid_to_list_of_string(image: Image) -> List[str]:
            """
            Convert an image of a character grid into a list of strings.
            Each string represents a row of characters.
            Rows does not have meaning. Just extract the characters as they are in the image.
            
            Arguments:
                image (PIL.Image.Image): The input image containing the character grid.
                
            Returns:
                List[str]: A list of strings. each string is a line of the grid. no space in between.
            """
            return emulate()

        img = open(assets_dir / "letter_grid.png")

        lines = image_of_char_grid_to_list_of_string(img)

        assert type(lines) == list, "The output should be a list of strings"
        assert len(lines) > 0, "We should have extracted some lines from the image"
        assert len(lines) == len(expected_lines), f"We should have extracted {len(expected_lines)} lines"
        
        for line in lines:
            assert type(line) == str, "Each line should be a string"

        for i, expected_line in enumerate(expected_lines):
            assert expected_line == lines[i], f"The line {i} should be '{expected_line}' but got '{lines[i]}'"