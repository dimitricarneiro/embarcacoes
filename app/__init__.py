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

# Inicializa o Flask-Limiter para controle de tentativas de login
limiter = Limiter(
    key_func=get_remote_address,  # Usa o IP do usuário para limitar requisições
    default_limits=["30 per minute"]  # Limite padrão de 30 requisições por minuto
)

def create_app():
    """Cria a aplicação Flask com base no ambiente configurado."""
    app = Flask(__name__, instance_relative_config=True)
    
    # Configura o esquema preferencial para URLs externas
    app.config['PREFERRED_URL_SCHEME'] = 'https'

    # Carrega a configuração do ambiente
    env = os.getenv("FLASK_ENV", "development")  # Obtém o ambiente do sistema (default: development)
    app.config.from_object(config[env])  # Usa a configuração correspondente do `config.py`

    print(f"🚀 Rodando no ambiente: {env}")

    # Tempo de expiração da sessão
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)

    # Inicializa extensões
    db.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)

    # Registra os Blueprints
    from app.routes import pedidos_bp
    from app.auth_routes import auth_bp
    from app.users_routes import users_bp
    app.register_blueprint(pedidos_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(users_bp)
    
    # Registra o Blueprint das agências
    from app.agencias_routes import agencias_bp
    app.register_blueprint(agencias_bp)
    
    # Configura o sistema de logging
    from logging_config import setup_logging
    setup_logging(app)
    
    # Registra o filter customizado para ajuste de fuso horário
    @app.template_filter('localize')
    def localize_time(dt):
        """
        Converte a data/hora de GMT para o fuso horário local (GMT-3).

        Args:
            dt (datetime): Data/hora em GMT.
        
        Returns:
            datetime: Data/hora ajustada para o fuso horário local.
        """
        return dt - timedelta(hours=3)

    return app

# Carregamento do usuário para o Flask-Login
from app.models import Usuario

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))
