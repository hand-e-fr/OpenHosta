---
trigger: always_on
---

I have created a .venv in OpenHosta.git/tests using uv
I then chnaged directory to tests/ and I installed the local clone of OpenHosta using uv pip install -e ..
I write default LLM credentials in tests/.env so that  OpenHosta reads it when I start the python interpreter from tests/ folder

When running a python code you must cd to tests folder and use python from its .venv that was created using uv