from math import sqrt
from random import randint
from .solver.sudoku_solver import Board


def parse_payload(data: str) -> Board:
    """ Helper function to parse incoming payload. """
    size = int(sqrt(len(data)))
    box_size = int(sqrt(size))
    dimensions = (1, size + 1)
    board = []
    row = []
    for i, item in enumerate(data):
        row.append(int(item))
        if (i + 1) % size == 0:
            board.append(row)
            row = []
    return Board(board, size, box_size, dimensions)


def generate_sudoku(size: int) -> tuple[str, int]:
    """ Function to generate size*size square Sudoku puzzle. """
    box_size = int(sqrt(size))
    dimensions = (1, size + 1)
    solvable = False
    iterations = 0
    while not solvable:
        iterations += 1

        board = [[0 for _ in range(0, 9)] for _ in range(0, 9)]
        temp_board = Board(board, size, box_size, dimensions)
        temp_board.generate()

        for i, row in enumerate(temp_board.board):
            for j, number in enumerate(row):
                choice = randint(0, 1)
                if choice:
                    temp_board.board[i][j] = 0

        number_of_clues = len([x for x in row if x != 0 for row in temp_board.board])
        if number_of_clues < 17 or number_of_clues > 30:
            continue
        challenge = ''
        for row in temp_board.board:
            for number in row:
                challenge += (str(number))
        return challenge, iterations
