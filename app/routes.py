from flask import Blueprint, request, jsonify

pedidos_bp = Blueprint('pedidos', __name__)

# Lista para armazenar pedidos temporariamente (simulando um banco de dados)
pedidos = []

@pedidos_bp.route('/api/pedidos-autorizacao', methods=['POST', 'GET'])
def gerenciar_pedidos():
    """ 
    POST: Cria um novo pedido de autorização de serviço 
    GET: Retorna todos os pedidos cadastrados
    """
    
    if request.method == 'POST':
        data = request.get_json()

        # Verificação de campos obrigatórios
        required_fields = ["empresa_responsavel", "embarcacoes", "veiculos", "servico", "equipe"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Campo obrigatório '{field}' está faltando"}), 400

        # Simulação de ID único do pedido
        pedido_id = len(pedidos) + 1
        data["id"] = pedido_id
        pedidos.append(data)

        return jsonify({"message": "Pedido de autorização criado com sucesso!", "id": pedido_id}), 201

    elif request.method == 'GET':
        return jsonify({"pedidos": pedidos}), 200  # Retorna todos os pedidos cadastrados
