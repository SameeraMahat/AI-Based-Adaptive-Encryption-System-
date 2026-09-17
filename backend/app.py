from flask import Flask
from flask_cors import CORS

from config import Config
from database.models import db
from extensions import bcrypt
from routes import main
from routes.auth import auth_bp
from routes.upload import upload_bp
from routes.decrypt import decrypt_bp


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    CORS(app)

    bcrypt.init_app(app)

    db.init_app(app)

    app.register_blueprint(main)
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(upload_bp, url_prefix="/api")
    app.register_blueprint(decrypt_bp, url_prefix="/api")

    with app.app_context():
        db.create_all()

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )