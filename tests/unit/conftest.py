import os
import sys
import tempfile
import pytest

# Garante que a app consiga iniciar no teste
os.environ.setdefault('EMBARCACOES_SECRET_KEY', 'test_secret_key')

# Insere o diretório raiz do projeto no sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app import create_app, db
from app.models import Usuario
import flask_wtf.csrf as fwcsrf

@pytest.fixture(autouse=True)
def disable_csrf(monkeypatch):
    """
    Desativa a validação de CSRF em todos os testes,
    substituindo a função validate_csrf por um noop.
    """
    monkeypatch.setattr(fwcsrf, "validate_csrf", lambda *args, **kwargs: None)
    yield


@pytest.fixture
def app():
    # banco temporário
    db_fd, db_path = tempfile.mkstemp()
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
        "WTF_CSRF_ENABLED": False,    # CSRF OFF para todos os testes
    })

    with app.app_context():
        db.create_all()
        # Cria usuários com cnpj dummy—só para satisfazer o NOT NULL
        u1 = Usuario(
            username="user",
            role="comum",
            cnpj="00.000.000/0001-91",
            nome_empresa="Empresa Teste"
        )
        u1.set_password("userpass")

        u2 = Usuario(
            username="admin",
            role="RFB",
            cnpj="11.111.111/0001-91",
            nome_empresa="Admin Teste"
        )
        u2.set_password("adminpass")

        u3 = Usuario(
            username="agencia",
            role="agencia_maritima",
            cnpj="22.222.222/0001-91",
            nome_empresa="Agencia Teste"
        )
        u3.set_password("agenciapass")

        db.session.add_all([u1, u2, u3])
        db.session.commit()

    yield app

    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()
