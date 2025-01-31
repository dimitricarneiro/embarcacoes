# 🔹 Importações do Flask
from flask import Blueprint, request, jsonify, render_template, Response, send_file
from app import limiter

# 🔹 Flask-Login (Autenticação)
from flask_login import login_required, current_user

# 🔹 Banco de Dados e Modelos
from app import db
from app.models import PedidoAutorizacao, Usuario, Notificacao  # ✅ Agora inclui Notificacao

# 🔹 Utilitários
from datetime import datetime
import csv
import re

# 🔹 SQLAlchemy
from sqlalchemy.sql import func

# 🔹 Bibliotecas para Gerar Relatórios PDF
from io import BytesIO
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas


def validar_cnpj(cnpj):
    """ Valida se o CNPJ informado é válido """
    cnpj = re.sub(r'\D', '', cnpj)  # Remove caracteres não numéricos

    if len(cnpj) != 14 or cnpj in (c * 14 for c in "0123456789"):
        return False

    def calcular_digito(cnpj, pesos):
        soma = sum(int(cnpj[i]) * pesos[i] for i in range(len(pesos)))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto

    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos2 = [6] + pesos1

    if int(cnpj[12]) != calcular_digito(cnpj[:12], pesos1):
        return False
    if int(cnpj[13]) != calcular_digito(cnpj[:13], pesos2):
        return False

    return True

def criar_notificacao(usuario_id, mensagem):
    """ Cria uma notificação para um usuário específico """
    nova_notificacao = Notificacao(usuario_id=usuario_id, mensagem=mensagem)
    db.session.add(nova_notificacao)
    db.session.commit()


pedidos_bp = Blueprint('pedidos', __name__)

@pedidos_bp.route('/')
def home():
    """Página inicial"""
    return "<h1>Bem-vindo ao sistema de pedidos de autorização</h1>", 200

@pedidos_bp.route('/api/pedidos-autorizacao', methods=['POST', 'GET'])
@login_required  # 🔹 Agora apenas usuários logados podem acessar
def gerenciar_pedidos():
    """ 
    POST: Cria um novo pedido de autorização de serviço 
    GET: Retorna todos os pedidos cadastrados com suporte a filtros e paginação
    """

    if request.method == 'POST':
        data = request.get_json()
        
        # ✅ Validação do CNPJ antes de continuar
        cnpj = data.get("cnpj_empresa", "")
        if not validar_cnpj(cnpj):
            return jsonify({"error": "CNPJ inválido!"}), 400

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
        
        # ✅ Criar notificação para os administradores sobre o novo pedido
        administradores = Usuario.query.filter_by(role="RFB").all()
        for admin in administradores:
            criar_notificacao(admin.id, f"Novo pedido {novo_pedido.id} foi cadastrado e aguarda aprovação.")


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
@login_required  # 🔹 Agora apenas usuários logados podem acessar
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
@login_required  # 🔹 Agora apenas usuários logados podem acessar
def exibir_detalhes_pedido(pedido_id):
    """ Exibe os detalhes de um pedido específico """
    pedido = PedidoAutorizacao.query.get_or_404(pedido_id)

    return render_template('detalhes-pedido.html', pedido=pedido)

@pedidos_bp.route('/api/pedidos-autorizacao/<int:pedido_id>/aprovar', methods=['PUT'])
@login_required  # 🔹 Agora apenas usuários logados podem acessar
def aprovar_pedido(pedido_id):
    """ Aprova um pedido de autorização """

    # 🔹 Verifica se o usuário tem permissão
    if current_user.role != "RFB":
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
@login_required  # 🔹 Agora apenas usuários logados podem acessar
def rejeitar_pedido(pedido_id):
    """ Rejeita um pedido de autorização """

    # 🔹 Verifica se o usuário tem permissão para rejeitar
    if current_user.role != "RFB":
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
@login_required  # 🔹 Agora apenas usuários logados podem acessar
def exibir_formulario():
    """ Rota que exibe o formulário para preencher o pedido de autorização """
    return render_template('formulario.html')

from flask import render_template
from flask_login import login_required, current_user

@pedidos_bp.route('/admin')
@login_required
def admin_dashboard():
    """ Painel Administrativo - Somente para usuários RFB """

    # 🔹 Verifica se o usuário é RFB
    if current_user.role != "RFB":
        return redirect(url_for("pedidos.exibir_pedidos"))

    # 🔹 Estatísticas gerais
    total_pedidos = PedidoAutorizacao.query.count()
    pedidos_aprovados = PedidoAutorizacao.query.filter_by(status="aprovado").count()
    pedidos_rejeitados = PedidoAutorizacao.query.filter_by(status="rejeitado").count()
    pedidos_pendentes = PedidoAutorizacao.query.filter_by(status="pendente").count()
    total_usuarios = Usuario.query.count()

    # 🔹 Contagem de pedidos por dia
    pedidos_por_dia = (
        db.session.query(func.date(PedidoAutorizacao.data_inicio), func.count())
        .group_by(func.date(PedidoAutorizacao.data_inicio))
        .order_by(func.date(PedidoAutorizacao.data_inicio))
        .all()
    )

    # 🔹 Preparar dados para o gráfico
    datas = [str(p[0]) for p in pedidos_por_dia]
    pedidos_quantidade = [p[1] for p in pedidos_por_dia]

    return render_template("admin.html", 
                           total_pedidos=total_pedidos, 
                           pedidos_aprovados=pedidos_aprovados,
                           pedidos_rejeitados=pedidos_rejeitados, 
                           pedidos_pendentes=pedidos_pendentes,
                           total_usuarios=total_usuarios,
                           datas=datas, 
                           pedidos_quantidade=pedidos_quantidade)

@pedidos_bp.route('/admin/exportar-csv')
@login_required
def exportar_csv():
    """ Exporta os pedidos como um arquivo CSV """
    
    if current_user.role != "RFB":
        return redirect(url_for("pedidos.exibir_pedidos"))

    pedidos = PedidoAutorizacao.query.all()

    # Criar resposta CSV
    response = Response()
    response.headers["Content-Disposition"] = "attachment; filename=relatorio_pedidos.csv"
    response.headers["Content-Type"] = "text/csv"

    # Escrever dados no CSV
    writer = csv.writer(response)
    writer.writerow(["ID", "Empresa", "CNPJ", "Motivo", "Data Início", "Data Término", "Status"])
    
    for pedido in pedidos:
        writer.writerow([pedido.id, pedido.empresa_responsavel, pedido.cnpj_empresa, pedido.motivo_solicitacao,
                         pedido.data_inicio, pedido.data_termino, pedido.status])
    
    return response

@pedidos_bp.route('/admin/exportar-pdf')
@login_required
def exportar_pdf():
    """ Exporta os pedidos como um arquivo PDF formatado com sumário estatístico """
    
    if current_user.role != "RFB":
        return redirect(url_for("pedidos.exibir_pedidos"))

    pedidos = PedidoAutorizacao.query.all()

    # 🔹 Estatísticas gerais
    total_pedidos = len(pedidos)
    pedidos_aprovados = len([p for p in pedidos if p.status == "aprovado"])
    pedidos_rejeitados = len([p for p in pedidos if p.status == "rejeitado"])
    pedidos_pendentes = len([p for p in pedidos if p.status == "pendente"])

    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=landscape(letter))
    
    elementos = []

    # 🔹 Título do Relatório
    styles = getSampleStyleSheet()
    elementos.append(Paragraph("<b>Relatório de Pedidos</b>", styles['Title']))
    elementos.append(Spacer(1, 12))  # Adiciona um espaço

    # 🔹 Criar a tabela de pedidos
    dados = [["ID", "Empresa", "CNPJ", "Motivo", "Data Início", "Data Término", "Status"]]
    
    for pedido in pedidos:
        dados.append([
            pedido.id, 
            pedido.empresa_responsavel, 
            pedido.cnpj_empresa, 
            pedido.motivo_solicitacao, 
            pedido.data_inicio.strftime("%d/%m/%Y"), 
            pedido.data_termino.strftime("%d/%m/%Y"), 
            pedido.status
        ])

    tabela = Table(dados)
    
    # 🔹 Estilizar a tabela
    estilo = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    
    tabela.setStyle(estilo)
    elementos.append(tabela)
    elementos.append(Spacer(1, 20))  # Adiciona um espaço antes do sumário

    # 🔹 Criar o sumário estatístico
    elementos.append(Paragraph("<b>Sumário Estatístico</b>", styles['Heading2']))
    elementos.append(Paragraph(f"Total de Pedidos: {total_pedidos}", styles['Normal']))
    elementos.append(Paragraph(f"Pedidos Aprovados: {pedidos_aprovados}", styles['Normal']))
    elementos.append(Paragraph(f"Pedidos Rejeitados: {pedidos_rejeitados}", styles['Normal']))
    elementos.append(Paragraph(f"Pedidos Pendentes: {pedidos_pendentes}", styles['Normal']))

    # 🔹 Criar o PDF
    pdf.build(elementos)
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="relatorio_pedidos.pdf", mimetype="application/pdf")

@pedidos_bp.route("/api/notificacoes", methods=["GET"])
@limiter.limit("30 per minute")  # Permite 30 requisições por minuto só para essa rota
@login_required
def listar_notificacoes():
    """ Retorna notificações não lidas do usuário autenticado """
    notificacoes = Notificacao.query.filter_by(usuario_id=current_user.id, lida=False).all()

    return jsonify([
        {"id": n.id, "mensagem": n.mensagem, "data": n.data_criacao.strftime("%d/%m/%Y %H:%M"), "lida": n.lida}
        for n in notificacoes
    ])

@pedidos_bp.route('/api/notificacoes/<int:notificacao_id>/marcar-lida', methods=['PUT'])
@login_required
def marcar_notificacao_lida(notificacao_id):
    """ Marca uma notificação como lida """
    
    notificacao = Notificacao.query.filter_by(id=notificacao_id, usuario_id=current_user.id).first()

    if not notificacao:
        return jsonify({"error": "Notificação não encontrada"}), 404

    notificacao.lida = True
    db.session.commit()

    return jsonify({"message": "Notificação marcada como lida"}), 200
