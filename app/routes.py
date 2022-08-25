""" Routes for the Sudoku Solver API. """
from math import sqrt
from flask import abort, escape, render_template, request
from app import app, errors
from app.utils import parse_payload, generate_sudoku


@app.route('/')
def root():
    """ Root URL. """
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
