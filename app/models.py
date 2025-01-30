from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="comum")  # "comum" ou "RFB"

    def set_password(self, password):
        """Gera um hash seguro para a senha"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica se a senha informada está correta"""
        return check_password_hash(self.password_hash, password)

class PedidoAutorizacao(db.Model):
    __tablename__ = 'pedidos_autorizacao'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    empresa_responsavel = db.Column(db.String(255), nullable=False)
    cnpj_empresa = db.Column(db.String(20), nullable=False)
    endereco_empresa = db.Column(db.String(255), nullable=False)
    motivo_solicitacao = db.Column(db.Text, nullable=False)
    data_inicio = db.Column(db.Date, nullable=False)
    data_termino = db.Column(db.Date, nullable=False)
    horario_servico = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default="pendente", nullable=False)  # 🔹 Novo campo de status

    def __repr__(self):
        return f"<PedidoAutorizacao {self.id} - {self.empresa_responsavel} - {self.status}>"
