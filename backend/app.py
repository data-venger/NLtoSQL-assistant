"""Warehouse SQL Assistant — Flask backend entry point."""

import logging
from flask import Flask
from flask_cors import CORS
from config import config

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(asctime)s %(name)s — %(message)s",
)


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = config.SECRET_KEY

    # Enable CORS for local frontend dev
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register blueprints
    from routes.chat import bp as chat_bp
    from routes.database import bp as db_bp
    from routes.embeddings import bp as emb_bp

    app.register_blueprint(chat_bp)
    app.register_blueprint(db_bp)
    app.register_blueprint(emb_bp)

    # Health check
    @app.route("/api/health")
    def health():
        return {"status": "ok"}

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5001, debug=config.DEBUG)
