import pytest
from app import create_app
from tests.unit.test_pedidos import login  # 🔹 Importa a função login corretamente

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.text == "<h1>Bem-vindo ao sistema de pedidos de autorização</h1>"
    
def test_exibir_formulario_pedido(client):
    """Teste para verificar se o formulário de pedido é carregado corretamente"""

    # 🔹 Primeiro, faz login
    login(client)

    response = client.get("/formulario-pedido")  # Faz uma requisição GET para a rota
    
    assert response.status_code == 200  # Verifica se a página carregou corretamente
    html_content = response.data.decode("utf-8")  # Converte bytes para string
    
    assert "<title>Pedido de Autorização</title>" in html_content  # Verifica se o título está presente no HTML
    assert "<form" in html_content  # Verifica se há um formulário na resposta HTML
    assert "Enviar Pedido" in html_content  # Verifica se o botão está presente

