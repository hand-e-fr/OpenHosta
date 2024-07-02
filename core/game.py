from OpenHosta import emulator

llm = emulator()

class Game_tic_tac_toe:
    def __init__(self):
        pass

    @llm.emulate
    def find_next_move(self, intput):
        '''This function will return the next move for the game
        and return the same type of output as the input but with the next move.
        you will find if you need to add an X or an 0 in the next move based on how many of them are in the input
        if you have more X than 0 you will add an 0 else you will add an X
        '''
    @llm.emulate
    def check_winner(self, input) -> int:
        '''This function will check if there is a winner in the game
        and return 1 if y win, 2 if you win and 0 if there is no winner
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