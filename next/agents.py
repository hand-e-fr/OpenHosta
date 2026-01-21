
### This is a sample agent for a smart home system.
### 
### It show how we plan to support tools in the next version of OpenHosta.
### In version 3.0 it is already possible to write agents but without tools.
### This means that we have to build a function that return the arguments of the tool to be called
###
### Example in v3.0:
### from enum import Enum
###
### class Tools(Enum):
###     StartTheLights = "startTheLights"
###     GetTemperature = "getTemperature"
###
### class MyAgent:
###     def processInput(self, query):
###         tool_to_use = self.decideTool(query)
###         if tool_to_use == Tools.StartTheLights:
###             return self.startTheLights()
###         elif tool_to_use == Tools.GetTemperature:
###             return self.getTemperature()
###         else:
###             return "I don't know how to help with that."
###
###     def decideTool(self, query:str) -> Tools:
###         """ This function decides which tool to use based on the query. ""
###         return emulate()



##### TODO:
# AgentList object to manage multiple agents
# Agent.clear() to clear memory
# Agent.save() to save memory to disk
# Agent.load() to load memory from disk
# Agent.internal_thinking_logs = [...] to store internal thoughts
# Agent.working_documents = [...] to store working documents
# Agent.chat_history = [...] to store chat history with other agents or users

# For agents we need local scope to be passed to the LLM
ret_dict = {
    "local_1": 42,
    "local_2": "Hello World!",
    "local_3": [1, 2, 3, 4, 5]
}
def showLocals()->dict:
    """
    This function return in a dict all his locals variable and arguments.
    """
    local_1 = ret_dict["local_1"]
    local_2 = ret_dict["local_2"]
    local_3 = ret_dict["local_3"]
    return emulate()

ret = showLocals()
assert ret["local_1"] == ret_dict["local_1"]
assert ret["local_2"] == ret_dict["local_2"]
assert ret["local_3"] == ret_dict["local_3"]

from OpenHosta import emulate, ask as load_context
import requests

from OpenHosta import print_last_decoding, print_last_prompt

print_last_prompt(showLocals)

class MyAgent:
    def __init__(self):
        self.object_states = {
            "lights": "off",
            "thermostat": "22C",
            "security system": "armed"
        }

    def ProcessInput(self, query):
        """
        This function processes the input query and determines if it's a question or a command.
        """
        if self.isQuestion(query):
            return self.answerQuestion(query)
        elif self.isCommand(query):
            return self.executeCommand(query)
        else:
            return "I'm sorry, I don't understand the request."
    
    def isQuestion(self, query):
        """
        This function checks if the input query is a question.
        """
        object_states = self.object_states
        return emulate()
    
    def isCommand(self, query):
        """
        This function checks if the input query is a command.
        """
        available_objects = ["lights", "thermostat", "security system"]
        command_keywords = ["run", "execute", "start", "stop", "launch"]
        return emulate()    
    
    def answerQuestion(self, query):
        return emulate()

    def executeCommand(self, keyword):
        """
        This function executes a command based on the keyword.
        """
        
        # This is a tool that the LLM can call
        tool1 = self.startTheLights
        
        # This is a second tool that the LLM can call
        def invert(command:str):
            """
            This function inverts the command from "start" to "stop" and vice versa.
            """
            if command == "start":
                return "stop"
            elif command == "stop":
                return "start"
            else:
                return command
            
        return emulate()

    def startTheLights(self, keyword):
        """
        This function starts the lights in the smart home system.
        """
        response = requests.get("http://my-smart-home-api/start-lights")
        if response.status_code == 200:
            return "Lights started successfully."
        else:
            return "Failed to start the lights."
