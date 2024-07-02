from flask import Flask
from llm import emulator
import random
import string

app = Flask(__name__)
llm = emulator()


@llm.emulate
def say_hello(first_letter: str) -> str:
    """
    This function returns a greeting message.
    And the first word of the message must start with the first letter.
    """
    pass


@app.route('/')
def hello_world():
    return say_hello(random.choice(string.ascii_uppercase))


@app.route('/tic-tac-toe', methods=['POST'])
def tic_tac_toe():



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
