from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_login import LoginManager

db = SQLAlchemy()

login_manager = LoginManager()
login_manager.login_view = "auth.login"  # Redireciona usuários não autenticados para o login

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'chave-super-secreta'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    
    db.init_app(app)
    login_manager.init_app(app)

    from app.routes import pedidos_bp
    from app.auth_routes import auth_bp  # Criamos esse módulo para autenticação
    app.register_blueprint(pedidos_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')

    return app

from app.models import Usuario

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))
