import pytest
from datetime import date, datetime, timedelta
from app import create_app
from tests.unit.test_pedidos import login, login_agencia  # Importa a função login

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# tests/unit/utils.py

def login_as_user(client, username="user"):
    """
    Autentica o cliente de teste como o usuário cujo username foi carregado
    pelo conftest.py. Em vez de postar no /auth/login, a gente injeta
    diretamente na sessão os dados do Flask-Login.
    """
    # Primeiro, descubra qual é o ID daquele username
    # (não precisa de app_context, pois o client já carrega o app)
    from app.models import Usuario
    with client.application.app_context():
        user = Usuario.query.filter_by(username=username).first()
        assert user, f"Usuário '{username}' não existe no teste"

    # Agora injete na sessão o _user_id e declare a sessão "fresh"
    with client.session_transaction() as sess:
        sess['_user_id'] = str(user.id)
        sess['_fresh'] = True



def test_listar_pedidos_agenciamento_sem_login(client):
    resposta = client.get("/agencia/pedidos")
    # Usuário sem login deve ser redirecionado
    assert resposta.status_code == 302
    assert resposta.headers["Location"].startswith("/embarcacoes/auth/login")

def test_listar_pedidos_agenciamento_nao_agencia(client):
    # Autentica como user (role="comum")
    login_as_user(client, username="user")

    resposta = client.get("/agencia/pedidos")
    # Usuário “comum” deve ser redirecionado para login de agência
    assert resposta.status_code == 302
    assert resposta.headers["Location"].startswith("/embarcacoes/auth/login")

def test_listar_pedidos_agenciamento_correto(client):
    """
    Testa que o usuário do tipo agência consegue acessar a rota GET /agencia/pedidos
    e visualizar a listagem de pedidos de agenciamento.
    """
    # Efetua o login do usuário agência
    login_agencia(client)
    
    # Acessa a rota, seguindo quaisquer redirecionamentos
    resposta = client.get("/agencia/pedidos", follow_redirects=True)
    
    # Verifica que a resposta tem status 200
    assert resposta.status_code == 200
    
    # Converte o conteúdo da resposta para string
    texto_resposta = resposta.get_data(as_text=True)
    
    # Verifica se o cabeçalho <h1> com "pedidos de agenciamento" está presente
    assert "<h1" in texto_resposta



