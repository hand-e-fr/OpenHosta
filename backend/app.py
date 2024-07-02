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


@llm.emulate
def emulate_tic_tac_toe(board: str) -> str:
    """
    This function emulates a tic-tac-toe game.
    You must provide the current state of the board as a list of lists.
    Each list represents a row of the board.
    Each element of the list represents a cell of the board.
    The value of each cell can be "-", "X" or "O".
    The function returns the next state of the board and the status of the game.
    The status can be "draw" or "win".
    example of received board:
    ```json
    {
        "board": [
            ["-", "-", "-"],
            ["-", "X", "-"],
            ["-", "-", "-"]
        ]
    }
    ```
    example of returned board:
    draw:
    ```json
    {
        "board": [
            ["-", "O", "-"],
            ["-", "X", "-"],
            ["-", "-", "-"]
        ],
        "status": "draw"
    }
    ```
    """
    pass


@app.route('/tic-tac-toe', methods=['POST'])
def tic_tac_toe():
    return emulate_tic_tac_toe()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
