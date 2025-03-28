from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Usuario
from app.forms import UserRegistrationForm, UserEditForm
from werkzeug.security import generate_password_hash
from app.utils import validar_cnpj, normalizar_cnpj

# Segurança
from app.security import role_required

users_bp = Blueprint('users', __name__, url_prefix='/users')

def admin_required():
    """Função auxiliar para permitir acesso apenas a administradores (role 'RFB')."""
    if current_user.role != "RFB":
        flash("Acesso não autorizado.", "error")
        return False
    return True

@users_bp.route('/', methods=['GET'])
@login_required
@role_required("RFB")
def list_users():
    """Lista todos os usuários (acessível apenas para administradores)."""

    if not admin_required(): # Verifica se é um usuário RFB antes de listar os usuários existentes
        return redirect(url_for('pedidos.exibir_pedidos'))
    usuarios = Usuario.query.all()
    return render_template('users/list.html', usuarios=usuarios)

@users_bp.route('/create', methods=['GET', 'POST'])
@login_required
@role_required("RFB")
def create_user():
    if not admin_required():  # Verifica se o usuário é RFB 
        return redirect(url_for('pedidos.exibir_pedidos'))

    form = UserRegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        nome_empresa = form.nome_empresa.data
        cnpj = form.cnpj.data
        role = form.role.data

        # Valida se o username já existe
        if Usuario.query.filter_by(username=username).first():
            flash("Usuário já existe.", "error")
            return redirect(url_for('users.create_user'))

        # Normaliza o CNPJ para manter apenas letras e dígitos
        cnpj_normalizado = normalizar_cnpj(cnpj)

        # Verifica se já existe um usuário com o mesmo CNPJ normalizado
        if Usuario.query.filter_by(cnpj=cnpj_normalizado).first():
            flash("Já existe um usuário com este CNPJ.", "error")
            return redirect(url_for('users.create_user'))

        # Valida se o CNPJ normalizado é válido
        if not validar_cnpj(cnpj_normalizado):
            flash("CNPJ inválido. Por favor, verifique o valor informado.", "error")
            return redirect(url_for('users.create_user'))

        # Cria o novo usuário com o CNPJ normalizado
        novo_usuario = Usuario(
            username=username,
            nome_empresa=nome_empresa,
            cnpj=cnpj_normalizado,
            role=role
        )
        novo_usuario.set_password(password)
        db.session.add(novo_usuario)
        db.session.commit()
        flash("Usuário criado com sucesso.", "success")
        return redirect(url_for('users.list_users'))

    return render_template('users/create.html', form=form)

@users_bp.route('/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@role_required("RFB")
def edit_user(user_id):
    """Edita os dados de um usuário existente (acessível apenas para administradores)."""
    if not admin_required():  # Verifica se é um usuário RFB
        return redirect(url_for('pedidos.exibir_pedidos'))
    
    usuario = Usuario.query.get_or_404(user_id)
    form = UserEditForm(obj=usuario)
    
    if form.validate_on_submit():
        new_username = form.username.data
        new_cnpj = form.cnpj.data
        
        # Normaliza o novo CNPJ, mantendo apenas letras e dígitos
        new_cnpj_normalizado = normalizar_cnpj(new_cnpj)

        # Verifica se o novo username já existe em outro registro
        existing_user = Usuario.query.filter_by(username=new_username).first()
        if existing_user and existing_user.id != usuario.id:
            flash("Usuário já existe.", "error")
            return redirect(url_for('users.edit_user', user_id=usuario.id))

        # Se o CNPJ for informado, verifica se ele já existe em outro registro
        if new_cnpj:
            existing_cnpj_user = Usuario.query.filter_by(cnpj=new_cnpj_normalizado).first()
            if existing_cnpj_user and existing_cnpj_user.id != usuario.id:
                flash("Já existe um usuário com este CNPJ.", "error")
                return redirect(url_for('users.edit_user', user_id=usuario.id))

            # Opcional: Valide o novo CNPJ usando a função validar_cnpj, se necessário
            if not validar_cnpj(new_cnpj_normalizado):
                flash("CNPJ inválido. Por favor, verifique o valor informado.", "error")
                return redirect(url_for('users.edit_user', user_id=usuario.id))

        # Atualiza os dados do usuário com o username e CNPJ normalizado
        usuario.username = new_username
        usuario.nome_empresa = form.nome_empresa.data
        usuario.cnpj = new_cnpj_normalizado
        usuario.role = form.role.data

        # Se uma nova senha for informada, atualiza-a
        if form.password.data:
            usuario.set_password(form.password.data)
        
        db.session.commit()
        flash("Usuário atualizado com sucesso.", "success")
        return redirect(url_for('users.list_users'))
    
    return render_template('users/edit.html', form=form)

@users_bp.route('/delete/<int:user_id>', methods=['POST'])
@login_required
@role_required("RFB")
def delete_user(user_id):
    """Exclui um usuário (acessível apenas para administradores)."""

    if not admin_required(): # Verifica se é um usuário RFB 
        return redirect(url_for('pedidos.exibir_pedidos'))
    
    usuario = Usuario.query.get_or_404(user_id)
    db.session.delete(usuario)
    db.session.commit()
    flash("Usuário excluído com sucesso.", "success")
    return redirect(url_for('users.list_users'))
