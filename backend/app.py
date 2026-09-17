from flask import Flask
from flask_cors import CORS

from config import Config
from database.mongodb import init_mongodb

from routes import main
from routes.auth import auth_bp
from routes.upload import upload_bp
from routes.decrypt import decrypt_bp


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    CORS(app)

    # Initialize MongoDB
    init_mongodb()

    # Register routes
    app.register_blueprint(main)

    app.register_blueprint(
        auth_bp,
        url_prefix="/api/auth"
    )

    app.register_blueprint(
        upload_bp,
        url_prefix="/api"
    )

    app.register_blueprint(
        decrypt_bp,
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