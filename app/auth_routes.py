from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import Usuario
from app import limiter

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute; 30 per hour")  # 🔹 10 tentativas por minuto, 30 por hora
def login():
    """Página de login."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        remember = "remember" in request.form

        user = Usuario.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user, remember=remember)
            # Define a sessão como permanente para que a expiração funcione
            session.permanent = True

            # Registra o evento de login com informações do usuário e IP
            current_app.logger.info(
                f"Usuário '{username}' efetuou login. IP: {request.remote_addr}"
            )

            if user.role == "RFB":
                return redirect(url_for("pedidos.admin_dashboard"))
            return redirect(url_for("pedidos.exibir_pedidos"))

        flash("Credenciais inválidas. Tente novamente.", "error")

    return render_template("login.html")

@auth_bp.route("/renovar-sessao", methods=["GET"])
@login_required
def renovar_sessao():
    """Renova a sessão do usuário ao clicar em 'Continuar Logado' no modal."""
    session.permanent = True  # Estende o tempo da sessão
    return jsonify({"message": "Sessão renovada"}), 200

@auth_bp.route("/logout")
@login_required
def logout():
    """Rota para logout."""
    # Captura o nome do usuário antes de efetuar logout
    username = current_user.username

    logout_user()

    # Registra o evento de logout com informações do usuário e IP
    current_app.logger.info(
        f"Usuário '{username}' efetuou logout. IP: {request.remote_addr}"
    )

    return redirect(url_for("auth.login"))
