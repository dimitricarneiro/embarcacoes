from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(config["development"])  # Usando a configuração de desenvolvimento

    db.init_app(app)  # Inicializa o banco de dados

    from app.routes import pedidos_bp
    app.register_blueprint(pedidos_bp)

    return app
