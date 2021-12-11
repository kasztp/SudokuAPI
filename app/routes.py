from math import sqrt
from flask import abort, escape, render_template, request
from random import randint
from app import app
from .solver.sudoku_solver import Board


def parse_payload(data):
    size = int(sqrt(len(data["payload"])))
    box_size = int(sqrt(size))
    dimensions = (1, size + 1)
    board = []
    row = []
    for i, item in enumerate(data["payload"]):
        row.append(int(item))
        if (i + 1) % size == 0:
            board.append(row)
            row = []
    return Board(board, size, box_size, dimensions)


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
    data = request.get_json(silent=True)
    if not request.json or 'payload' not in request.json:
        abort(400)
    if not sqrt(len(data["payload"])).is_integer():
        response = {
            "error": "Invalid input length or non square board size.",
            "original": data["payload"],
            "solvable": False
        }
        return response, 400
    challenge = parse_payload(data)
    solvable = challenge.check_solvable()
    if not solvable:
        response = {
            "error": "Invalid clues.",
            "original": data["payload"],
            "solvable": solvable
        }
        return response, 400
    else:
        passes = challenge.preprocess_board()
        challenge.solve()
        solution = ''
        for row in challenge.board:
            for number in row:
                solution += (str(number))
        response = {
            "original": data["payload"],
            "solved": solution,
            "iterations": challenge.iterations,
            "passes": passes
        }
        return response


@app.route('/v1/check', methods=["POST"])
def check():
    data = request.get_json(silent=True)
    if not request.json or 'payload' not in request.json:
        abort(400)
    submitted = escape(data["payload"])
    if not sqrt(len(submitted)).is_integer():
        response = {
            "original": submitted,
            "solvable": False,
            "reason": "Invalid input length or non square board size."
        }
    else:
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
    # Initial version - to be improved & optimized
    size = 9
    box_size = int(sqrt(size))
    dimensions = (1, size + 1)
    board = []
    row = []
    solvable = False
    iterations = 0
    while not solvable:
        iterations += 1
        for i in range(90):
            number = randint(0, 9)
            if number not in row:
                row.append(number)
            else:
                row.append(0)
            if (i + 1) % size == 0:
                board.append(row)
                row = []
        print(board)
        temp_board = Board(board, size, box_size, dimensions)
        print(temp_board)
        if temp_board.check_solvable():
            solvable = True
            challenge = ''
            for row in temp_board.board:
                for number in row:
                    challenge += (str(number))
            response = {
                "sudoku": challenge,
                "iterations": iterations,
            }
            return response
    pass
