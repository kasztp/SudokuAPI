""" Routes for the Sudoku Solver API. """
from math import sqrt
from random import randint
from flask import abort, escape, render_template, request
from app import app
from .solver.sudoku_solver import Board


def parse_payload(data):
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


def generate_sudoku(size):
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


@app.errorhandler(404)
def not_found(error):
    return {'error': 'Not found'}, 404


@app.errorhandler(405)
def not_found(error):
    return {'error': 'HTTP Method Not allowed'}, 405


@app.route('/')
def root():
    return render_template('index.html', title='SudokuAPI Documentation')


@app.route('/v1/solve', methods=["POST"])
def solve():
    """ Route to return solved Sudoku puzzle. """
    data = request.get_json(silent=True)
    if not request.json or 'payload' not in request.json:
        abort(400)

    submitted = escape(data["payload"])
    if not sqrt(len(submitted)).is_integer():
        response = {
            "error": "Invalid input length or non square board size.",
            "original": submitted,
            "solvable": False
        }
        return response, 400

    challenge = parse_payload(submitted)
    solvable = challenge.check_solvable()
    if not solvable:
        response = {
            "error": "Invalid clues.",
            "original": submitted,
            "solvable": solvable
        }
        return response, 400

    passes = challenge.preprocess_board()
    challenge.solve()
    solution = ''
    for row in challenge.board:
        for number in row:
            solution += str(number)
    response = {
        "original": submitted,
        "solved": solution,
        "iterations": challenge.iterations,
        "passes": passes
    }
    return response


@app.route('/v1/check', methods=["POST"])
def check():
    """ Route to check if a board seems to be solvable or not. - To be improved! """
    data = request.get_json(silent=True)
    if not request.json or 'payload' not in request.json:
        abort(400)

    submitted = escape(data['payload'])
    if not sqrt(len(submitted)).is_integer():
        response = {
            "original": submitted,
            "solvable": False,
            "reason": "Invalid input length or non square board size."
        }
        return response

    challenge = parse_payload(submitted)
    solvable = challenge.check_solvable()
    if solvable:
        response = {
            "original": submitted,
            "solvable": solvable,
            "reason": "Looks good."
        }
    else:
        response = {
            "original": submitted,
            "solvable": solvable,
            "reason": "Invalid clues."
        }
    return response


@app.route('/v1/generate', methods=["GET"])
def generate():
    """ Route to return a random Sudoku puzzle. """
    size = 9
    challenge, iterations = generate_sudoku(size)
    response = {
        "sudoku": challenge,
        "iterations": iterations,
    }
    return response
