from functools import wraps
from flask import jsonify
from app import app

def handle_errors(f):
    """Decorator to handle exceptions in routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            app.logger.error(f'Error occurred: {e}')  # Log the error for debugging
            if hasattr(e, 'code'):
                return jsonify({'error': str(e), 'message': e.description}), e.code
            return jsonify({'error': str(e), 'message': 'An unexpected error occurred.'}), 500  # Internal Server Error
    return decorated_function

