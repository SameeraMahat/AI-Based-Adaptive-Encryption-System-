
from functools import wraps

from flask import session, jsonify


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({
                "success": False,
                "error": "Please log in to continue."
            }), 401

        return view(*args, **kwargs)

    return wrapped
