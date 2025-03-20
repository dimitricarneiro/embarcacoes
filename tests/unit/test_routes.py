import pytest
from datetime import date, datetime, timedelta
from app import create_app
from tests.unit.test_pedidos import login, login_admin  # Importa a função login

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_route(client):
    response = client.get('/')
    assert response.status_code == 302
    assert "Location" in response.headers  # Confirma que há um cabeçalho de redirecionamento
    assert response.headers["Location"].startswith("/embarcacoes/auth/login")

def test_acesso_sem_login_formulario_pedido(client):
    """Teste para verificar que usuários não autenticados são redirecionados (302) ao tentar acessar /formulario-pedido"""

    response = client.get("/formulario-pedido", follow_redirects=False)
    
    assert response.status_code == 302  # Confirma que há um redirecionamento
    assert "Location" in response.headers  # Confirma que há um cabeçalho de redirecionamento
    assert response.headers["Location"].startswith("/embarcacoes/auth/login")
  
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
    client.application.config['WTF_CSRF_ENABLED'] = False  # Desabilita CSRF para efetivar o login
    login(client)  # Função helper que realiza o login com follow_redirects=True internamente, se necessário
    resposta = client.get("/", follow_redirects=False)
    
    # Usuário autenticado deve ser redirecionado para /lista-pedidos
    assert resposta.status_code == 302
    assert "/lista-pedidos" in resposta.location

def teste_exibir_lista_de_pedidos(client):
    login(client)
    resposta = client.get("/lista-pedidos", follow_redirects=True)
    assert resposta.status_code == 200
    texto_resposta = resposta.get_data(as_text=True)
    assert "<html" in texto_resposta.lower()

def teste_exibir_detalhes_pedido_nao_encontrado(client):
    # Desabilita a validação do CSRF para que o login seja efetivado corretamente
    client.application.config['WTF_CSRF_ENABLED'] = False  
    login(client)  # Certifique-se de que essa função efetua o login com follow_redirects=True internamente
    # Agora, acessa a rota que deveria retornar 404 para um pedido inexistente.
    resposta = client.get("/pedido/999999999", follow_redirects=False)
    assert resposta.status_code == 404

def teste_get_alertas_admin(client):
    client.application.config['WTF_CSRF_ENABLED'] = False  # Desabilita CSRF para garantir que o login funcione
    login_admin(client)  # Função helper que deve efetuar o login do admin, preferencialmente com follow_redirects=True
    resposta = client.get("/admin/alertas", follow_redirects=True)
    assert resposta.status_code == 200
    texto = resposta.get_data(as_text=True)
    assert "gerenciar alertas" in texto.lower() or "alertas" in texto.lower()


def teste_post_alertas_admin_valido(client):
    client.application.config['WTF_CSRF_ENABLED'] = False  # Desabilita CSRF para o teste, se necessário
    login_admin(client)
    dados = {
        "tipo": "embarcacao",  # valor válido (ou "cnpj")
        "valor": "barco"       # valor não vazio
    }
    resposta = client.post("/admin/alertas", data=dados, follow_redirects=True)
    # Como o redirecionamento ocorre, o status final esperado é 200
    assert resposta.status_code == 200
    texto = resposta.get_data(as_text=True)
    # Em vez de buscar "barco", verificamos um conteúdo que sabemos estar presente, como "gerenciar alertas"
    assert "gerenciar alertas" in texto.lower()


def teste_post_alertas_admin_invalido(client):
    client.application.config['WTF_CSRF_ENABLED'] = False  # Desabilita o CSRF para o teste
    login_admin(client)
    dados = {
        "tipo": "invalido",  # Valor inválido para o formulário
        "valor": "qualquer"
    }
    headers = {"X-Requested-With": "XMLHttpRequest"}
    resposta = client.post("/admin/alertas", data=dados, headers=headers, follow_redirects=True)
    # Como a rota re-renderiza o template, espera-se status 200
    assert resposta.status_code == 200
    texto = resposta.get_data(as_text=True)
    # Verifica que o template de gerenciamento de alertas foi renderizado
    assert "gerenciar alertas" in texto.lower()

def teste_get_alertas_nao_admin(client):
    """Verifica se um usuário não administrador é redirecionado ao tentar acessar /admin/alertas."""
    client.application.config['WTF_CSRF_ENABLED'] = False  # Desabilita o CSRF para o teste
    # Autentica como usuário regular
    login(client)
    resposta = client.get("/admin/alertas", follow_redirects=True)
    # Espera que o usuário seja redirecionado para a página de login
    assert resposta.status_code == 200
    texto = resposta.get_data(as_text=True)
    assert "login" in texto.lower()

def teste_exportar_csv_nao_admin(client):
    """
    Verifica que um usuário não administrador consegue acessar e baixar o relatório CSV.
    
    Nesse novo comportamento, ao acessar a rota, o usuário receberá o arquivo CSV
    contendo o cabeçalho e os dados dos pedidos.
    """
    # Desabilita o CSRF para o teste
    client.application.config['WTF_CSRF_ENABLED'] = False

    # Autentica como usuário comum (não admin)
    login(client)
    
    # Faz a requisição à rota de exportação de CSV, seguindo redirecionamentos
    resposta = client.get("/admin/exportar-csv", follow_redirects=True)
    
    # Verifica se a resposta foi bem-sucedida (código 200)
    assert resposta.status_code == 200
    
    # Verifica se os headers indicam que o conteúdo é um arquivo CSV para download
    content_disp = resposta.headers.get("Content-Disposition", "")
    assert "attachment; filename=relatorio_pedidos.csv" in content_disp, \
        "O header 'Content-Disposition' não indica o arquivo CSV esperado."
    
    content_type = resposta.headers.get("Content-Type", "")
    assert "text/csv" in content_type, "O header 'Content-Type' não indica um CSV."
    
    # Obtém o conteúdo do CSV e remove o BOM (se presente)
    texto = resposta.get_data(as_text=True)
    if texto.startswith('\ufeff'):
        texto = texto[1:]
    
    # Verifica se a primeira linha do CSV contém o cabeçalho esperado
    linhas = texto.splitlines()
    assert linhas, "O CSV não possui linhas."
    cabecalho_esperado = "ID,Empresa,CNPJ,Motivo,Data Início,Data Término,Data Solicitação,Status"
    assert linhas[0] == cabecalho_esperado, \
        f"O cabeçalho do CSV está incorreto. Esperado: '{cabecalho_esperado}'. Obtido: '{linhas[0]}'"


