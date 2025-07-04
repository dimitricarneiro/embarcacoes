import os

class Config:
    """Configuração base (usada por todos os ambientes)."""
    SECRET_KEY = os.getenv("EMBARCACOES_SECRET_KEY")
    if not SECRET_KEY:
        raise RuntimeError("A variável de ambiente EMBARCACOES_SECRET_KEY não está definida")
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    """Configuração para Desenvolvimento."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(Config.BASE_DIR, 'instance', 'database.db')}"
    APPLICATION_ROOT = '/embarcacoes'
    # Define o caminho do cookie de sessão para incluir o prefixo
    SESSION_COOKIE_PATH = '/embarcacoes'

class TestingConfig(Config):
    """Configuração para Testes (usada no GitHub Actions e pytest)."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(Config.BASE_DIR, 'instance', 'test_database.db')}"
    APPLICATION_ROOT = '/embarcacoes'
    # Define o caminho do cookie de sessão para incluir o prefixo
    SESSION_COOKIE_PATH = '/embarcacoes'

class StagingConfig(Config):
    """Configuração para Staging."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(Config.BASE_DIR, 'instance', 'staging_database.db')}"

#class ProductionConfig(Config):
#    """Configuração para Produção."""
#    DEBUG = False
#    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(Config.BASE_DIR, 'instance', 'prod_database.db')}")

class ProductionConfig(Config):
#    """Configuração para Produção utilizando SQL."""
    DEBUG = False
    # Exige que a variável de ambiente DATABASE_URL esteja definida.
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(Config.BASE_DIR, 'instance', 'prod_database.db')}")
#    SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URL"]

config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "staging": StagingConfig,
    "production": ProductionConfig
}