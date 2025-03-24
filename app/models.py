from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Tabelas de associação para os relacionamentos muitos-para-muitos
pedido_embarcacao = db.Table('pedido_embarcacao',
    db.Column('pedido_id', db.Integer, db.ForeignKey('pedidos_autorizacao.id'), primary_key=True),
    db.Column('embarcacao_id', db.Integer, db.ForeignKey('embarcacoes.id'), primary_key=True)
)

pedido_veiculo = db.Table('pedido_veiculo',
    db.Column('pedido_id', db.Integer, db.ForeignKey('pedidos_autorizacao.id'), primary_key=True),
    db.Column('veiculo_id', db.Integer, db.ForeignKey('veiculos.id'), primary_key=True)
)

pedido_pessoa = db.Table('pedido_pessoa',
    db.Column('pedido_id', db.Integer, db.ForeignKey('pedidos_autorizacao.id'), primary_key=True),
    db.Column('pessoa_id', db.Integer, db.ForeignKey('pessoas.id'), primary_key=True)
)

# Tabela de associação para Equipamentos (novo)
pedido_equipamento = db.Table('pedido_equipamento',
    db.Column('pedido_id', db.Integer, db.ForeignKey('pedidos_autorizacao.id'), primary_key=True),
    db.Column('equipamento_id', db.Integer, db.ForeignKey('equipamentos.id'), primary_key=True)
)

# Modelo de Usuário
class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuario'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    cnpj = db.Column(db.String(14), unique=True, nullable=False)  # campo para o CNPJ
    nome_empresa = db.Column(db.String(255), nullable=True)  # campo para o nome da empresa
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="comum")  # "comum", "agencia_maritima" ou "RFB"
    data_criacao_usuario = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def set_password(self, password):
        """Gera um hash seguro para a senha"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica se a senha informada está correta"""
        return check_password_hash(self.password_hash, password)

# Modelo de Pedido de Autorização
class PedidoAutorizacao(db.Model):
    __tablename__ = 'pedidos_autorizacao'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    empresa_responsavel = db.Column(db.String(255), nullable=False)
    cnpj_empresa = db.Column(db.String(20), nullable=False)
    endereco_empresa = db.Column(db.String(255), nullable=False)
    motivo_solicitacao = db.Column(db.Text, nullable=False)
    data_inicio = db.Column(db.Date, nullable=False)
    data_termino = db.Column(db.Date, nullable=False)  # Data de término original ou atualizada
    horario_inicio_servicos = db.Column(db.String(20), nullable=False)
    horario_termino_servicos = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default="aguardando_agencia", nullable=False)
    certificado_livre_pratica = db.Column(db.String(8), nullable=True)
    cidade_servico = db.Column(db.String(50), nullable=True)
    observacoes = db.Column(db.Text, nullable=True)
    data_criacao_pedido = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    token_comprovante = db.Column(db.String(100), nullable=True)
    agencia_maritima = db.Column(db.String(255), nullable=True)
    cnpj_agencia = db.Column(db.String(20), nullable=True)
    termo_responsabilidade = db.Column(db.Boolean, nullable=False, default=False)
    data_analise_pedido = db.Column(db.DateTime, nullable=True)
    id_usuario_que_analisou_pedido = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=True)

    # Relacionamento para o usuário que analisou o pedido:
    usuario_que_analisou = db.relationship("Usuario", foreign_keys=[id_usuario_que_analisou_pedido])

    # Relacionamento com o usuário que criou o pedido:
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    usuario = db.relationship("Usuario", foreign_keys=[usuario_id], backref="pedidos")

    # Relacionamentos muitos-para-muitos
    embarcacoes = db.relationship("Embarcacao", secondary=pedido_embarcacao, backref="pedidos")
    veiculos = db.relationship("Veiculo", secondary=pedido_veiculo, backref="pedidos")
    pessoas = db.relationship("Pessoa", secondary=pedido_pessoa, backref="pedidos")
    equipamentos = db.relationship("Equipamento", secondary=pedido_equipamento, backref="pedidos")

class Prorrogacao(db.Model):
    __tablename__ = 'prorrogacoes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # Chave estrangeira para associar a prorrogação a um pedido
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos_autorizacao.id'), nullable=False)
    
    # Data de término registrada antes da prorrogação
    data_termino_antiga = db.Column(db.Date, nullable=False)
    # Nova data de término solicitada
    data_termino_nova = db.Column(db.Date, nullable=False)
    
    # Data e hora em que a solicitação foi realizada
    data_solicitacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Campo para indicar o status da prorrogação:
    # Possíveis valores: 'pendente', 'aprovada', 'rejeitada'
    status_prorrogacao = db.Column(db.String(20), nullable=False, default='pendente')
    
    # Novo campo: justificativa para a prorrogação
    justificativa = db.Column(db.Text, nullable=False)

    # Relacionamento com o modelo PedidoAutorizacao.
    # O backref 'prorrogacoes' permite acessar todas as prorrogações de um pedido: pedido.prorrogacoes
    pedido = db.relationship('PedidoAutorizacao', backref=db.backref('prorrogacoes', lazy=True))

    def __repr__(self):
        return (
            f"<Prorrogacao {self.id}: {self.data_termino_antiga} -> "
            f"{self.data_termino_nova}, status={self.status_prorrogacao}>"
        )

# Modelo para Embarcações
class Embarcacao(db.Model):
    __tablename__ = 'embarcacoes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(255), nullable=False)
    imo = db.Column(db.String(10), nullable=True)
    bandeira = db.Column(db.String(50), nullable=True)
    # Outros campos relevantes da embarcação podem ser adicionados aqui.

# Modelo para Pessoas
class Pessoa(db.Model):
    __tablename__ = 'pessoas'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(255), nullable=False)
    cpf = db.Column(db.String(14), nullable=False)
    isps = db.Column(db.String(8), nullable=True)
    # --- Novos campos adicionados ---
    funcao = db.Column(db.String(255), nullable=True)           # Função da pessoa
    local_embarque = db.Column(db.String(255), nullable=True)     # Local de embarque
    local_desembarque = db.Column(db.String(255), nullable=True)  # Local de desembarque

# Modelo para Veículos
class Veiculo(db.Model):
    __tablename__ = 'veiculos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    modelo = db.Column(db.String(255), nullable=False)
    placa = db.Column(db.String(20), nullable=False)
    # Outros campos, se necessário

# Modelo para Equipamentos
class Equipamento(db.Model):
    __tablename__ = 'equipamentos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descricao = db.Column(db.String(255), nullable=False)
    numero_serie = db.Column(db.String(100), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False, default=1)  # novo campo para quantidade

# Modelo para Notificações
class Notificacao(db.Model):
    __tablename__ = "notificacoes"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    mensagem = db.Column(db.String(255), nullable=False)
    lida = db.Column(db.Boolean, default=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    usuario = db.relationship("Usuario", backref=db.backref("notificacoes", lazy=True))

    def __repr__(self):
        return f"<Notificacao {self.id} - Usuário: {self.usuario_id} - {self.mensagem}>"

class Alerta(db.Model):
    __tablename__ = 'alertas'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # Ex: "embarcacao" ou "cnpj"
    valor = db.Column(db.String(255), nullable=False)  # Ex: "Titanic" ou "26.994.558/0001-23"
    ativo = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    usuario = db.relationship("Usuario", backref=db.backref("alertas", lazy=True))

    def __repr__(self):
        return f"<Alerta {self.id} - Tipo: {self.tipo} - Valor: {self.valor}>"

class Exigencia(db.Model):
    __tablename__ = 'exigencias'
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos_autorizacao.id'), nullable=False)
    motivo_exigencia = db.Column(db.Text, nullable=False)
    prazo_exigencia = db.Column(db.Date, nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)  # usuário que fez a exigência
    data_resposta = db.Column(db.DateTime, nullable=True)  # Armazena a data em que a resposta foi feita
    texto_resposta = db.Column(db.Text, nullable=True)       # Armazena o conteúdo da resposta

    # Associação com o usuário que fez a exigência
    usuario = db.relationship('Usuario', backref=db.backref('exigencias_criadas', lazy=True))

    # Associação com o pedido de autorização com ordenação pela data de criação (mais recente primeiro)
    pedido = db.relationship(
        'PedidoAutorizacao',
        backref=db.backref('exigencias', lazy=True, order_by="desc(Exigencia.data_criacao)")
    )
