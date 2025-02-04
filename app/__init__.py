import os
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import timedelta
from config import config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"  # Redireciona usuários não autenticados para o login

# ✅ Inicializa o Flask-Limiter para controle de tentativas de login
limiter = Limiter(
    key_func=get_remote_address,  # 🔹 Usa o IP do usuário para limitar requisições
    default_limits=["50 per minute"]  # 🔹 Limite padrão de 50 requisições por minuto
)

def create_app():
    """Cria a aplicação Flask com base no ambiente configurado."""
    app = Flask(__name__, instance_relative_config=True)

    # 🔹 Carrega a configuração do ambiente
    env = os.getenv("FLASK_ENV", "development")  # 🔹 Obtém o ambiente do sistema (default: development)
    app.config.from_object(config[env])  # 🔹 Usa a configuração correspondente do `config.py`

    print(f"🚀 Rodando no ambiente: {env}")

    # ✅ Tempo de expiração da sessão
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=10)

    # ✅ Inicializa extensões
    db.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)

    # ✅ Registra os Blueprints
    from app.routes import pedidos_bp
    from app.auth_routes import auth_bp
    app.register_blueprint(pedidos_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")

    return app

# 🔹 Carregamento do usuário para o Flask-Login
from app.models import Usuario

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


