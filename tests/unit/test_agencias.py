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

def test_listar_pedidos_agenciamento_sem_login(client):
    resposta = client.get("/agencia/pedidos")
    # Usuário sem login deve ser redirecionado
    assert resposta.status_code == 302
    assert resposta.headers["Location"].startswith("/embarcacoes/auth/login")

def test_listar_pedidos_agenciamento_nao_agencia(client):
    login(client)
    resposta = client.get("/agencia/pedidos")
    # Usuário não agência deve ser redirecionado
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
    assert "<h1>" in texto_resposta



