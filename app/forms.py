from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, TextAreaField, SelectField,
    DateField, BooleanField, IntegerField, SubmitField,
    FieldList, FormField
)
from wtforms.validators import DataRequired, Optional

# Sub-formulários para campos compostos no pedido
class EmbarcacaoForm(FlaskForm):
    nome = StringField("Nome da Embarcação", validators=[DataRequired()])
    imo = StringField("IMO", validators=[Optional()])
    bandeira = StringField("Bandeira", validators=[Optional()])

class VeiculoForm(FlaskForm):
    modelo = StringField("Modelo do Veículo", validators=[DataRequired()])
    placa = StringField("Placa do Veículo", validators=[DataRequired()])

class EquipamentoForm(FlaskForm):
    descricao = StringField("Descrição do Equipamento", validators=[DataRequired()])
    numero_serie = StringField("Número de Série", validators=[DataRequired()])
    quantidade = IntegerField("Quantidade", validators=[DataRequired()])

class PessoaForm(FlaskForm):
    nome = StringField("Nome da Pessoa", validators=[DataRequired()])
    cpf = StringField("CPF", validators=[DataRequired()])
    isps = StringField("ISPS", validators=[Optional()])

# Formulário para criação de novo usuário
class UserRegistrationForm(FlaskForm):
    username = StringField("Usuário", validators=[DataRequired()])
    password = PasswordField("Senha", validators=[DataRequired()])
    nome_empresa = StringField("Nome da Empresa", validators=[Optional()])
    cnpj = StringField("CNPJ", validators=[Optional()])
    role = SelectField("Role", choices=[("comum", "Comum"), ("RFB", "RFB")], validators=[DataRequired()])
    submit = SubmitField("Criar Usuário")

# Formulário para editar usuário
class UserEditForm(FlaskForm):
    username = StringField("Usuário", validators=[DataRequired()])
    password = PasswordField("Nova Senha (deixe em branco para manter a atual)", validators=[Optional()])
    nome_empresa = StringField("Nome da Empresa", validators=[Optional()])
    cnpj = StringField("CNPJ", validators=[Optional()])
    role = SelectField("Role", choices=[("comum", "Comum"), ("RFB", "RFB")], validators=[DataRequired()])
    submit = SubmitField("Salvar Alterações")

# Formulário para criação de novo pedido
class PedidoForm(FlaskForm):
    nome_empresa = StringField("Nome da Empresa", validators=[DataRequired()])
    cnpj_empresa = StringField("CNPJ", validators=[DataRequired()])
    endereco_empresa = StringField("Endereço", validators=[DataRequired()])
    motivo_solicitacao = StringField("Motivo", validators=[DataRequired()])
    data_inicio = DateField("Data Início", validators=[DataRequired()], format='%Y-%m-%d')
    data_termino = DateField("Data Término", validators=[DataRequired()], format='%Y-%m-%d')
    horario_inicio_servicos = StringField("Horário de Início", validators=[DataRequired()])
    horario_termino_servicos = StringField("Horário de Término", validators=[DataRequired()])
    certificado_livre_pratica = StringField("Certificado de Livre Prática", validators=[DataRequired()])
    cidade_servico = StringField("Cidade de Serviço", validators=[DataRequired()])
    observacoes = TextAreaField("Observações", validators=[Optional()])

    # Coleções dinâmicas usando FieldList e FormField
    embarcacoes = FieldList(FormField(EmbarcacaoForm), min_entries=1)
    veiculos = FieldList(FormField(VeiculoForm), min_entries=1)
    equipamentos = FieldList(FormField(EquipamentoForm), min_entries=1)
    pessoas = FieldList(FormField(PessoaForm), min_entries=1)

    submit = SubmitField("Enviar Pedido de Autorização")

# Formulário de login
class LoginForm(FlaskForm):
    username = StringField("Usuário", validators=[DataRequired()])
    password = PasswordField("Senha", validators=[DataRequired()])
    remember = BooleanField("Lembrar-me")
    submit = SubmitField("Entrar")

# Formulário para criação de alertas
class AlertaForm(FlaskForm):
    tipo = SelectField("Tipo", choices=[("embarcacao", "Embarcação"), ("cnpj", "CNPJ")], validators=[DataRequired()])
    valor = StringField("Valor", validators=[DataRequired()])
    submit = SubmitField("Criar Alerta")

# Formulário para busca de pedidos
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
