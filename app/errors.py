from app import app


@app.errorhandler(400)
def incorrect_properties(error):
    """ Return a 400 error. """
    return {'error': 'The client provided incorrect input.'}, 400


@app.errorhandler(401)
def auth_error(error):
    """ Return a 401 error. """
    return {'error': 'Authentication error.'}, 401


@app.errorhandler(403)
def operation_error(error):
    """ Return a 403 error. """
    return {'error': 'The operation cannot be performed by the client'}, 403


@app.errorhandler(404)
def not_found(error):
    """ Return a 404 error. """
    return {'error': 'Not found'}, 404


@app.errorhandler(405)
def not_allowed(error):
    """ Return a 405 error. """
    return {'error': 'HTTP Method Not allowed'}, 405
