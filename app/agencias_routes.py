from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from datetime import date
from app import db
from app.models import PedidoAutorizacao, Usuario

# Importa a função de notificação
from app.routes import criar_notificacao, verificar_alertas

# Formulários
from app.forms import PedidoSearchForm

# Segurança
from app.security import role_required


# Cria um Blueprint para as rotas da agência marítima
agencias_bp = Blueprint('agencias', __name__)

@agencias_bp.route('/agencia/pedidos', methods=['GET'])
@login_required
@role_required("agencia_maritima")
def agenciar_pedidos():
    """
    Exibe os pedidos destinados à agência marítima autenticada.
    """
    # Instancia o formulário de busca com os parâmetros da query string
    form = PedidoSearchForm(request.args)

    # Parâmetros de paginação
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)
    
    # Base da query: filtra os pedidos pelo cnpj_agencia
    query = PedidoAutorizacao.query.filter(
        PedidoAutorizacao.cnpj_agencia == current_user.cnpj
    )
    
    # Aplicando os filtros do formulário
    if form.nome_empresa.data:
        query = query.filter(PedidoAutorizacao.empresa_responsavel.ilike(f"%{form.nome_empresa.data}%"))
    
    if form.cnpj_empresa.data:
        query = query.filter(PedidoAutorizacao.cnpj_empresa.ilike(f"%{form.cnpj_empresa.data}%"))
    
    if form.status.data in ["pendente", "aprovado", "rejeitado", "aguardando_agencia", "rejeitado_agencia", "exigência"]:
        query = query.filter(PedidoAutorizacao.status == form.status.data)
    
    if form.data_inicio.data:
        query = query.filter(PedidoAutorizacao.data_inicio >= form.data_inicio.data)
    
    if form.data_termino.data:
        query = query.filter(PedidoAutorizacao.data_termino <= form.data_termino.data)
    
    if form.nome_embarcacao.data:
        # Filtra pelo nome da embarcação (ajustando para caixa baixa)
        query = query.join(PedidoAutorizacao.embarcacoes).filter(func.lower(Embarcacao.nome) == form.nome_embarcacao.data.lower())
    
    # Ordena e pagina
    query = query.order_by(PedidoAutorizacao.id.desc())
    pedidos_paginados = query.paginate(page=page, per_page=per_page, error_out=False)
    
    hoje = date.today()
    
    return render_template("agenciar.html", pedidos=pedidos_paginados, form=form, hoje=hoje)

@agencias_bp.route('/api/pedidos-autorizacao/<int:pedido_id>/agenciar', methods=['PUT'])
@login_required
@role_required("agencia_maritima")
def agenciar_pedido(pedido_id):
    """
    Rota para que uma agência marítima aceite (agencie) um pedido.
    
    Regras:
    - Apenas usuários com role "agencia_maritima" podem acessar.
    - O usuário logado deve ter o cnpj igual ao cnpj_agencia do pedido.
    - Se aprovado, atualiza o status do pedido para 'pendente'.
    """
    
    # Tenta ler o JSON da requisição, se houver, mas não o utiliza
    dados = request.get_json(silent=True) or {}
    
    # Se o payload tentar enviar o campo "status", rejeita a requisição
    if "status" in dados:
        return jsonify({"error": "Modificação do status não é permitida via payload."}), 400

    # Verifica se o usuário logado é do tipo agência marítima
    if current_user.role != "agencia_maritima":
        return jsonify({"error": "Acesso não autorizado."}), 403

    pedido = PedidoAutorizacao.query.get_or_404(pedido_id)

    # Verifica se o cnpj do usuário é igual ao cnpj_agencia do pedido
    if pedido.cnpj_agencia != current_user.cnpj:
        return jsonify({"error": "Você não tem permissão para agenciar este pedido."}), 403

    # Verifica se o pedido está no status esperado
    if pedido.status != "aguardando_agencia":
        return jsonify({"error": "Este pedido não está aguardando agenciamento."}), 400

    # Atualiza o status para 'pendente'
    pedido.status = "pendente"
    db.session.commit()

    # Agora, notifica os administradores (RFB)
    verificar_alertas(pedido)
    administradores = Usuario.query.filter_by(role="RFB").all()
    mensagem = f"O pedido {pedido.id} foi aceito pela agência {current_user.nome_empresa}."
    for admin in administradores:
        criar_notificacao(admin.id, mensagem)

    return jsonify({
        "message": "Pedido agenciado com sucesso!",
        "id_pedido": pedido.id,
        "status": pedido.status
    }), 200

@agencias_bp.route('/api/pedidos-autorizacao/<int:pedido_id>/rejeitar-agencia', methods=['PUT'])
@login_required
@role_required("agencia_maritima")
def rejeitar_pedido_agencia(pedido_id):
    """
    Rota para que uma agência marítima rejeite um pedido.
    
    Regras:
    - Apenas usuários com role "agencia_maritima" podem acessar.
    - O usuário logado deve ter o cnpj igual ao cnpj_agencia do pedido.
    - Se rejeitado, atualiza o status do pedido para 'rejeitado_agencia'.
    """
    
    # Tenta ler o JSON da requisição, se houver, mas não o utiliza
    dados = request.get_json(silent=True) or {}
    
    # Se o payload tentar enviar o campo "status", rejeita a requisição
    if "status" in dados:
        return jsonify({"error": "Modificação do status não é permitida via payload."}), 400

    # Verifica se o usuário logado é do tipo agência marítima    
    if current_user.role != "agencia_maritima":
        return jsonify({"error": "Acesso não autorizado."}), 403

    pedido = PedidoAutorizacao.query.get_or_404(pedido_id)

    # Verifica se o cnpj do usuário é igual ao cnpj_agencia do pedido
    if pedido.cnpj_agencia != current_user.cnpj:
        return jsonify({"error": "Você não tem permissão para rejeitar este pedido."}), 403

    # Verifica se o pedido está no status esperado
    if pedido.status != "aguardando_agencia":
        return jsonify({"error": "Este pedido não está aguardando agenciamento."}), 400

    # Atualiza o status para 'rejeitado_agencia'
    pedido.status = "rejeitado_agencia"
    db.session.commit()

    return jsonify({
        "message": "Pedido rejeitado com sucesso!",
        "id_pedido": pedido.id,
        "status": pedido.status
    }), 200
