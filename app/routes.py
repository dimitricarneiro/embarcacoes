from flask import Blueprint, request, jsonify, render_template
from datetime import datetime
from app import db
from app.models import PedidoAutorizacao

pedidos_bp = Blueprint('pedidos', __name__)

@pedidos_bp.route('/')
def home():
    """Página inicial"""
    return "<h1>Bem-vindo ao sistema de pedidos de autorização</h1>", 200


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

        try:
            # ✅ Convertendo strings para objetos `date`
            data_inicio = datetime.strptime(data["data_inicio_servico"], "%Y-%m-%d").date()
            data_termino = datetime.strptime(data["data_termino_servico"], "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Formato de data inválido. Use 'YYYY-MM-DD'"}), 400

        # Criar um novo pedido e salvar no banco de dados SQLite
        novo_pedido = PedidoAutorizacao(
            empresa_responsavel=data["nome_empresa"],
            cnpj_empresa=data["cnpj_empresa"],
            endereco_empresa=data["endereco_empresa"],
            motivo_solicitacao=data["motivo_solicitacao"],
            data_inicio=data_inicio,  # ✅ Agora como objeto `date`
            data_termino=data_termino,  # ✅ Agora como objeto `date`
            horario_servico=data["horario_servicos"]
        )

        db.session.add(novo_pedido)
        db.session.commit()

        return jsonify({
            "message": "Pedido de autorização criado com sucesso!",
            "id_autorizacao": novo_pedido.id  # Retorna o ID do banco
        }), 201

    elif request.method == 'GET':
        # Buscar todos os pedidos no banco de dados
        pedidos = PedidoAutorizacao.query.all()
        pedidos_lista = [
            {
                "id_autorizacao": pedido.id,
                "nome_empresa": pedido.empresa_responsavel,
                "cnpj_empresa": pedido.cnpj_empresa,
                "endereco_empresa": pedido.endereco_empresa,
                "motivo_solicitacao": pedido.motivo_solicitacao,
                "data_inicio_servico": pedido.data_inicio.strftime("%Y-%m-%d"),  # ✅ Convertendo para string antes de exibir
                "data_termino_servico": pedido.data_termino.strftime("%Y-%m-%d"),  # ✅ Convertendo para string antes de exibir
                "horario_servicos": pedido.horario_servico
            } for pedido in pedidos
        ]

        return jsonify({"pedidos": pedidos_lista}), 200


@pedidos_bp.route('/formulario-pedido', methods=['GET'])
def exibir_formulario():
    """ Rota que exibe o formulário para preencher o pedido de autorização """
    return render_template('formulario.html')
