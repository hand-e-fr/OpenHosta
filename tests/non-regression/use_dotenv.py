## Test if .env is properly used

from OpenHosta import ask, closure

print(ask("What is your name?"))

from OpenHosta import DefaultModel
DefaultModel.api_parameters |= {  "options": { "think": False } }
describe = closure("Describe this content based on Charles S. Peirce's semiotic triad (Representamen, Object, Interpretant)")
print(describe("Paris Hilton went to paris to sleep. Where did she sleep?"))
print(describe("Quel est le prix du pain?"))

from OpenHosta import reload_dotenv
reload_dotenv()

import os
os.getenv("OPENHOSTA_DEFAULT_MODEL_SEED", None)

print(describe("Quel est le prix du pain?"))

describe.hosta_inspection["model"].base_url
describe.hosta_inspection["model"].model_name
describe.hosta_inspection["model"].api_parameters |= {"options": {"Thinking": False, "think": False}, "Thinking": False, "think": False}

from OpenHosta import print_last_prompt, print_last_decoding
print_last_prompt(describe)
# print_last_decoding(describe)

from OpenHosta.core.meta_prompt import EMULATE_META_PROMPT

describe.hosta_inspection['pipeline'].emulate_meta_prompt = EMULATE_META_PROMPT.copy()
describe.hosta_inspection['pipeline'].emulate_meta_prompt.source += "\nDo not think. replace your thinking by <think></think> tags."