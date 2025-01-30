from flask import Blueprint, request, jsonify, render_template

pedidos_bp = Blueprint('pedidos', __name__)

# Lista para armazenar pedidos temporariamente
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
        required_fields = [
            "nome_empresa", "cnpj_empresa", "endereco_empresa", "motivo_solicitacao",
            "data_inicio_servico", "data_termino_servico", "horario_servicos",
            "num_certificado_livre_pratica", "embarcacoes", "equipamentos", "pessoas"
        ]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Campo obrigatório '{field}' está faltando"}), 400

        # **Correção:** Gerar um ID único antes de adicionar o pedido
        pedido_id = len(pedidos) + 1  # ID começa a partir de 1 e é sequencial
        data["id_autorizacao"] = pedido_id  # Adiciona o ID ao pedido
        
        pedidos.append(data)  # Armazena o pedido na lista em memória

        return jsonify({
            "message": "Pedido de autorização criado com sucesso!",
            "id_autorizacao": pedido_id  # Retorna o ID correto
        }), 201

    elif request.method == 'GET':
        return jsonify({"pedidos": pedidos}), 200  # Retorna todos os pedidos cadastrados


@pedidos_bp.route('/formulario-pedido', methods=['GET'])
def exibir_formulario():
    """ Rota que exibe o formulário para preencher o pedido de autorização """
    return render_template('formulario.html')