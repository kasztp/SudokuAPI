from math import sqrt
from flask import abort, render_template, request
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
    if not sqrt(len(data["payload"])).is_integer():
        response = {
            "original": data["payload"],
            "solvable": False,
            "reason": "Invalid input length or non square board size."
        }
    else:
        challenge = parse_payload(data)
        solvable = challenge.check_solvable()
        if solvable:
            response = {
                "original": data["payload"],
                "solvable": solvable,
                "reason": "Looks good."
            }
        else:
            response = {
                "original": data["payload"],
                "solvable": solvable,
                "reason": "Invalid clues."
            }
    return response


@app.route('/v1/generate', methods=["GET"])
def generate():
    pass
    # TODO To be implemented
