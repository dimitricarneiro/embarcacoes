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
    login_admin(client)
    resposta = client.get("/users/")
    assert resposta.status_code == 200
    texto_resposta = resposta.get_data(as_text=True)
    assert "usuários" in texto_resposta.lower()

def teste_acessar_criar_usuario_nao_admin(client):
    login(client)
    resposta = client.get("/users/create")
    # Usuário não administrador deve ser redirecionado
    assert resposta.status_code == 302

def teste_acessar_criar_usuario_admin(client):
    login_admin(client)
    resposta = client.get("/users/create")
    assert resposta.status_code == 200
    texto_resposta = resposta.get_data(as_text=True)
    assert "criar" in texto_resposta.lower()

def teste_post_criar_usuario_campos_obrigatorios(client):
    login_admin(client)
    resposta = client.post("/users/create", data={}, follow_redirects=True)
    assert resposta.status_code == 200
    texto_resposta = resposta.get_data(as_text=True)
    assert "usuário e senha são obrigatórios" in texto_resposta.lower()

def teste_post_criar_usuario_username_duplicado(client):
    login_admin(client)
    # Cria um usuário com username "novo"
    client.post("/users/create", data={
        "username": "novo",
        "password": "novopass",
        "nome_empresa": "Empresa Novo",
        "cnpj": "",
        "role": "comum"
    }, follow_redirects=True)
    # Tenta criar outro usuário com o mesmo username
    resposta = client.post("/users/create", data={
        "username": "novo",
        "password": "novopass",
        "nome_empresa": "Empresa Novo",
        "cnpj": "",
        "role": "comum"
    }, follow_redirects=True)
    assert resposta.status_code == 200
    texto_resposta = resposta.get_data(as_text=True)
    assert "usuário já existe" in texto_resposta.lower()

def teste_criar_usuario_cnpj_invalido(client):

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
    login(client)
    resposta = client.get("/users/edit/1", follow_redirects=True)
    assert resposta.status_code == 200
    texto_resposta = resposta.get_data(as_text=True)
    # Usuário não admin deve ser redirecionado para a área de pedidos
    assert "pedidos" in texto_resposta.lower()

def teste_acessar_editar_usuario_admin(client):
    login_admin(client)
    # Supondo que o usuário com id 2 exista (usuário regular criado na fixture)
    resposta = client.get("/users/edit/2")
    assert resposta.status_code == 200
    texto_resposta = resposta.get_data(as_text=True)
    assert "editar" in texto_resposta.lower()

#def teste_post_editar_usuario_admin(client):
#    login_admin(client)
#    resposta = client.post("/users/edit/2", data={
#        "username": "user_updated",
#        "nome_empresa": "Empresa Atualizada",
#        "cnpj": "",
#        "role": "comum",
#        "password": "newpass"
#    }, follow_redirects=True)
#    assert resposta.status_code == 200
#    texto_resposta = resposta.get_data(as_text=True)
#    assert "atualizado com sucesso" in texto_resposta.lower()

def teste_excluir_usuario_nao_admin(client):
    login(client)
    resposta = client.post("/users/delete/2")
    texto_resposta = resposta.get_data(as_text=True)
    assert resposta.status_code == 302

#def teste_excluir_usuario_admin(client, app):
#    login_admin(client)
#    with app.app_context():
#        from app.models import Usuario
#        novo = Usuario(username="delete_me", role="comum")
#        novo.set_password("temp")
#        db = app.extensions["sqlalchemy"].db
#        db.session.add(novo)
#        db.session.commit()
#        user_id = novo.id
#    resposta = client.post(f"/users/delete/{user_id}", follow_redirects=True)
#    assert resposta.status_code == 200
#    texto_resposta = resposta.get_data(as_text=True)
#    assert "excluído com sucesso" in texto_resposta.lower()
