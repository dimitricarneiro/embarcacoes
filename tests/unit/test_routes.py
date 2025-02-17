import pytest
from datetime import date, datetime, timedelta
from app import create_app
from tests.unit.test_pedidos import login, login_admin  # 🔹 Importa a função login

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
    client.application.config['WTF_CSRF_ENABLED'] = False  # Desabilita o CSRF para o teste
    login(client)  # Certifique-se de que essa função realiza o login com follow_redirects=True internamente
    response = client.get("/formulario-pedido", follow_redirects=True)
    
    assert response.status_code == 200
    html_content = response.data.decode("utf-8")
    
    assert "Cadastrar Pedido de Autorização" in html_content  # Verifica se o título esperado está presente
    assert "<form" in html_content
    assert "Enviar Pedido de Autorização" in html_content


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

def teste_get_alertas_admin(client):
    """Verifica se um administrador pode acessar a página de alertas via GET."""
    # Autentica como administrador
    login_admin(client)
    resposta = client.get("/admin/alertas")
    # Espera status 200 e o template da página de alertas
    assert resposta.status_code == 200
    texto = resposta.get_data(as_text=True)
    # Verifica se algum conteúdo esperado do template (por exemplo, título ou palavra-chave) está presente.
    # Ajuste a verificação conforme o conteúdo do seu template.
    assert "gerenciar alertas" in texto.lower() or "alertas" in texto.lower()

def teste_post_alertas_admin_valido(client):
    """Verifica se um administrador consegue criar um alerta com dados válidos."""
    # Autentica como administrador
    login_admin(client)
    dados = {
        "tipo": "embarcacao",  # valor válido (ou "cnpj")
        "valor": "barco"       # valor não vazio
    }
    resposta = client.post("/admin/alertas", data=dados, follow_redirects=True)
    # Como o redirecionamento ocorre, o status final esperado é 200 (após a renderização do template)
    assert resposta.status_code == 200
    texto = resposta.get_data(as_text=True)
    # Opcionalmente, verifique se o template renderizado indica que o alerta foi criado.
    # Se o template listar os alertas criados, você pode buscar o valor "barco" nele.
    assert "barco" in texto.lower() or "alertas" in texto.lower()

def teste_post_alertas_admin_invalido(client):
    """Verifica se o sistema retorna erro quando os dados para criar um alerta são inválidos."""
    # Autentica como administrador
    login_admin(client)
    # Usa um 'tipo' inválido (não está na lista ["embarcacao", "cnpj"])
    dados = {
        "tipo": "invalido",
        "valor": "qualquer"
    }
    resposta = client.post("/admin/alertas", data=dados)
    # Espera status 400 e resposta JSON com mensagem de erro
    assert resposta.status_code == 400
    dados_resposta = resposta.get_json()
    assert "error" in dados_resposta
    assert "Dados inválidos" in dados_resposta["error"]

def teste_get_alertas_nao_admin(client):
    """Verifica se um usuário não administrador é redirecionado ao tentar acessar /admin/alertas."""
    # Autentica como usuário regular
    login(client)
    resposta = client.get("/admin/alertas", follow_redirects=True)
    # Como o usuário não admin é redirecionado para a página de exibição de pedidos, espera-se status 200
    # e conteúdo esperado dessa página.
    assert resposta.status_code == 200
    texto = resposta.get_data(as_text=True)
    # Verifica se o template exibido pertence à área de pedidos.
    # Ajuste a verificação conforme o conteúdo do seu template para 'exibir_pedidos'.
    assert "pedidos" in texto.lower()

def teste_exportar_csv_nao_admin(client):
    """
    Verifica que um usuário não administrador é redirecionado ao tentar acessar a rota de exportação de CSV.
    """
    # Autentica como usuário comum
    login(client)
    
    # Faz a requisição à rota de exportação de CSV
    resposta = client.get("/admin/exportar-csv", follow_redirects=True)
    # Como o usuário não é admin, espera-se ser redirecionado para a página de exibição de pedidos.
    # Como usamos follow_redirects=True, o status final provavelmente será 200,
    # e o conteúdo renderizado deve conter elementos da página de pedidos.
    assert resposta.status_code == 200
    texto = resposta.get_data(as_text=True)
    # Verifica que o texto da resposta contém alguma palavra que identifique a área de pedidos.
    assert "pedidos" in texto.lower()
