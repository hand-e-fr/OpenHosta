from core.OpenHosta import emulator

llm = emulator()


class Game_tic_tac_toe:
    def __init__(self):
        pass

    @llm.emulate
    def find_next_move(self, intput):
        '''
        You play the game of tic tac toe with the computer.
        This function will return the next move for the game
        and return the same type of output as the input but with the next move.
        You are the 'O' player
        You have to WIN the game try to find the next move to win the game. or block the computer to win the game.
        '''

    @llm.emulate
    def check_winner(self, input) -> int:
        '''
        You play the game of tic tac toe with the computer.
        Tell if there is a winner in the game.
        If there is a winner return the winner number (1 or 2) else return 0
        if the game is a draw return 3
        if its player 'O' return 1
        if its player 'X' return 2
        '''

    @llm.emulate
    def create_a_board(self, intput):
        '''
        This function will create a board for the game.
        You will be able to only create a board with 3x3 dimensions
        and you need to return the board as bach like this example in base of the given intput:
        "X | 0 | X
         ---------
         0 |   | 0
         ---------
         0 | X | X"
        BEWARE: of the spaces between the characters
        '''

    @llm.emulate
    def parse_move_player(self, input, position):
        '''
        This function take in parameter an input and a positon,
        the position is the position where the player want to play
        so your goal is to return the input with the new move.
        As like you need to add an extra X at the postion given in parameter if it's possible or not.
        Like the problem can.
        The moves are beetween 1 and 9 as the 1 correspond to the top left corner and 9 to the bottom right corner.
        Return the input with the new move.
        '''


game = Game_tic_tac_toe()


def play_the_game():
    pass
