from flask import render_template, request
from math import sqrt
from app import app
from .solver.sudoku_solver import Board


@app.route('/')
def root():
    return render_template('index.html', title='SudokuAPI Documentation')


@app.route('/v1/solve', methods=["GET", "POST"])
def solve():
    data = request.get_json(silent=True)
    board = []
    row = []
    for i, item in enumerate(data["payload"]):
        row.append(int(item))
        if (i + 1) % 9 == 0:
            board.append(row)
            row = []
    size = int(sqrt(len(data["payload"])))
    box_size = int(sqrt(sqrt(len(data["payload"]))))
    dimensions = (1, 10)
    challenge = Board(board, size, box_size, dimensions)
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


@app.route('/v1/check', methods=["GET", "POST"])
def check():
    pass
    # TODO To be implemented


@app.route('/v1/generate', methods=["GET", "POST"])
def generate():
    pass
    # TODO To be implemented
