import pytest
from app import create_app
from tests.unit.test_pedidos import login, login_admin  # 🔹 Importa a função login

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def teste_acesso_login_get(client):
    resposta = client.get("/auth/login")
    assert resposta.status_code == 200
    texto_resposta = resposta.get_data(as_text=True)
    assert "login" in texto_resposta.lower()

def teste_login_post_invalido(client):
    resposta = client.post("/auth/login", data={"username": "inexistente", "password": "errada"}, follow_redirects=True)
    assert resposta.status_code == 200
    texto_resposta = resposta.get_data(as_text=True)
    assert "credenciais inválidas" in texto_resposta.lower()

def teste_login_post_valido_regular(client):
    login(client)
    resposta = client.get("/lista-pedidos")
    assert resposta.status_code == 200
    texto_resposta = resposta.get_data(as_text=True)
    assert "pedidos" in texto_resposta.lower()

def teste_login_post_valido_admin(client):
    login_admin(client)
    resposta = client.get("/admin")
    assert resposta.status_code == 200
    texto_resposta = resposta.get_data(as_text=True)
    assert "admin" in texto_resposta.lower()

def teste_renovar_sessao(client):
    login(client)
    resposta = client.get("/auth/renovar-sessao")
    assert resposta.status_code == 200
    dados = resposta.get_json()
    assert dados.get("message") == "Sessão renovada"

def teste_logout(client):
    login(client)
    resposta = client.get("/auth/logout", follow_redirects=True)
    assert resposta.status_code == 200
    texto_resposta = resposta.get_data(as_text=True)
    assert "login" in texto_resposta.lower()
