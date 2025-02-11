import os

class Config:
    """Configuração base (usada por todos os ambientes)."""
    SECRET_KEY = os.getenv("SECRET_KEY", "minha_chave_secreta")
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    """Configuração para Desenvolvimento."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(Config.BASE_DIR, 'instance', 'database.db')}"

class TestingConfig(Config):
    """Configuração para Testes (usada no GitHub Actions e pytest)."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(Config.BASE_DIR, 'instance', 'test_database.db')}"

class StagingConfig(Config):
    """Configuração para Staging."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(Config.BASE_DIR, 'instance', 'staging_database.db')}"

#class ProductionConfig(Config):
#    """Configuração para Produção."""
#    DEBUG = False
#    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(Config.BASE_DIR, 'instance', 'prod_database.db')}")

class ProductionConfig(Config):
    """Configuração para Produção utilizando SQL."""
    DEBUG = False
    # Exige que a variável de ambiente DATABASE_URL esteja definida.
    SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URL"]

config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "staging": StagingConfig,
    "production": ProductionConfig
}