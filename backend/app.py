from flask import Flask
from flask_cors import CORS

from config import Config
from database.mongodb import init_mongodb

from routes import main
from routes.auth import auth_bp
from routes.upload import upload_bp
from routes.decrypt import decrypt_bp
from routes.history import history_bp
from routes.dashboard import dashboard_bp
from routes.settings import settings_bp
from routes.support import support_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Allow requests from the React/Vite frontend
    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": [
                    "http://localhost:5173",
                    "http://127.0.0.1:5173",
                ]
            }
        },
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=[
    "Content-Type",
    "Authorization",
    "X-Decrypt-Token",
],
        expose_headers=[
            "X-Decryption-Algorithm",
            "X-Decryption-Status",
            "X-Original-Filename",
        ],
    )

    # Initialize MongoDB
    init_mongodb()

    # Register routes
    app.register_blueprint(main)

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(upload_bp, url_prefix="/api")
    app.register_blueprint(decrypt_bp, url_prefix="/api")
    app.register_blueprint(history_bp, url_prefix="/api")
    app.register_blueprint(dashboard_bp, url_prefix="/api")
    app.register_blueprint(settings_bp, url_prefix="/api/settings")
    app.register_blueprint(support_bp, url_prefix="/api/support")

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
    )
