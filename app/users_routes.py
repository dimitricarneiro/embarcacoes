from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Usuario
from werkzeug.security import generate_password_hash
from app.utils import validar_cnpj

users_bp = Blueprint('users', __name__, url_prefix='/users')

def admin_required():
    """Função auxiliar para permitir acesso apenas a administradores (role 'RFB')."""
    if current_user.role != "RFB":
        flash("Acesso não autorizado.", "error")
        return False
    return True

@users_bp.route('/', methods=['GET'])
@login_required
def list_users():
    """Lista todos os usuários (acessível apenas para administradores)."""
    if not admin_required():
        return redirect(url_for('pedidos.exibir_pedidos'))
    usuarios = Usuario.query.all()
    return render_template('users/list.html', usuarios=usuarios)

@users_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_user():
    if not admin_required():
        return redirect(url_for('pedidos.exibir_pedidos'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        nome_empresa = request.form.get('nome_empresa')
        cnpj = request.form.get('cnpj')
        role = request.form.get('role', 'comum')

        if not username or not password:
            flash("Usuário e senha são obrigatórios.", "error")
            return redirect(url_for('users.create_user'))

        # Verifica se o usuário já existe
        if Usuario.query.filter_by(username=username).first():
            flash("Usuário já existe.", "error")
            return redirect(url_for('users.create_user'))

        # Verifica se já existe um usuário com o mesmo CNPJ (se o CNPJ for informado)
        if cnpj and Usuario.query.filter_by(cnpj=cnpj).first():
            flash("Já existe um usuário com este CNPJ.", "error")
            return redirect(url_for('users.create_user'))

        # Validação do CNPJ (usando a função validar_cnpj do módulo utils)
        from app.utils import validar_cnpj
        if cnpj and not validar_cnpj(cnpj):
            flash("CNPJ inválido. Por favor, verifique o valor informado.", "error")
            return redirect(url_for('users.create_user'))

        novo_usuario = Usuario(
            username=username,
            nome_empresa=nome_empresa,
            cnpj=cnpj,
            role=role
        )
        novo_usuario.set_password(password)
        db.session.add(novo_usuario)
        db.session.commit()
        flash("Usuário criado com sucesso.", "success")
        return redirect(url_for('users.list_users'))

    return render_template('users/create.html')

@users_bp.route('/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    """Edita os dados de um usuário existente (acessível apenas para administradores)."""
    if not admin_required():
        return redirect(url_for('pedidos.exibir_pedidos'))
    
    usuario = Usuario.query.get_or_404(user_id)
    if request.method == 'POST':
        usuario.username = request.form.get('username')
        usuario.nome_empresa = request.form.get('nome_empresa')
        usuario.cnpj = request.form.get('cnpj')
        usuario.role = request.form.get('role', 'comum')

        # Se for informada uma nova senha, atualiza-a
        password = request.form.get('password')
        if password:
            usuario.set_password(password)

        db.session.commit()
        flash("Usuário atualizado com sucesso.", "success")
        return redirect(url_for('users.list_users'))
    
    return render_template('users/edit.html', usuario=usuario)

@users_bp.route('/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    """Exclui um usuário (acessível apenas para administradores)."""
    if not admin_required():
        return redirect(url_for('pedidos.exibir_pedidos'))
    
    usuario = Usuario.query.get_or_404(user_id)
    db.session.delete(usuario)
    db.session.commit()
    flash("Usuário excluído com sucesso.", "success")
    return redirect(url_for('users.list_users'))
