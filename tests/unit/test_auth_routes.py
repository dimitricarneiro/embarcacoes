# tests/unit/test_auth_routes.py

import re
import pytest

# pytest já encontra automaticamente o client e o app do tests/conftest.py
# e também a fixture db que cria o esquema e os usuários.

def extrair_csrf(html: str) -> str:
    m = re.search(
        r'<input[^>]+name=["\']csrf_token["\'][^>]+value=["\']([^"\']+)["\']',
        html
    )
    assert m, f"Não encontrei csrf_token no formulário:\n{html}"
    return m.group(1)

def teste_acesso_login_get(client):
    resp = client.get("/auth/login")
    assert resp.status_code == 200
    # basta verificar que o form existe e que há um campo de token
    html = resp.get_data(as_text=True)
    assert "<form" in html.lower()
    assert 'name="csrf_token"' in html

def teste_login_post_invalido(client):
    # GET primeiro para pegar o token
    get0 = client.get("/auth/login")
    token = extrair_csrf(get0.get_data(as_text=True))

    # POST com credenciais inválidas + csrf
    resp = client.post(
        "/auth/login",
        data={
            "username": "inexistente",
            "password": "errada",
            "csrf_token": token
        },
        follow_redirects=True
    )
    assert resp.status_code == 200
    assert "credenciais inválidas. tente novamente." in resp.get_data(as_text=True).lower()

@pytest.mark.parametrize("user,passwd,redirect_url,check_text", [
    ("user",    "userpass",   "/lista-pedidos",   "minhas autorizações"),
    ("admin",   "adminpass",  "/admin",            "admin"),
    ("agencia","agenciapass","/agencia/pedidos",  None),
])
def teste_login_post_valido(client, user, passwd, redirect_url, check_text):
    # GET /auth/login -> extrai csrf
    get0  = client.get("/auth/login")
    token = extrair_csrf(get0.get_data(as_text=True))

    # POST válido
    resp1 = client.post(
        "/auth/login",
        data={
            "username":   user,
            "password":   passwd,
            "csrf_token": token
        },
        follow_redirects=True
    )
    # agora uma requisição GET para a página alvo
    resp2 = client.get(redirect_url, follow_redirects=True)
    assert resp2.status_code == 200
    if check_text:
        assert check_text in resp2.get_data(as_text=True).lower()

def teste_renovar_sessao(client):
    # primeiro faz login válido
    get0  = client.get("/auth/login")
    token = extrair_csrf(get0.get_data(as_text=True))
    client.post("/auth/login",
        data={"username":"user","password":"userpass","csrf_token":token},
        follow_redirects=True
    )

    # GET renova
    resp = client.get("/auth/renovar-sessao")
    assert resp.status_code == 200
    assert resp.get_json().get("message") == "Sessão renovada"

def teste_logout(client):
    # login
    get0  = client.get("/auth/login")
    token = extrair_csrf(get0.get_data(as_text=True))
    client.post("/auth/login",
        data={"username":"user","password":"userpass","csrf_token":token},
        follow_redirects=True
    )

    # logout
    resp = client.get("/auth/logout", follow_redirects=True)
    assert resp.status_code == 200
    assert "login" in resp.get_data(as_text=True).lower()
