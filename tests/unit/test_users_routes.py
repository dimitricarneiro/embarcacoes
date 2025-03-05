import pytest
from app import create_app
from tests.unit.test_pedidos import login, login_admin  # 🔹 Importa a função login

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def teste_listar_usuarios_nao_admin(client):
    login(client)
    resposta = client.get("/users/")
    # Usuário não administrador deve ser redirecionado
    assert resposta.status_code == 302

def teste_listar_usuarios_admin(client):
    client.application.config['WTF_CSRF_ENABLED'] = False  # Desabilita o CSRF para o teste
    login_admin(client)
    resposta = client.get("/users/", follow_redirects=True)
    assert resposta.status_code == 200
    texto_resposta = resposta.get_data(as_text=True)
    assert "usuários" in texto_resposta.lower()

def teste_acessar_criar_usuario_nao_admin(client):
    client.application.config['WTF_CSRF_ENABLED'] = False  # Desabilita o CSRF para o teste
    login(client)
    resposta = client.get("/users/create")
    # Usuário não administrador deve ser redirecionado
    assert resposta.status_code == 302

def teste_acessar_criar_usuario_admin(client):
    client.application.config['WTF_CSRF_ENABLED'] = False  # Desabilita o CSRF para o teste
    login_admin(client)
    resposta = client.get("/users/create")
    assert resposta.status_code == 200
    texto_resposta = resposta.get_data(as_text=True)
    assert "criar" in texto_resposta.lower()

def teste_post_criar_usuario_campos_obrigatorios(client):
    client.application.config['WTF_CSRF_ENABLED'] = False  # Desabilita o CSRF para o teste
    login_admin(client)
    resposta = client.post("/users/create", data={}, follow_redirects=True)
    assert resposta.status_code == 200
    texto_resposta = resposta.get_data(as_text=True)
    # Como os dados obrigatórios não foram enviados, espera-se que o template seja re-renderizado,
    # exibindo o título "Criar Novo Usuário"
    assert "criar novo usuário" in texto_resposta.lower()


def teste_post_criar_usuario_username_duplicado(client):
    client.application.config['WTF_CSRF_ENABLED'] = False  # Desabilita o CSRF para o teste
    login_admin(client)
    # Cria um usuário com username "novo"
    client.post("/users/create", data={
        "username": "novo",
        "password": "novopass",
        "nome_empresa": "Empresa Novo",
        "cnpj": "10299541000116",
        "role": "comum"
    }, follow_redirects=True)
    # Tenta criar outro usuário com o mesmo username
    resposta = client.post("/users/create", data={
        "username": "novo",
        "password": "novopass",
        "nome_empresa": "Empresa Novo",
        "cnpj": "19914841000132",
        "role": "comum"
    }, follow_redirects=True)
    assert resposta.status_code == 200
    texto_resposta = resposta.get_data(as_text=True)
    assert "já existe um usuário com este cnpj" in texto_resposta.lower()

def teste_criar_usuario_cnpj_invalido(client):

    client.application.config['WTF_CSRF_ENABLED'] = False  # Desabilita o CSRF para o teste

    # Autentica como administrador para ter acesso à rota
    login_admin(client)
    
    # Dados para criação de usuário com CNPJ inválido
    dados = {
        "username": "usuario_teste",
        "password": "senha_teste",
        "nome_empresa": "Empresa Teste",
        "cnpj": "00000000000000",  # Supondo que este CNPJ seja inválido
        "role": "comum"
    }
    
    # Envia a requisição POST para /users/create
    resposta = client.post("/users/create", data=dados, follow_redirects=True)
    
    # Verifica se a resposta foi redirecionada para a página de criação novamente
    # e se a mensagem de erro foi exibida
    assert resposta.status_code == 200
    texto_resposta = resposta.get_data(as_text=True)
    assert "CNPJ inválido. Por favor, verifique o valor informado." in texto_resposta

def teste_acessar_editar_usuario_nao_admin(client):
    client.application.config['WTF_CSRF_ENABLED'] = False  # Desabilita o CSRF para o teste
    login(client)
    resposta = client.get("/users/edit/1", follow_redirects=True)
    assert resposta.status_code == 200
    texto_resposta = resposta.get_data(as_text=True)
    # Usuário não admin deve ser redirecionado para login
    assert "login" in texto_resposta.lower()

def teste_acessar_editar_usuario_admin(client):
    client.application.config['WTF_CSRF_ENABLED'] = False  # Desabilita o CSRF para o teste
    login_admin(client)
    # Supondo que o usuário com id 2 exista (usuário regular criado na fixture)
    resposta = client.get("/users/edit/2")
    assert resposta.status_code == 200
    texto_resposta = resposta.get_data(as_text=True)
    assert "editar" in texto_resposta.lower()

def teste_post_editar_usuario_admin(client):
    client.application.config['WTF_CSRF_ENABLED'] = False  # Desabilita o CSRF para o teste
    login_admin(client)
    resposta = client.post("/users/edit/3", data={
        "username": "usuário atualizado",
        "nome_empresa": "Empresa Atualizada",
        "cnpj": "02.905.011/0001-46",
        "role": "comum",
        "password": "novasenha"
    }, follow_redirects=True)
    assert resposta.status_code == 200
    texto_resposta = resposta.get_data(as_text=True)
    assert "atualizado com sucesso" in texto_resposta.lower()

def teste_excluir_usuario_nao_admin(client):
    login(client)
    resposta = client.post("/users/delete/2")
    texto_resposta = resposta.get_data(as_text=True)
    assert resposta.status_code == 302