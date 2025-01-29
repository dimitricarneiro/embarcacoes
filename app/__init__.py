from flask import Flask
from .routes import pedidos_bp  # Importação relativa


def create_app():
    app = Flask(__name__)
    app.config.from_object('config')

    # Registrando a rota de pedidos
    app.register_blueprint(pedidos_bp)

    return app
