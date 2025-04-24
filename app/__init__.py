from flask import Flask
from flask_cors import CORS
import os

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.secret_key = os.getenv("SECRET_KEY", "segredo-temporario")

    from .routes import main
    app.register_blueprint(main)

    os.makedirs("logs", exist_ok=True)

    return app
