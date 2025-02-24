from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user

def role_required(*roles):
    """
    Decorator que garante que o usuário logado possua uma das roles especificadas.
    
    Parâmetros:
      *roles (tuple): Lista de roles permitidas para acessar a rota.
    
    Se o usuário não tiver uma das roles permitidas, a função pode:
      - Redireciona para uma página padrão;
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.role not in roles:
                # Exemplo: exibindo mensagem e redirecionando para a página inicial
                flash("Você não tem permissão para acessar esta página.", "danger")
                return redirect(url_for("auth.logout")) #desloga o usuário

                # abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
