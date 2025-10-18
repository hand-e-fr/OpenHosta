from OpenHosta.core.logger import print_last_prompt
import pytest

from OpenHosta import emulate

class TestMultiModal:
       
    def test_ImageInPrompt(self):
        from PIL.Image import Image, open
        from io import BytesIO
        import requests
        
        def WhatCompanyLogo(logo:Image) -> str:
            """
            Identify the company name given the logo in parameter
            """
            return emulate()
        
        # Load from URL
        url = "https://www.hand-e.fr/hand_e_logo.jpeg"
        img = open(BytesIO(requests.get(url).content))
        response = WhatCompanyLogo(img)
        assert "and" in response, "We should have recognized hand-e logo"
