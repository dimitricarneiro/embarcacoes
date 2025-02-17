from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, TextAreaField, SelectField,
    DateField, BooleanField, IntegerField, SubmitField,
    FieldList, FormField
)
from wtforms.validators import DataRequired, Optional

# Base para formulários de API: CSRF desabilitado
class ApiForm(FlaskForm):
    class Meta:
        csrf = False

# Sub-formulários (para campos dinâmicos) usados no pedido – sem CSRF, pois são para API
class EmbarcacaoForm(ApiForm):
    # Os nomes dos campos abaixo correspondem às keys enviadas pelo JSON
    nome = StringField("nome", validators=[DataRequired()])
    imo = StringField("imo", validators=[Optional()])
    bandeira = StringField("bandeira", validators=[Optional()])

class VeiculoForm(ApiForm):
    modelo = StringField("modelo", validators=[DataRequired()])
    placa = StringField("placa", validators=[DataRequired()])

class EquipamentoForm(ApiForm):
    descricao = StringField("descricao", validators=[DataRequired()])
    numero_serie = StringField("numero_serie", validators=[DataRequired()])
    quantidade = IntegerField("quantidade", validators=[DataRequired()])

class PessoaForm(ApiForm):
    nome = StringField("nome", validators=[DataRequired()])
    cpf = StringField("cpf", validators=[DataRequired()])
    isps = StringField("isps", validators=[Optional()])

# Formulário para criação de novo pedido – usado em endpoint de API, sem CSRF
class PedidoForm(ApiForm):
    nome_empresa = StringField("nome_empresa", validators=[DataRequired()])
    cnpj_empresa = StringField("cnpj_empresa", validators=[DataRequired()])
    endereco_empresa = StringField("endereco_empresa", validators=[DataRequired()])
    motivo_solicitacao = StringField("motivo_solicitacao", validators=[DataRequired()])
    data_inicio = DateField("data_inicio", validators=[DataRequired()], format='%Y-%m-%d')
    data_termino = DateField("data_termino", validators=[DataRequired()], format='%Y-%m-%d')
    horario_inicio_servicos = StringField("horario_inicio_servicos", validators=[DataRequired()])
    horario_termino_servicos = StringField("horario_termino_servicos", validators=[DataRequired()])
    certificado_livre_pratica = StringField("certificado_livre_pratica", validators=[DataRequired()])
    cidade_servico = StringField("cidade_servico", validators=[DataRequired()])
    observacoes = TextAreaField("observacoes", validators=[Optional()])

    # Alterado para min_entries=0 para evitar a criação automática de um item vazio.
    embarcacoes = FieldList(FormField(EmbarcacaoForm), min_entries=0)
    veiculos = FieldList(FormField(VeiculoForm), min_entries=0)
    equipamentos = FieldList(FormField(EquipamentoForm), min_entries=0)
    pessoas = FieldList(FormField(PessoaForm), min_entries=0)

    submit = SubmitField("Enviar Pedido de Autorização")

# Os demais formulários, usados em templates renderizados, mantêm a proteção CSRF

# Formulário para criação de novo usuário (com CSRF)
class UserRegistrationForm(FlaskForm):
    username = StringField("Usuário", validators=[DataRequired()])
    password = PasswordField("Senha", validators=[DataRequired()])
    nome_empresa = StringField("Nome da Empresa", validators=[Optional()])
    cnpj = StringField("CNPJ", validators=[Optional()])
    role = SelectField("Role", choices=[("comum", "Comum"), ("RFB", "RFB")], validators=[DataRequired()])
    submit = SubmitField("Criar Usuário")

# Formulário para editar usuário (com CSRF)
class UserEditForm(FlaskForm):
    username = StringField("Usuário", validators=[DataRequired()])
    password = PasswordField("Nova Senha (deixe em branco para manter a atual)", validators=[Optional()])
    nome_empresa = StringField("Nome da Empresa", validators=[Optional()])
    cnpj = StringField("CNPJ", validators=[Optional()])
    role = SelectField("Role", choices=[("comum", "Comum"), ("RFB", "RFB")], validators=[DataRequired()])
    submit = SubmitField("Salvar Alterações")

# Formulário de login (com CSRF)
class LoginForm(FlaskForm):
    username = StringField("Usuário", validators=[DataRequired()])
    password = PasswordField("Senha", validators=[DataRequired()])
    remember = BooleanField("Lembrar-me")
    submit = SubmitField("Entrar")

# Formulário para criação de alertas (com CSRF)
class AlertaForm(FlaskForm):
    tipo = SelectField("Tipo", choices=[("embarcacao", "Embarcação"), ("cnpj", "CNPJ")], validators=[DataRequired()])
    valor = StringField("Valor", validators=[DataRequired()])
    submit = SubmitField("Criar Alerta")

# Formulário para busca de pedidos (com CSRF)
class PedidoSearchForm(FlaskForm):
    nome_empresa = StringField("Nome da Empresa", validators=[Optional()])
    cnpj_empresa = StringField("CNPJ", validators=[Optional()])
    nome_embarcacao = StringField("Nome da Embarcação", validators=[Optional()])
    status = SelectField("Status", choices=[
        ("", "Todos os Status"),
        ("pendente", "Pendente"),
        ("aprovado", "Aprovado"),
        ("rejeitado", "Rejeitado"),
        ("exigência", "Com exigência")
    ], validators=[Optional()])
    data_inicio = DateField("Data Início", validators=[Optional()], format='%Y-%m-%d')
    data_termino = DateField("Data Término", validators=[Optional()], format='%Y-%m-%d')
    submit = SubmitField("Filtrar")
