import pytest
from app import create_app
from tests.unit.test_pedidos import login  # 🔹 Importa a função login

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_route(client):
    response = client.get('/')
    assert response.status_code == 302
    assert "Location" in response.headers  # 🔹 Confirma que há um cabeçalho de redirecionamento
    assert response.headers["Location"].startswith("/auth/login")

def test_acesso_sem_login_formulario_pedido(client):
    """Teste para verificar que usuários não autenticados são redirecionados (302) ao tentar acessar /formulario-pedido"""

    response = client.get("/formulario-pedido", follow_redirects=False)
    
    assert response.status_code == 302  # 🔹 Confirma que há um redirecionamento
    assert "Location" in response.headers  # 🔹 Confirma que há um cabeçalho de redirecionamento
    assert response.headers["Location"].startswith("/auth/login")
  
def test_acesso_com_login_formulario_pedido(client):
    """Teste para verificar se o formulário de pedido é carregado corretamente"""

    # 🔹 Primeiro, faz login
    login(client)

    response = client.get("/formulario-pedido")  # Faz uma requisição GET para a rota
    
    assert response.status_code == 200  # Verifica se a página carregou corretamente
    html_content = response.data.decode("utf-8")  # Converte bytes para string
    
    assert "<title>Cadastrar Pedido de Autorização</title>" in html_content  # Verifica se o título está presente no HTML
    assert "<form" in html_content  # Verifica se há um formulário na resposta HTML
    assert "Enviar Pedido de Autorização" in html_content  # Verifica se o botão está presente

def teste_redirecionamento_home_sem_login(client):
    resposta = client.get("/")
    # Usuário não autenticado deve ser redirecionado para /auth/login
    assert resposta.status_code == 302
    assert "/auth/login" in resposta.location

def teste_redirecionamento_home_com_login(client):
    login(client)
    resposta = client.get("/")
    # Usuário autenticado deve ser redirecionado para /lista-pedidos
    assert resposta.status_code == 302
    assert "/lista-pedidos" in resposta.location

def teste_exibir_lista_de_pedidos(client):
    login(client)
    resposta = client.get("/lista-pedidos")
    assert resposta.status_code == 200
    texto_resposta = resposta.get_data(as_text=True)
    assert "<html" in texto_resposta.lower()

def teste_exibir_detalhes_pedido_nao_encontrado(client):
    login(client)
    resposta = client.get("/pedido/99999")
    assert resposta.status_code == 404