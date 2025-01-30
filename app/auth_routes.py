from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app import db
from app.models import Usuario

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """ Página de login """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = Usuario.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("pedidos.exibir_pedidos"))  # Redireciona após login

        flash("Credenciais inválidas. Tente novamente.", "error")

    return render_template("login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    """ Rota para logout """
    logout_user()
    return redirect(url_for("auth.login"))
