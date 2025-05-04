# This Flask application is improved by ChatGPT o4-mini-high

# 1 - Externalize Configuration & Use a Production-Ready Server
# • Pull settings (host, port, debug mode) from environment variables
# • Swap out the built-in dev server for something like Gunicorn in production

# 2 - Add Input Validation & Sanitization
# • Guard against empty or malicious input
# • Return a clear error if validation fails

# 3 - Introduce Structured Logging & Error Handling
# • Log every request with status code, path, and user input
# • Return JSON-formatted errors for better client-side handling

import os
import re
import logging
from flask import Flask, request, abort, jsonify

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

def create_app():
    app = Flask(__name__)

    # Load configuration from environment variables
    app.config.update(
        HOST=os.getenv("FLASK_HOST", "0.0.0.0"),
        PORT=int(os.getenv("FLASK_PORT", 5000)),
        DEBUG=os.getenv("FLASK_DEBUG", "false").lower() == "true",
    )

    @app.before_request
    def log_request():
        logging.info(
            "Request: %s %s?%s",
            request.method,
            request.path,
            request.query_string.decode(),
        )

    @app.errorhandler(400)
    @app.errorhandler(404)
    @app.errorhandler(500)
    def handle_error(err):
        response = jsonify({
            "error": err.name,
            "message": err.description if hasattr(err, "description") else str(err),
        })
        response.status_code = err.code if hasattr(err, "code") else 500
        logging.error(
            "Error %s on %s: %s",
            response.status_code,
            request.path,
            response.json,
        )
        return response

    @app.route("/")
    def hello():
        # Input validation and sanitization
        name = request.args.get("name", "").strip()
        if not name:
            abort(400, description="Query parameter 'name' is required and cannot be empty.")
        if not re.fullmatch(r"[A-Za-z ]{1,50}", name):
            abort(400, description="Invalid characters in 'name'. Letters and spaces only.")

        return f"Hello, {name}!"

    return app

if __name__ == "__main__":
    app = create_app()
    # Development: use built-in server
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG'],
    )
    # Production: run with Gunicorn
    # e.g., gunicorn "app:create_app()"
