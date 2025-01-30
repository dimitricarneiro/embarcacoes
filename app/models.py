from app import db

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

    def __repr__(self):
        return f"<PedidoAutorizacao {self.id} - {self.empresa_responsavel}>"
