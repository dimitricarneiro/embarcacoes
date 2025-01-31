from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app import db
from app.models import Usuario
from app import limiter

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute; 10 per hour")  # 🔹 5 tentativas por minuto, 10 por hora
def login():
    """ Página de login """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        remember = "remember" in request.form

        user = Usuario.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user, remember=remember)
            return redirect(url_for("pedidos.exibir_pedidos"))

        flash("Credenciais inválidas. Tente novamente.", "error")

    return render_template("login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    """ Rota para logout """
    logout_user()
    return redirect(url_for("auth.login"))
