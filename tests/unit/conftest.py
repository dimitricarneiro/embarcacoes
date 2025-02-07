# tests/conftest.py
import os
import sys
import tempfile
import pytest
from app import create_app, db
from app.models import Usuario

# Insere o diretório raiz do projeto no sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

@pytest.fixture
def app():
    # Cria um banco de dados temporário
    db_fd, db_path = tempfile.mkstemp()
    config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///" + db_path,
        "WTF_CSRF_ENABLED": False,
    }
    app = create_app()
    app.config.update(config)
    
    with app.app_context():
        db.create_all()
        # Cria um usuário administrador e um usuário comum
        admin_user = Usuario(username="admin", role="RFB")
        admin_user.set_password("adminpass")
        regular_user = Usuario(username="user", role="comum")
        regular_user.set_password("userpass")
        db.session.add_all([admin_user, regular_user])
        db.session.commit()
        
    yield app

    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

def login(client, username, password):
    """Helper para logar o usuário via rota de login."""
    return client.post("/auth/login", data={
        "username": username,
        "password": password
    }, follow_redirects=True)
