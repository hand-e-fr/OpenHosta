import asyncio
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
    
from OpenHosta import emulate, emulate_async
from OpenHosta import ask, ask_async

from OpenHosta import test as oh_test
from OpenHosta import test_async as oh_test_async


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



    def test_ImageInPromptAsync(self):
        
        async def WhatCompanyLogo(logo:Image) -> str:
            """
            Identify the company name given the logo in parameter
            """
            return await emulate_async()
        
        img = open(assets_dir / "hand_e_logo.jpeg")
        response = asyncio.run(WhatCompanyLogo(img))
        
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
        
        MAX_MISMATCHES = 1
        
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

        count_ok_lines = 0
        missmatch_info = ""
        for i, expected_line in enumerate(expected_lines):
            if expected_line == lines[i]:
                count_ok_lines += 1
            else:
                missmatch_info = f" (expected: '{expected_line}' got: '{lines[i]}')\n"

        assert count_ok_lines >= len(expected_lines) - MAX_MISMATCHES , f"Too many mismatches in extracted lines{missmatch_info}"

    def test_AskWithImageAndText(self):
                
        img = open(assets_dir / "hand_e_logo.jpeg")
        text = "This is the logo of which company?"
        
        response = ask(text, img)
        
        assert "hand" in response.lower(), "We should have recognized hand-e logo in the description"


    def test_AskWithImageAndTextAsync(self):

        img = open(assets_dir / "hand_e_logo.jpeg")
        text = "This is the logo of which company?"
        
        response = asyncio.run(ask_async(text, img))
        
        assert "hand" in response.lower(), "We should have recognized hand-e logo in the description"        
        
        
    def test_TestWithImageAndText(self):
                
        img = open(assets_dir / "hand_e_logo.jpeg")
        
        if oh_test("This is the Nike logo", img):
            result = True
        else:
            result = False
        
        assert result is False, "The test should have failed recognizing Nike logo in the description"

        if oh_test("This is the hand-e logo", img):
            result = True
        else:
            result = False

        assert result is True, "The test should have passed recognizing hand-e logo in the description"
        
        

    def test_TestWithImageAndTextAsync(self):
    
        img = open(assets_dir / "hand_e_logo.jpeg")
        
        async def run_test1():               
            if await oh_test_async("This is the Nike logo", img):
                result = True
            else:
                result = False
            
            return result
        
        result = asyncio.run(run_test1())
        assert result is False, "The test should have failed recognizing Nike logo in the description"

        async def run_test2():
            if oh_test("This is the hand-e logo", img):
                result = True
            else:
                result = False
            return result
        
        result = asyncio.run(run_test2())
        assert result is True, "The test should have passed recognizing hand-e logo in the description"