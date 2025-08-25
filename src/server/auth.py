from flask import request, jsonify

API_SECRET = "supersecretkey"

def require_api_key(view_function):
    def decorated_function(*args, **kwargs):
        key = request.headers.get("x-api-key")
        if key and key == API_SECRET:
            return view_function(*args, **kwargs)
        else:
            return jsonify({"error": "Unauthorized"}), 401
    decorated_function.__name__ = view_function.__name__
    return decorated_function