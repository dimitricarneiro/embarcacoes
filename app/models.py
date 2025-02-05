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
    cnpj = db.Column(db.String(20), unique=True, nullable=True)         # Novo campo para o CNPJ
    nome_empresa = db.Column(db.String(255), nullable=True)  # Novo campo para o nome da empresa
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="comum")  # "comum" ou "RFB"

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
    data_termino = db.Column(db.Date, nullable=False)
    horario_inicio_servicos = db.Column(db.String(20), nullable=False)
    horario_termino_servicos = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default="pendente", nullable=False)
    
    # Relacionamento com o usuário que criou o pedido
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    usuario = db.relationship("Usuario", backref="pedidos")
    
    # Relacionamentos muitos-para-muitos
    embarcacoes = db.relationship("Embarcacao", secondary=pedido_embarcacao, backref="pedidos")
    veiculos = db.relationship("Veiculo", secondary=pedido_veiculo, backref="pedidos")
    pessoas = db.relationship("Pessoa", secondary=pedido_pessoa, backref="pedidos")
    equipamentos = db.relationship("Equipamento", secondary=pedido_equipamento, backref="pedidos")

# Modelo para Embarcações
class Embarcacao(db.Model):
    __tablename__ = 'embarcacoes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(255), nullable=False)
    # Outros campos relevantes da embarcação podem ser adicionados aqui.

# Modelo para Veículos
class Veiculo(db.Model):
    __tablename__ = 'veiculos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    modelo = db.Column(db.String(255), nullable=False)
    placa = db.Column(db.String(20), nullable=False)
    # Outros campos, se necessário

# Modelo para Pessoas
class Pessoa(db.Model):
    __tablename__ = 'pessoas'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(255), nullable=False)
    cpf = db.Column(db.String(14), nullable=False)
    # Outros campos, se necessário

# Modelo para Equipamentos (novo)
class Equipamento(db.Model):
    __tablename__ = 'equipamentos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descricao = db.Column(db.String(255), nullable=False)
    # Você pode adicionar outros campos relevantes para equipamentos, como número de série, modelo, etc.

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

