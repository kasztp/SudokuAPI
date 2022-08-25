from flask import json
from app import app

app.testing = True

def test_solve_ok():
    """Test for /v1/solve endpoint."""
    with app.app_context():
        test_sudoku = {
            "payload": "900000000060000000027008000000000307890300000301020580000100800080075602010600009"
            }
        expected_response = {
            "iterations": 9399,
            "original": "900000000060000000027008000000000307890300000301020580000100800080075602010600009",
            "passes": 5,
            "solved": "938764125564291738127538964245816397896357241371429586659142873483975612712683459"
            }
        response = app.test_client().post('/v1/solve', json=test_sudoku)

        assert response.status_code == 200
        assert dict(json.loads(response.get_data(as_text=True))) == expected_response


def test_solve_get():
    """Test for /v1/solve endpoint."""
    with app.app_context():
        response = app.test_client().get('/v1/solve')

        assert response.status_code == 405
        assert dict(json.loads(response.get_data(as_text=True))) == {'error': 'HTTP Method Not allowed'}


def test_solve_invalid_payload():
    """Test for /v1/solve endpoint."""
    with app.app_context():
        test_sudoku = {
            "payload": "9000000000600000000270080000000003078903000003010205800001008000800756020009"
            }
        response = app.test_client().post('/v1/solve', json=test_sudoku)

        assert response.status_code == 400
        assert dict(json.loads(response.get_data(as_text=True))) == {
            'error': 'Invalid input length or non square board size.',
            'original': '9000000000600000000270080000000003078903000003010205800001008000800756020009',
            'solvable': False
            }
