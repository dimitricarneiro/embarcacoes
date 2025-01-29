import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "minha_chave_secreta")
    DEBUG = True

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig
}
