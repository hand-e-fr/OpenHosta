from OpenHosta import emulator

llm = emulator()

class Game_tic_tac_toe:
    def __init__(self):
        pass

    @llm.emulate
    def find_next_move(self, intput):
        '''Beforehand here's the rules of the tic-tac-toe games:
        Basic Rules:

    Players: The game is played by two players. One player uses 'X' and the other uses '0'.
    Game Board: The game is played on a 3x3 grid.
    Objective: The goal is to be the first player to get three of their marks in a row, either horizontally, vertically, or diagonally.

How to Play:

    Starting the Game: Players decide who will go first. This can be done by a coin toss or any other method of choice.
    Turns: Players take turns placing their mark (either 'X' or '0') in an empty cell on the grid.
    Winning the Game: A player wins by placing three of their marks in a row, column, or diagonal.
    Draw: If all nine cells are filled and neither player has three in a row, the game is a draw.

Strategic Considerations:

    First Move Advantage: The player who goes first (usually 'X') has a slight advantage. Optimal play can mitigate this.
    Center Control: The center cell is the most strategic position as it is part of four potential winning lines (two diagonals, one row, and one column).
    Forks: Creating a situation where you have two ways to win on your next turn is called a fork. This forces the opponent to block one line, allowing you to win with the other.

Advanced Strategies:

    Blocking: Always block your opponent’s potential winning move if they have two in a row.
    Creating Opportunities: Aim to create multiple opportunities to win simultaneously.
    Anticipation: Try to anticipate your opponent’s moves and plan your strategy accordingly.

Variations:

    Board Size: While the standard board is 3x3, variations can include larger grids like 4x4 or 5x5, which can change the complexity and strategies of the game.
    Marks: Some variations use different marks or even numbers.
    Multiple Rounds: Some play multiple rounds and keep score over several games.

Common Terms:

    Row: A horizontal line of three cells.
    Column: A vertical line of three cells.
    Diagonal: A line of three cells that runs from one corner to the opposite corner.
    Fork: A strategy where a player creates two potential winning moves simultaneously.
    Block: Placing a mark to prevent the opponent from winning.

Winning and Draw Conditions:

    Three in a Row: The primary winning condition is getting three of your marks in a row.
    Draw: If all cells are filled and no player has three in a row, the game ends in a draw.

Etiquette and Fair Play:

    Respect Turns: Ensure each player takes their turn in the correct order.
    No Cheating: Do not change or move marks once placed.
    Sportsmanship: Congratulate your opponent regardless of the outcome.

Mathematical Perspective:

    Combinatorial Analysis: There are 255,168 possible games of tic-tac-toe if you consider all possible moves and outcomes.
    Symmetry: Many of these games are symmetrical, meaning they can be rotated or flipped and still be considered the same game.

You will act as an expert game developer to help me create a function that determines the next move in a tic-tac-toe game with the purpose of winning the game. The function will return the next move and output the same type of input but with the next move added. The function will check the current counts of 'X' and '0' in the input:

    If there are more 'X's than '0's, the function will add an '0'.
    Otherwise, the function will add an 'X'.

The input will be a character array containing the characters 'X', '0', and ' '. The output must be of the same type as the input. The function must handle error cases by ignoring and adapting to the errors, such as when the input type is different, or if the number of 'X' or '0' is inconsistent with the rules of the tic-tac-toe game. The primary purpose of the function is to make moves that will lead to winning the game.

The function should prioritize blocking the opponent's winning moves and creating opportunities for a win. Specifically:

    If the opponent has two filled squares forming a line, the function must block it.
    Otherwise, the function must try to form a filled line to win.
    It can't fill an alredy filled square, an empty square is represented by ' '.

Here are examples of valid and invalid inputs:
Valid input: [['X', '0', ' '], ['X', '0', ' '], [' ', ' ', '0']]
Valid output: [['X', '0', ' '], ['X', '0', ' '], ['X', ' ', '0']]

Invalid input: [['X', 'X', ' '], ['X', 'X', ' '], [' ', ' ', '0']]
        '''
    @llm.emulate
    def check_winner(self, input) -> int:
        ''' Beforehand here's the rules of the tic-tac-toe games:
        Basic Rules:

    Players: The game is played by two players. One player uses 'X' and the other uses '0'.
    Game Board: The game is played on a 3x3 grid.
    Objective: The goal is to be the first player to get three of their marks in a row, either horizontally, vertically, or diagonally.

How to Play:

    Starting the Game: Players decide who will go first. This can be done by a coin toss or any other method of choice.
    Turns: Players take turns placing their mark (either 'X' or '0') in an empty cell on the grid.
    Winning the Game: A player wins by placing three of their marks in a row, column, or diagonal.
    Draw: If all nine cells are filled and neither player has three in a row, the game is a draw.

Strategic Considerations:

    First Move Advantage: The player who goes first (usually 'X') has a slight advantage. Optimal play can mitigate this.
    Center Control: The center cell is the most strategic position as it is part of four potential winning lines (two diagonals, one row, and one column).
    Forks: Creating a situation where you have two ways to win on your next turn is called a fork. This forces the opponent to block one line, allowing you to win with the other.

Advanced Strategies:

    Blocking: Always block your opponent’s potential winning move if they have two in a row.
    Creating Opportunities: Aim to create multiple opportunities to win simultaneously.
    Anticipation: Try to anticipate your opponent’s moves and plan your strategy accordingly.

Variations:

    Board Size: While the standard board is 3x3, variations can include larger grids like 4x4 or 5x5, which can change the complexity and strategies of the game.
    Marks: Some variations use different marks or even numbers.
    Multiple Rounds: Some play multiple rounds and keep score over several games.

Common Terms:

    Row: A horizontal line of three cells.
    Column: A vertical line of three cells.
    Diagonal: A line of three cells that runs from one corner to the opposite corner.
    Fork: A strategy where a player creates two potential winning moves simultaneously.
    Block: Placing a mark to prevent the opponent from winning.

Winning and Draw Conditions:

    Three in a Row: The primary winning condition is getting three of your marks in a row.
    Draw: If all cells are filled and no player has three in a row, the game ends in a draw.

Etiquette and Fair Play:

    Respect Turns: Ensure each player takes their turn in the correct order.
    No Cheating: Do not change or move marks once placed.
    Sportsmanship: Congratulate your opponent regardless of the outcome.

Mathematical Perspective:

    Combinatorial Analysis: There are 255,168 possible games of tic-tac-toe if you consider all possible moves and outcomes.
    Symmetry: Many of these games are symmetrical, meaning they can be rotated or flipped and still be considered the same game.

You will act as an expert game developer to help me create a function that checks if there is a winner in a tic-tac-toe game. The function will return:

    1 if '0' wins (i.e., a player has succeeded in forming a vertical, horizontal, or diagonal line in the array with the '0' character),
    2 if 'X' wins (i.e., a player has succeeded in forming a vertical, horizontal, or diagonal line in the array with the 'X' character),
    0 if there is no winner or if it's a tie (i.e., no one has succeeded in forming a vertical, horizontal, or diagonal line in the array with a single character; spaces are not considered characters, they are empty squares),
    -1 if the game isn't ended yet (i.e., none of the winning or tie conditions are met).

The input will be a character array containing the characters 'X', '0', and ' '. The function must handle error cases by skipping invalid entries and adapting to the errors, such as when the input type is different or if the number of 'X' or '0' is inconsistent with the rules of the tic-tac-toe game.

Here are examples of valid and invalid inputs:
Valid input (tie game): [['0', '0', 'X'], ['X', 'X', '0'], ['0', 'X', 'X']]
Valid output: 0

Valid input (game won by '0'): [['0', 'X', 'X'], [' ', '0', 'X'], [' ', ' ', '0']]
Valid output: 1

Valid input (game won by 'X'): [['0', 'X', '0'], ['X', 'X', '0'], ['0', 'X', 'X']]
Valid output: 2

Valid input (game not ended yet): [['0', 'X', ' '], [' ', '0', 'X'], [' ', ' ', ' ']]
Valid output: -1

Invalid input: [['X', 'X', ' '], ['X', 'X', ' '], [' ', ' ', '0']]
        '''

    @llm.emulate
    def create_a_board(self, intput):
        '''
        You will act as an expert game developer to help me create a function that generates a tic-tac-toe board. The function will create a board with 3x3 dimensions and return it as a formatted string based on the given input. The input will be a character array containing the characters 'X', '0', and ' '. The output must adhere to the following format, ensuring correct spacing between characters:

Example input:

[['X', '0', 'X'],
['0', ' ', '0'],
['0', 'X', 'X']]

Example output:
```
"X | 0 | X
----------
0 |   | 0
----------
0 | X | X"
        '''

    @llm.emulate
    def parse_move_player(self, input, position):
        '''
        This function take in parameter an input and a positon,
        the position is the position where the player want to play
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