from flask import jsonify, session
from functools import wraps

def login_not_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("logged_in"):
            return jsonify({"error": "You are already logged in"}), 400  # Changed from 401 to 400
        return f(*args, **kwargs)
    return decorated_function

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            return jsonify({"error": "You are not logged in"}), 401
        return f(*args, **kwargs)
    return decorated_function