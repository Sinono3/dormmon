from flask import jsonify, request


JSON_MIME = "application/json"


def wants_json_response() -> bool:
    """
    Return True when the caller explicitly prefers a JSON response.
    Defaults to HTML when the Accept header does not mention JSON.
    """
    accept = request.headers.get("Accept", "")
    return JSON_MIME in accept.lower()


def json_response(payload: dict, status: int = 200):
    """Return a JSON response with the provided payload and status code."""
    return jsonify(payload), status


def json_error(message: str, status: int = 400, **extra):
    """Return a JSON error response with a consistent structure."""
    payload = {"error": message}
    if extra:
        payload.update(extra)
    return jsonify(payload), status

