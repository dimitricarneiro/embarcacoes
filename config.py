import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "minha_chave_secreta")
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'database.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig
}
