from flask import Flask
from flask_cors import CORS

from config import Config
from database.mongodb import init_mongodb

from routes import main
from routes.auth import auth_bp
from routes.upload import upload_bp
from routes.decrypt import decrypt_bp
from routes.history import history_bp
from routes.analytics import analytics_bp
from routes.dashboard import dashboard_bp


def create_app():

    app = Flask(__name__)

    app.config.from_object(
        Config
    )

    # ========================================================
    # CORS
    # ========================================================

    CORS(
        app,
        expose_headers=[
            "X-Decryption-Algorithm",
            "X-Decryption-Status",
            "X-Original-Filename"
        ]
    )

    # ========================================================
    # INITIALIZE MONGODB
    # ========================================================

    init_mongodb()

    # ========================================================
    # REGISTER MAIN ROUTES
    # ========================================================

    app.register_blueprint(
        main
    )

    # ========================================================
    # AUTH
    # ========================================================

    app.register_blueprint(
        auth_bp,
        url_prefix="/api/auth"
    )

    # ========================================================
    # UPLOAD / ENCRYPTION
    # ========================================================

    app.register_blueprint(
        upload_bp,
        url_prefix="/api"
    )

    # ========================================================
    # DECRYPTION
    # ========================================================

    app.register_blueprint(
        decrypt_bp,
        url_prefix="/api"
    )

    # ========================================================
    # HISTORY
    # ========================================================

    app.register_blueprint(
        history_bp,
        url_prefix="/api"
    )

    # ========================================================
    # ANALYTICS
    # ========================================================

    app.register_blueprint(
        analytics_bp,
        url_prefix="/api"
    )

    # ========================================================
    # DASHBOARD / ENCRYPTION DATABASE
    # ========================================================

    app.register_blueprint(
        dashboard_bp,
        url_prefix="/api"
    )

    return app


app = create_app()


if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )