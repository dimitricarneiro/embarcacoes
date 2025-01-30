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
    
    # JSON atualizado para o novo formato do pedido
    novo_pedido = {
        "nome_empresa": "Empresa XYZ",
        "cnpj_empresa": "00.000.000/0000-00",
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
                "isps": 123456
            }
        ]
    }
    
    response = client.post("/api/pedidos-autorizacao", json=novo_pedido)
    
    assert response.status_code == 201  # Código HTTP de sucesso para criação
    assert "id_autorizacao" in response.json  # Verifica se o ID foi retornado
    assert response.json["message"] == "Pedido de autorização criado com sucesso!"

