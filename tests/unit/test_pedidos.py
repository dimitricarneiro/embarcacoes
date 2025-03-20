import pytest
from app import create_app
from datetime import datetime, timedelta

@pytest.fixture
def client():
    """Configura um cliente de teste para o Flask"""
    app = create_app()
    app.config['TESTING'] = True  # Modo de teste ativado
    with app.test_client() as client:
        yield client

def login(client):
    """Função auxiliar para autenticar o usuário de teste"""
    credenciais = {
        "username": "usuario",
        "password": "123456"
    }
    response = client.post("/auth/login", data=credenciais, follow_redirects=True)

    print("Headers da resposta de login:", response.headers)

    # 🔹 Mantém a sessão do usuário ativa no cliente de testes
    with client.session_transaction() as sess:
        sess.permanent = True  # Força a sessão a ser mantida
        print("Sessão ativa após login:", sess)  # Verifica se a sessão está carregada corretamente
    
    assert response.status_code == 200  # Confirma que o login foi bem-sucedido
    return response

def login_admin(client):
    """Função auxiliar para autenticar o usuário de teste como admin"""
    credenciais = {
        "username": "admin",
        "password": "123456"
    }
    response = client.post("/auth/login", data=credenciais, follow_redirects=True)

    print("Headers da resposta de login:", response.headers)

    # 🔹 Mantém a sessão do usuário ativa no cliente de testes
    with client.session_transaction() as sess:
        sess.permanent = True  # Força a sessão a ser mantida
        print("Sessão ativa após login:", sess)  # Verifica se a sessão está carregada corretamente
    
    assert response.status_code == 200  # Confirma que o login foi bem-sucedido
    return response

def login_agencia(client):
    """Função auxiliar para autenticar o usuário de teste"""
    credenciais = {
        "username": "agencia",
        "password": "123456"
    }
    response = client.post("/auth/login", data=credenciais, follow_redirects=True)

    print("Headers da resposta de login:", response.headers)

    # 🔹 Mantém a sessão do usuário ativa no cliente de testes
    with client.session_transaction() as sess:
        sess.permanent = True  # Força a sessão a ser mantida
        print("Sessão ativa após login:", sess)  # Verifica se a sessão está carregada corretamente
    
    assert response.status_code == 200  # Confirma que o login foi bem-sucedido
    return response

def test_criar_pedido_autorizacao_com_login(client):
    client.application.config['WTF_CSRF_ENABLED'] = False  # Desabilita o CSRF para os testes
    login(client)  # Garante que o usuário está autenticado

    # Gera datas dinâmicas para que 'data_inicio' seja amanhã e 'data_termino' alguns dias depois (dentro de 90 dias e com duração máxima de 5 dias)
    hoje = datetime.today()
    data_inicio = (hoje + timedelta(days=1)).strftime("%Y-%m-%d")
    data_termino = (hoje + timedelta(days=3)).strftime("%Y-%m-%d")

    novo_pedido = {
        "nome_empresa": "Empresa XYZ",
        "cnpj_empresa": "75.092.881/0001-17",
        "endereco_empresa": "Rua Exemplo, 123",
        "motivo_solicitacao": "Inspeção de casco",
        "data_inicio": data_inicio,
        "data_termino": data_termino,
        "horario_inicio_servicos": "08:00",
        "horario_termino_servicos": "18:00",
        "certificado_livre_pratica": "ABC123",
        "cidade_servico": "Cidade Exemplo",
        "observacoes": "Serviço sujeito a alteração",
        "agencia_maritima": "Agência Marítima XYZ",
        "cnpj_agencia": "93.474.269/0001-90",
        "termo_responsabilidade": True,
        "embarcacoes": [
            {
                "nome": "Embarcação A",
                "imo": "1234567",
                "bandeira": "Bandeira A"
            }
        ],
        "equipamentos": [
            {
                "descricao": "Equipamento A",
                "numero_serie": "SERIE123",
                "quantidade": 1
            }
        ],
        "pessoas": [
            {
                "nome": "João Silva",
                "cpf": "969.281.130-14",
                "funcao": "Engenheiro",
                "local_embarque": "Porto A",
                "local_desembarque": "Porto B"
            }
        ],
        "veiculos": [
            {
                "modelo": "Modelo A",
                "placa": "ABC1234"
            }
        ]
    }
    
    response = client.post("/api/pedidos-autorizacao", json=novo_pedido)

    # Verificações atualizadas
    assert response.status_code == 200  # Agora espera 200
    assert "redirect_url" in response.json  # Verifica se 'redirect_url' foi retornado

def test_criar_pedido_autorizacao_sem_login(client):
    """Teste para criar um novo pedido de autorização de serviço sem estar autenticado"""
    
    # JSON atualizado para o novo formato do pedido
    novo_pedido = {
        "nome_empresa": "Empresa XYZ",
        "cnpj_empresa": "75.371.927/0001-37",
        "endereco_empresa": "Rua Exemplo, 123",
        "motivo_solicitacao": "Manutenção no motor",
        "data_inicio_servico": "2025-02-01",
        "data_termino_servico": "2025-02-10",
        "horario_servicos": "08:00 - 18:00",
        "num_certificado_livre_pratica": "ABC123",
        "observacoes": "Serviço sujeito a alteração",
        "embarcacoes": [
            {
                "nome_embarcacao": "Embarcação A",
                "bandeira_embarcacao": "Brasil",
                "imo_embarcacao": "1234567",
                "local_embarque": "Porto A",
                "local_desembarque": "Porto B",
                "local_embarque_equipamentos": "Terminal X",
                "local_desembarque_equipamentos": "Terminal Y"
            }
        ],
        "equipamentos": [
            {
                "descricao_equipamento": "Caminhão 123",
                "patrimonio_num_serie_modelo": "CAM-001",
                "quantidade": 1
            }
        ],
        "pessoas": [
            {
                "nome": "João Silva",
                "cpf": "123.456.789-00",
                "funcao": "Mecânico",
                "isps": 123456789
            }
        ]
    }
    
    # 🔹 Agora, faz a requisição para criar o pedido
    response = client.post("/api/pedidos-autorizacao", json=novo_pedido)
    
    # Verificações
    assert response.status_code == 302  # Código HTTP correto
