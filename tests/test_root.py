from flask import json
from app import app

app.testing = True


def test_root():
    """Test for Root URL"""
    with app.app_context():
        response = app.test_client().post('/')

        assert response.status_code == 405
        assert dict(json.loads(response.get_data(as_text=True))) == {'error': 'HTTP Method Not allowed'}
