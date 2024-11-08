from OpenHosta.OpenHosta import thinkof, config
import os

config.set_default_apiKey(os.getenv("OPENAI_KEY"))

x = thinkof("Est un prénom masculin ?")

print(x("Emmanuel"))
print(x("Marc"))
print(x("Julie"))
