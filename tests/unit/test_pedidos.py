import pytest
from app import create_app

@pytest.fixture
def client():
    """Configura um cliente de teste para o Flask"""
    app = create_app()
    app.config['TESTING'] = True  # Modo de teste ativado
    with app.test_client() as client:
        yield client

def test_criar_pedido_autorizacao(client):
    """Teste para criar um novo pedido de autorização de serviço"""
    
    # JSON de exemplo para o teste
    novo_pedido = {
        "empresa_responsavel": "Empresa XYZ",
        "embarcacoes": ["Embarcação A", "Embarcação B"],
        "veiculos": ["Caminhão 123", "Carro XYZ"],
        "servico": "Manutenção no motor",
        "equipe": [
            {"nome": "João Silva", "funcao": "Mecânico"},
            {"nome": "Maria Souza", "funcao": "Supervisor"}
        ]
    }
    
    response = client.post("/api/pedidos-autorizacao", json=novo_pedido)
    
    assert response.status_code == 201  # Código HTTP de sucesso para criação
    assert response.json["message"] == "Pedido de autorização criado com sucesso!"
