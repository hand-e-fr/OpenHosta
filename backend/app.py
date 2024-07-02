import sys
import json

from flask import Flask
from flask import request
from flask_cors import CORS
from game import Game_tic_tac_toe

app = Flask(__name__)
CORS(app)
game = Game_tic_tac_toe()


class GameMove:
    def __init__(self, board, col, player, row):
        self.board = board
        self.col = col
        self.player = player
        self.row = row

    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        return cls(**data)


class GameMoveResponse:
    def __init__(self, board, winner):
        self.board = board
        self.winner = winner

    def to_json(self):
        return json.dumps(self.__dict__)


class MyMove:
    def __init__(self, board, played_case):
        self.board = board
        self.played_case = played_case

    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        return cls(**data)


@app.route('/tic-tac-toe/gpt_play', methods=['POST'])
def tic_tac_toe_gpt():
    move = GameMove.from_json(request.data)
    winner = game.check_winner(move.board)
    if winner != -1:
        return GameMoveResponse(move.board, winner).to_json()
    print(f"[DEBUG] move.board before: {move.board}", file=sys.stderr)
    move.board = game.find_next_move(move.board)
    print(f"[DEBUG] move.board after: {move.board}\n", file=sys.stderr)
    winner = game.check_winner(move.board)
    return GameMoveResponse(move.board, winner).to_json()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
