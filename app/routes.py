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
    GET: Retorna todos os pedidos cadastrados com suporte a filtros e paginação
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
        """ 
        Retorna todos os pedidos cadastrados com suporte a filtros, paginação e ordenação.
        """

        # Filtros opcionais
        nome_empresa = request.args.get("nome_empresa")
        data_inicio = request.args.get("data_inicio")  # Formato YYYY-MM-DD
        data_termino = request.args.get("data_termino")  # Formato YYYY-MM-DD

        # Paginação (padrão: página 1, 10 itens por página)
        page = request.args.get("page", default=1, type=int)
        per_page = request.args.get("per_page", default=10, type=int)

        # Base da query
        query = PedidoAutorizacao.query

        # Aplicando filtros se fornecidos na URL
        if nome_empresa:
            query = query.filter(PedidoAutorizacao.empresa_responsavel.ilike(f"%{nome_empresa}%"))

        if data_inicio:
            try:
                data_inicio = datetime.strptime(data_inicio, "%Y-%m-%d").date()
                query = query.filter(PedidoAutorizacao.data_inicio >= data_inicio)
            except ValueError:
                return jsonify({"error": "Formato inválido para 'data_inicio'. Use 'YYYY-MM-DD'."}), 400

        if data_termino:
            try:
                data_termino = datetime.strptime(data_termino, "%Y-%m-%d").date()
                query = query.filter(PedidoAutorizacao.data_termino <= data_termino)
            except ValueError:
                return jsonify({"error": "Formato inválido para 'data_termino'. Use 'YYYY-MM-DD'."}), 400

        # Ordenação por data de início
        query = query.order_by(PedidoAutorizacao.data_inicio.desc())

        # Aplicando paginação
        pedidos_paginados = query.paginate(page=page, per_page=per_page, error_out=False)

        # Montando resposta
        pedidos_lista = [
            {
                "id_autorizacao": pedido.id,
                "nome_empresa": pedido.empresa_responsavel,
                "cnpj_empresa": pedido.cnpj_empresa,
                "endereco_empresa": pedido.endereco_empresa,
                "motivo_solicitacao": pedido.motivo_solicitacao,
                "data_inicio_servico": pedido.data_inicio.strftime("%Y-%m-%d"),
                "data_termino_servico": pedido.data_termino.strftime("%Y-%m-%d"),
                "horario_servicos": pedido.horario_servico
            } for pedido in pedidos_paginados.items
        ]

        return jsonify({
            "total_pedidos": pedidos_paginados.total,
            "pagina_atual": pedidos_paginados.page,
            "total_paginas": pedidos_paginados.pages,
            "pedidos": pedidos_lista
        }), 200

@pedidos_bp.route('/lista-pedidos', methods=['GET'])
def exibir_pedidos():
    """ Exibe os pedidos em uma página HTML com filtros, busca e paginação """

    # Captura os filtros opcionais da URL
    nome_empresa = request.args.get("nome_empresa", "").strip()
    cnpj_empresa = request.args.get("cnpj_empresa", "").strip()
    status = request.args.get("status", "").strip()
    data_inicio = request.args.get("data_inicio", "").strip()
    data_termino = request.args.get("data_termino", "").strip()

    # Configuração da paginação (mantendo a lógica original)
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)

    # Base da query (mantendo a ordenação original)
    query = PedidoAutorizacao.query.order_by(PedidoAutorizacao.data_inicio.desc())

    # Aplicando filtros se fornecidos
    if nome_empresa:
        query = query.filter(PedidoAutorizacao.empresa_responsavel.ilike(f"%{nome_empresa}%"))

    if cnpj_empresa:
        query = query.filter(PedidoAutorizacao.cnpj_empresa.ilike(f"%{cnpj_empresa}%"))

    if status in ["pendente", "aprovado", "rejeitado"]:
        query = query.filter(PedidoAutorizacao.status == status)

    if data_inicio:
        try:
            data_inicio = datetime.strptime(data_inicio, "%Y-%m-%d").date()
            query = query.filter(PedidoAutorizacao.data_inicio >= data_inicio)
        except ValueError:
            return jsonify({"error": "Formato inválido para 'data_inicio'. Use 'YYYY-MM-DD'."}), 400

    if data_termino:
        try:
            data_termino = datetime.strptime(data_termino, "%Y-%m-%d").date()
            query = query.filter(PedidoAutorizacao.data_termino <= data_termino)
        except ValueError:
            return jsonify({"error": "Formato inválido para 'data_termino'. Use 'YYYY-MM-DD'."}), 400

    # Mantendo a paginação original
    pedidos_paginados = query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template('lista-pedidos.html', pedidos=pedidos_paginados)

@pedidos_bp.route('/pedido/<int:pedido_id>', methods=['GET'])
def exibir_detalhes_pedido(pedido_id):
    """ Exibe os detalhes de um pedido específico """
    pedido = PedidoAutorizacao.query.get_or_404(pedido_id)

    return render_template('detalhes-pedido.html', pedido=pedido)

@pedidos_bp.route('/api/pedidos-autorizacao/<int:pedido_id>/aprovar', methods=['PUT'])
def aprovar_pedido(pedido_id):
    """ Aprova um pedido de autorização """

    # 🔹 Verifica se a requisição tem a chave de autorização
    auth_key = request.headers.get("Authorization")
    SECRET_KEY = "RFB_SECRET"  # 🔹 Defina uma chave secreta estática

    if auth_key != SECRET_KEY:
        return jsonify({"error": "Acesso não autorizado"}), 403

    # 🔹 Busca o pedido no banco
    pedido = PedidoAutorizacao.query.get_or_404(pedido_id)

    # 🔹 Verifica se já foi aprovado
    if pedido.status == "aprovado":
        return jsonify({"error": "Este pedido já foi aprovado"}), 400

    # 🔹 Aprova o pedido
    pedido.status = "aprovado"
    db.session.commit()

    return jsonify({"message": "Pedido aprovado com sucesso!", "id_autorizacao": pedido.id, "status": pedido.status}), 200

@pedidos_bp.route('/api/pedidos-autorizacao/<int:pedido_id>/rejeitar', methods=['PUT'])
def rejeitar_pedido(pedido_id):
    """ Rejeita um pedido de autorização """

    # 🔹 Verifica se a requisição tem a chave de autorização
    auth_key = request.headers.get("Authorization")
    SECRET_KEY = "RFB_SECRET"  # 🔹 Chave secreta provisória para autorização

    if auth_key != SECRET_KEY:
        return jsonify({"error": "Acesso não autorizado"}), 403

    # 🔹 Busca o pedido no banco
    pedido = PedidoAutorizacao.query.get_or_404(pedido_id)

    # 🔹 Verifica se já foi aprovado ou rejeitado
    if pedido.status != "pendente":
        return jsonify({"error": f"Este pedido já foi {pedido.status}."}), 400

    # 🔹 Rejeita o pedido
    pedido.status = "rejeitado"
    db.session.commit()

    return jsonify({"message": "Pedido rejeitado com sucesso!", "id_autorizacao": pedido.id, "status": pedido.status}), 200


@pedidos_bp.route('/formulario-pedido', methods=['GET'])
def exibir_formulario():
    """ Rota que exibe o formulário para preencher o pedido de autorização """
    return render_template('formulario.html')