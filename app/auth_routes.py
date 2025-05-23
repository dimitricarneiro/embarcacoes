from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import Usuario
from app.forms import LoginForm  # importa o formulário de login
from app import limiter

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("12 per minute; 60 per hour")
def login():
    try:
        form = LoginForm()
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            remember = form.remember.data

            user = Usuario.query.filter_by(username=username).first()

            if user and user.check_password(password):
                login_user(user, remember=remember)
                session.permanent = True

                current_app.logger.info(
                    f"Usuário '{username}' efetuou login. IP: {request.remote_addr}"
                )

                if user.role == "RFB":
                    return redirect(url_for("pedidos.admin_dashboard"))
                elif user.role == "agencia_maritima":
                    return redirect(url_for("agencias.agenciar_pedidos"))
                else:
                    return redirect(url_for("pedidos.exibir_pedidos"))

            flash("Credenciais inválidas. Tente novamente.", "error")

        return render_template("login.html", form=form)

    except Exception as e:
        current_app.logger.exception("Falha inesperada em /auth/login")
        raise

@auth_bp.route("/renovar-sessao", methods=["GET"])
@login_required
def renovar_sessao():
    """Renova a sessão do usuário ao clicar em 'Continuar Logado' no modal."""
    session.permanent = True  # Estende o tempo da sessão
    return jsonify({"message": "Sessão renovada"}), 200

from flask import session, current_app, request, redirect, url_for
from flask_login import logout_user, login_required

@auth_bp.route("/logout")
@login_required
def logout():
    """Rota para logout."""
    # Captura o nome do usuário antes de efetuar logout
    username = current_user.username

    logout_user()
    session.clear()  # Limpa a sessão, removendo mensagens flash e outros dados

    # Registra o evento de logout com informações do usuário e IP
    current_app.logger.info(
        f"Usuário '{username}' efetuou logout. IP: {request.remote_addr}"
    )

    return redirect(url_for("auth.login"))

