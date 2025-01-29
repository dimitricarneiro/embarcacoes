from flask import Flask

def create_app():
    app = Flask(__name__)

    # Configurações do app podem ser carregadas aqui
    app.config.from_object('config')

    # Importa e registra as rotas
    from app.routes import register_routes
    register_routes(app)

    return app
