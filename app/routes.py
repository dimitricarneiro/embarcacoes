# 🔹 Importações do Flask
from flask import Blueprint, request, jsonify, render_template, Response, send_file, redirect, url_for
from app import limiter

# 🔹 Flask-Login (Autenticação)
from flask_login import login_required, current_user

# 🔹 Banco de Dados e Modelos
from app import db
from app.models import PedidoAutorizacao, Usuario, Notificacao, Embarcacao, Veiculo, Pessoa, Equipamento

# 🔹 Utilitários
from datetime import datetime
import csv
import re
import logging

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
from app.utils import validar_cnpj
from app.models import Alerta

# 🔹 Bibliotecas para Gerar Planilhas Excel
from openpyxl import Workbook
from openpyxl.styles import Font

#Funções auxiliares
def filtrar_pedidos():
    """
    Aplica os filtros enviados via query string e retorna a lista de pedidos filtrados.
    """
    query = PedidoAutorizacao.query

    # Filtro: Nome da Empresa (busca parcial, sem case sensitive)
    nome_empresa = request.args.get('nome_empresa')
    if nome_empresa:
        query = query.filter(PedidoAutorizacao.empresa_responsavel.ilike(f"%{nome_empresa}%"))

    # Filtro: CNPJ (busca exata)
    cnpj_empresa = request.args.get('cnpj_empresa')
    if cnpj_empresa:
        query = query.filter(PedidoAutorizacao.cnpj_empresa == cnpj_empresa)

    # Filtro: Status
    status = request.args.get('status')
    if status:
        query = query.filter(PedidoAutorizacao.status == status)

    # Filtro: Data Início
    data_inicio = request.args.get('data_inicio')
    if data_inicio:
        try:
            data_inicio_date = datetime.strptime(data_inicio, '%Y-%m-%d').date()
            query = query.filter(PedidoAutorizacao.data_inicio >= data_inicio_date)
        except ValueError:
            pass  # Se o formato da data for inválido, ignora o filtro

    # Filtro: Data Término
    data_termino = request.args.get('data_termino')
    if data_termino:
        try:
            data_termino_date = datetime.strptime(data_termino, '%Y-%m-%d').date()
            query = query.filter(PedidoAutorizacao.data_termino <= data_termino_date)
        except ValueError:
            pass

    return query.all()


######### Início de definição das rotas ##########################################################################
def verificar_alertas(novo_pedido):
    """
    Verifica se o novo pedido atende a algum alerta cadastrado e, se sim, cria notificações para os respectivos usuários RFB.
    """
    alertas = Alerta.query.filter_by(ativo=True).all()
    for alerta in alertas:
        # Se o alerta for do tipo "embarcacao", verificamos cada embarcação do pedido
        if alerta.tipo == "embarcacao":
            for embarcacao in novo_pedido.embarcacoes:
                if alerta.valor.lower() in embarcacao.nome.lower():
                    mensagem = (f"Novo pedido {novo_pedido.id} contém embarcação com nome "
                                f"correspondente ao seu alerta ('{alerta.valor}').")
                    criar_notificacao(alerta.usuario_id, mensagem)
                    break  # Evita notificar o mesmo alerta mais de uma vez para o mesmo pedido

        # Se o alerta for do tipo "cnpj", comparamos com o CNPJ da empresa do pedido
        elif alerta.tipo == "cnpj":
            if novo_pedido.cnpj_empresa == alerta.valor:
                mensagem = (f"Novo pedido {novo_pedido.id} criado por CNPJ "
                            f"'{novo_pedido.cnpj_empresa}' corresponde ao seu alerta.")
                criar_notificacao(alerta.usuario_id, mensagem)

def criar_notificacao(usuario_id, mensagem):
    """ Cria uma notificação para um usuário específico """
    nova_notificacao = Notificacao(usuario_id=usuario_id, mensagem=mensagem)
    db.session.add(nova_notificacao)
    db.session.commit()


pedidos_bp = Blueprint('pedidos', __name__)

@pedidos_bp.route('/')
def home():
    """Redireciona usuários não logados para a página de login"""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))  # 🔹 Redireciona para login
    return redirect(url_for('pedidos.exibir_pedidos'))  # 🔹 Se logado, vai para /lista-pedidos

@pedidos_bp.route('/api/pedidos-autorizacao', methods=['POST', 'GET'])
@login_required
def gerenciar_pedidos():
    """
    POST: Cria um novo pedido de autorização de serviço.
    GET: Retorna todos os pedidos cadastrados com suporte a filtros, paginação e ordenação.
    """
    if request.method == 'POST':
        try:
            # Obter dados em formato JSON
            data = request.get_json()
            if not data:
                return jsonify({"error": "Dados JSON não enviados ou inválidos."}), 400

            # Validação do CNPJ
            cnpj = data.get("cnpj_empresa", "")
            if not validar_cnpj(cnpj):
                return jsonify({"error": "CNPJ inválido!"}), 400

            # Verificação de campos obrigatórios
            required_fields = [
                "nome_empresa", "cnpj_empresa", "endereco_empresa", "motivo_solicitacao",
                "data_inicio", "data_termino", "horario_inicio_servicos", "horario_termino_servicos",
                "num_certificado_livre_pratica", "embarcacoes", "equipamentos", "pessoas"
            ]
            campos_invalidos = [field for field in required_fields if not data.get(field)]
            if campos_invalidos:
                return jsonify({
                    "error": f"Campos obrigatórios faltantes ou vazios: {', '.join(campos_invalidos)}"
                }), 400

            # Conversão das datas para objetos datetime.date
            try:
                data_inicio = datetime.strptime(data["data_inicio"], "%Y-%m-%d").date()
                data_termino = datetime.strptime(data["data_termino"], "%Y-%m-%d").date()
            except ValueError:
                return jsonify({"error": "Formato de data inválido. Use 'YYYY-MM-DD'."}), 400

            # Obter a data de hoje e validar as datas
            hoje = datetime.today().date()
            if data_inicio < hoje:
                return jsonify({"error": "A data de início deve ser hoje ou uma data futura."}), 400
            if data_termino < data_inicio:
                return jsonify({"error": "A data de término deve ser maior ou igual à data de início."}), 400

            # Criação do novo pedido de autorização (ainda sem associar os relacionamentos)
            novo_pedido = PedidoAutorizacao(
                empresa_responsavel=data["nome_empresa"],
                cnpj_empresa=data["cnpj_empresa"],
                endereco_empresa=data["endereco_empresa"],
                motivo_solicitacao=data["motivo_solicitacao"],
                data_inicio=data_inicio,
                data_termino=data_termino,
                horario_inicio_servicos=data["horario_inicio_servicos"],
                horario_termino_servicos=data["horario_termino_servicos"],
                usuario_id=current_user.id
            )

            # -------------------------------
            # Processamento de Embarcações
            # -------------------------------
            # Assume que data["embarcacoes"] é uma lista de nomes de embarcações.
            for nome_embarcacao in data["embarcacoes"]:
                nome_embarcacao = nome_embarcacao.strip()
                if nome_embarcacao:  # Ignora strings vazias
                    embarcacao = db.session.query(Embarcacao).filter_by(nome=nome_embarcacao).first()
                    if not embarcacao:
                        embarcacao = Embarcacao(nome=nome_embarcacao)
                        db.session.add(embarcacao)
                    novo_pedido.embarcacoes.append(embarcacao)

            # -------------------------------
            # Processamento de Equipamentos
            # -------------------------------
            # Agora espera-se que data["equipamentos"] seja uma lista de dicionários
            # com as chaves: "descricao", "numero_serie" e "quantidade"
            if "equipamentos" in data and data["equipamentos"]:
                for equipamento_data in data["equipamentos"]:
                    descricao = equipamento_data.get("descricao", "").strip()
                    numero_serie = equipamento_data.get("numero_serie", "").strip()
                    quantidade = equipamento_data.get("quantidade", 0)
                    if descricao and numero_serie and quantidade:
                        # Buscamos pelo número de série para identificar o equipamento
                        equipamento = db.session.query(Equipamento).filter_by(numero_serie=numero_serie).first()
                        if not equipamento:
                            # Cria novo equipamento (certifique-se de que o modelo Equipamento foi atualizado para ter o campo "numero_serie")
                            equipamento = Equipamento(descricao=descricao, numero_serie=numero_serie)
                            db.session.add(equipamento)
                        # Adiciona o equipamento ao pedido conforme a quantidade informada
                        for i in range(int(quantidade)):
                            novo_pedido.equipamentos.append(equipamento)
                    else:
                        # Se algum dos campos obrigatórios do equipamento estiver faltando, podemos optar por ignorar este item
                        continue

            # -------------------------------
            # Processamento de Pessoas
            # -------------------------------
            # Espera-se que data["pessoas"] seja uma lista de dicionários com "nome" e "cpf"
            for pessoa_data in data["pessoas"]:
                nome_pessoa = pessoa_data.get("nome", "").strip()
                cpf_pessoa = pessoa_data.get("cpf", "").strip()
                if nome_pessoa and cpf_pessoa:
                    pessoa = db.session.query(Pessoa).filter_by(cpf=cpf_pessoa).first()
                    if not pessoa:
                        pessoa = Pessoa(nome=nome_pessoa, cpf=cpf_pessoa)
                        db.session.add(pessoa)
                    novo_pedido.pessoas.append(pessoa)

            # -------------------------------
            # Processamento de Veículos
            # -------------------------------
            # Espera-se que data["veiculos"] seja uma lista de dicionários com "modelo" e "placa"
            if "veiculos" in data and data["veiculos"]:
                for veiculo_data in data["veiculos"]:
                    modelo_veiculo = veiculo_data.get("modelo", "").strip()
                    placa_veiculo = veiculo_data.get("placa", "").strip()
                    if modelo_veiculo and placa_veiculo:
                        veiculo = db.session.query(Veiculo).filter_by(placa=placa_veiculo).first()
                        if not veiculo:
                            veiculo = Veiculo(modelo=modelo_veiculo, placa=placa_veiculo)
                            db.session.add(veiculo)
                        novo_pedido.veiculos.append(veiculo)

            # Adiciona o pedido à sessão e comita as alterações
            db.session.add(novo_pedido)
            db.session.commit()

            # Verificar se o pedido atende a algum alerta
            verificar_alertas(novo_pedido)

            # Notificar os administradores sobre o novo pedido cadastrado
            administradores = Usuario.query.filter_by(role="RFB").all()
            mensagem = f"Novo pedido {novo_pedido.id} foi cadastrado e aguarda aprovação."
            for admin in administradores:
                criar_notificacao(admin.id, mensagem)

            return jsonify({
                "message": "Pedido de autorização criado com sucesso!",
                "id_autorizacao": novo_pedido.id
            }), 201

        except Exception as e:
            logging.exception("Erro ao criar pedido de autorização:")
            return jsonify({"error": "Ocorreu um erro interno no servidor."}), 500

    elif request.method == 'GET':
        try:
            # (Código GET permanece inalterado)
            # ...
            # Ordenação e paginação
            query = query.order_by(PedidoAutorizacao.data_inicio.desc())
            pedidos_paginados = query.paginate(page=page, per_page=per_page, error_out=False)

            # Montagem da resposta com os dados dos pedidos
            pedidos_lista = []
            for pedido in pedidos_paginados.items:
                pedido_dict = {
                    "id_autorizacao": pedido.id,
                    "nome_empresa": pedido.empresa_responsavel,
                    "cnpj_empresa": pedido.cnpj_empresa,
                    "endereco_empresa": pedido.endereco_empresa,
                    "motivo_solicitacao": pedido.motivo_solicitacao,
                    "data_inicio_servico": pedido.data_inicio.strftime("%Y-%m-%d"),
                    "data_termino_servico": pedido.data_termino.strftime("%Y-%m-%d"),
                    "horario_servicos": f"{pedido.horario_inicio_servicos} - {pedido.horario_termino_servicos}"
                }
                pedidos_lista.append(pedido_dict)

            return jsonify({
                "total_pedidos": pedidos_paginados.total,
                "pagina_atual": pedidos_paginados.page,
                "total_paginas": pedidos_paginados.pages,
                "pedidos": pedidos_lista
            }), 200

        except Exception as e:
            logging.exception("Erro ao recuperar pedidos de autorização:")
            return jsonify({"error": "Ocorreu um erro interno no servidor."}), 500

    elif request.method == 'GET':
        try:
            # Filtros opcionais enviados via query string
            nome_empresa = request.args.get("nome_empresa")
            data_inicio_str = request.args.get("data_inicio")  # Esperado no formato YYYY-MM-DD
            data_termino_str = request.args.get("data_termino")  # Esperado no formato YYYY-MM-DD

            # Paginação: página atual e itens por página
            page = request.args.get("page", default=1, type=int)
            per_page = request.args.get("per_page", default=10, type=int)

            # Inicia a query base
            query = PedidoAutorizacao.query

            # Aplicação do filtro por nome da empresa (case insensitive)
            if nome_empresa:
                query = query.filter(PedidoAutorizacao.empresa_responsavel.ilike(f"%{nome_empresa}%"))

            # Filtro para data de início
            if data_inicio_str:
                try:
                    data_inicio_filter = datetime.strptime(data_inicio_str, "%Y-%m-%d").date()
                    query = query.filter(PedidoAutorizacao.data_inicio >= data_inicio_filter)
                except ValueError:
                    return jsonify({"error": "Formato inválido para 'data_inicio'. Use 'YYYY-MM-DD'."}), 400

            # Filtro para data de término
            if data_termino_str:
                try:
                    data_termino_filter = datetime.strptime(data_termino_str, "%Y-%m-%d").date()
                    query = query.filter(PedidoAutorizacao.data_termino <= data_termino_filter)
                except ValueError:
                    return jsonify({"error": "Formato inválido para 'data_termino'. Use 'YYYY-MM-DD'."}), 400

            # Ordenação decrescente pela data de início
            query = query.order_by(PedidoAutorizacao.data_inicio.desc())

            # Aplicação da paginação
            pedidos_paginados = query.paginate(page=page, per_page=per_page, error_out=False)

            # Montagem da resposta com os dados dos pedidos
            pedidos_lista = []
            for pedido in pedidos_paginados.items:
                pedido_dict = {
                    "id_autorizacao": pedido.id,
                    "nome_empresa": pedido.empresa_responsavel,
                    "cnpj_empresa": pedido.cnpj_empresa,
                    "endereco_empresa": pedido.endereco_empresa,
                    "motivo_solicitacao": pedido.motivo_solicitacao,
                    "data_inicio": pedido.data_inicio.strftime("%Y-%m-%d"),
                    "data_termino": pedido.data_termino.strftime("%Y-%m-%d"),
                    "horario_servicos": pedido.horario_servico
                }
                pedidos_lista.append(pedido_dict)

            return jsonify({
                "total_pedidos": pedidos_paginados.total,
                "pagina_atual": pedidos_paginados.page,
                "total_paginas": pedidos_paginados.pages,
                "pedidos": pedidos_lista
            }), 200

        except Exception as e:
            logging.exception("Erro ao recuperar pedidos de autorização:")
            return jsonify({"error": "Ocorreu um erro interno no servidor."}), 500

@pedidos_bp.route('/lista-pedidos', methods=['GET'])
@login_required
def exibir_pedidos():
    """ Exibe os pedidos em uma página HTML com filtros, busca e paginação """

    # Captura os filtros opcionais da URL
    nome_empresa = request.args.get("nome_empresa", "").strip()
    cnpj_empresa = request.args.get("cnpj_empresa", "").strip()
    status = request.args.get("status", "").strip()
    data_inicio = request.args.get("data_inicio", "").strip()
    data_termino = request.args.get("data_termino", "").strip()
    # Novo filtro para o nome da embarcação:
    nome_embarcacao = request.args.get("nome_embarcacao", "").strip()

    # Configuração da paginação (mantendo a lógica original)
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)

    # Base da query: usuários comuns veem apenas seus pedidos, RFB vê todos
    if current_user.role == "RFB":
        query = PedidoAutorizacao.query
    else:
        query = PedidoAutorizacao.query.filter_by(usuario_id=current_user.id)

    # Aplicando filtros opcionais
    if nome_empresa:
        query = query.filter(PedidoAutorizacao.empresa_responsavel.ilike(f"%{nome_empresa}%"))

    if cnpj_empresa:
        query = query.filter(PedidoAutorizacao.cnpj_empresa.ilike(f"%{cnpj_empresa}%"))

    if status in ["pendente", "aprovado", "rejeitado"]:
        query = query.filter(PedidoAutorizacao.status == status)

    if data_inicio:
        try:
            data_inicio_dt = datetime.strptime(data_inicio, "%Y-%m-%d").date()
            query = query.filter(PedidoAutorizacao.data_inicio >= data_inicio_dt)
        except ValueError:
            return jsonify({"error": "Formato inválido para 'data_inicio'. Use 'YYYY-MM-DD'."}), 400

    if data_termino:
        try:
            data_termino_dt = datetime.strptime(data_termino, "%Y-%m-%d").date()
            query = query.filter(PedidoAutorizacao.data_termino <= data_termino_dt)
        except ValueError:
            return jsonify({"error": "Formato inválido para 'data_termino'. Use 'YYYY-MM-DD'."}), 400

    # Novo filtro: busca por nome da embarcação
    if nome_embarcacao:
        query = query.join(PedidoAutorizacao.embarcacoes).filter(Embarcacao.nome.ilike(f"%{nome_embarcacao}%"))

    # Ordenação e paginação
    query = query.order_by(PedidoAutorizacao.data_inicio.desc())
    pedidos_paginados = query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template('lista-pedidos.html', pedidos=pedidos_paginados)

@pedidos_bp.route('/pedido/<int:pedido_id>', methods=['GET'])
@login_required 
def exibir_detalhes_pedido(pedido_id):
    """ Exibe os detalhes de um pedido específico """
    pedido = PedidoAutorizacao.query.get_or_404(pedido_id)

    return render_template('detalhes-pedido.html', pedido=pedido)

@pedidos_bp.route('/api/pedidos-autorizacao/<int:pedido_id>/aprovar', methods=['PUT'])
@login_required
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

@pedidos_bp.route('/admin/alertas', methods=['GET', 'POST'])
@login_required
def gerenciar_alertas():
    """Exibe os alertas do usuário RFB e permite a criação de novos alertas."""
    if current_user.role != "RFB":
        return redirect(url_for('pedidos.exibir_pedidos'))
    
    if request.method == "POST":
        # Recebe os dados do formulário
        tipo = request.form.get("tipo")  # Esperado: "embarcacao" ou "cnpj"
        valor = request.form.get("valor")
        if tipo not in ["embarcacao", "cnpj"] or not valor:
            return jsonify({"error": "Dados inválidos para criar o alerta."}), 400

        novo_alerta = Alerta(usuario_id=current_user.id, tipo=tipo, valor=valor)
        db.session.add(novo_alerta)
        db.session.commit()
        return redirect(url_for("pedidos.gerenciar_alertas"))
    
    # Para método GET, exibe os alertas já criados pelo usuário
    alertas = Alerta.query.filter_by(usuario_id=current_user.id).all()
    return render_template("gerenciar_alertas.html", alertas=alertas)

@pedidos_bp.route('/admin/exportar-csv')
@login_required
def exportar_csv():
    """ Exporta os pedidos como um arquivo CSV """
    
    if current_user.role != "RFB":
        return redirect(url_for("pedidos.exibir_pedidos"))

    #pedidos = PedidoAutorizacao.query.all() #caso queira exportar todos os pedidos sem nenhum filtro
    
    # Utiliza os filtros para obter os pedidos
    pedidos = filtrar_pedidos()

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

    #pedidos = PedidoAutorizacao.query.all() #caso queira exportar todos os pedidos sem nenhum filtro
    
    # Utiliza os filtros para obter os pedidos
    pedidos = filtrar_pedidos()

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

@pedidos_bp.route('/admin/exportar-excel')
@login_required
def exportar_excel():
    """ 
    Exporta os pedidos cadastrados como um arquivo Excel (.xlsx).
    
    O arquivo conterá duas planilhas:
      1. 'Pedidos': Relação completa dos pedidos.
      2. 'Sumário': Estatísticas gerais dos pedidos.
    """
    # Apenas usuários com role "RFB" podem acessar esta rota.
    if current_user.role != "RFB":
        return redirect(url_for("pedidos.exibir_pedidos"))

    #pedidos = PedidoAutorizacao.query.all() #caso queira exportar todos os pedidos sem nenhum filtro
    
    # Utiliza os filtros para obter os pedidos
    pedidos = filtrar_pedidos()

    # Calcular estatísticas
    total_pedidos = len(pedidos)
    pedidos_aprovados = len([p for p in pedidos if p.status == "aprovado"])
    pedidos_rejeitados = len([p for p in pedidos if p.status == "rejeitado"])
    pedidos_pendentes = len([p for p in pedidos if p.status == "pendente"])

    # Criar um novo Workbook
    wb = Workbook()

    # --------------------------
    # Planilha de Pedidos
    # --------------------------
    ws_pedidos = wb.active
    ws_pedidos.title = "Pedidos"

    # Cabeçalho da tabela
    headers = ["ID", "Empresa", "CNPJ", "Motivo", "Data Início", "Data Término", "Status"]
    ws_pedidos.append(headers)

    # Estilizar o cabeçalho (fonte em negrito)
    for col in range(1, len(headers) + 1):
        ws_pedidos.cell(row=1, column=col).font = Font(bold=True)

    # Preencher os dados de cada pedido
    for pedido in pedidos:
        # Formatar datas como "dd/mm/aaaa"
        data_inicio = pedido.data_inicio.strftime("%d/%m/%Y") if pedido.data_inicio else ""
        data_termino = pedido.data_termino.strftime("%d/%m/%Y") if pedido.data_termino else ""
        ws_pedidos.append([
            pedido.id,
            pedido.empresa_responsavel,
            pedido.cnpj_empresa,
            pedido.motivo_solicitacao,
            data_inicio,
            data_termino,
            pedido.status
        ])

    # Ajustar a largura das colunas para melhor visualização
    for column_cells in ws_pedidos.columns:
        max_length = 0
        column = column_cells[0].column_letter  # Obter a letra da coluna
        for cell in column_cells:
            try:
                cell_length = len(str(cell.value))
                if cell_length > max_length:
                    max_length = cell_length
            except Exception:
                pass
        adjusted_width = max_length + 2
        ws_pedidos.column_dimensions[column].width = adjusted_width

    # --------------------------
    # Planilha do Sumário Estatístico
    # --------------------------
    ws_sumario = wb.create_sheet(title="Sumário")
    
    # Título do sumário
    ws_sumario["A1"] = "Sumário Estatístico"
    ws_sumario["A1"].font = Font(bold=True, size=14)
    
    # Preencher estatísticas
    ws_sumario["A3"] = "Total de Pedidos:"
    ws_sumario["B3"] = total_pedidos

    ws_sumario["A4"] = "Pedidos Aprovados:"
    ws_sumario["B4"] = pedidos_aprovados

    ws_sumario["A5"] = "Pedidos Rejeitados:"
    ws_sumario["B5"] = pedidos_rejeitados

    ws_sumario["A6"] = "Pedidos Pendentes:"
    ws_sumario["B6"] = pedidos_pendentes

    # Ajustar a largura das colunas do sumário
    ws_sumario.column_dimensions["A"].width = 25
    ws_sumario.column_dimensions["B"].width = 15

    # --------------------------
    # Salvar o Workbook em um objeto BytesIO
    # --------------------------
    output = BytesIO()
    wb.save(output)
    output.seek(0)

    # Retornar o arquivo para download
    return send_file(
        output,
        as_attachment=True,
        download_name="relatorio_pedidos.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

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
