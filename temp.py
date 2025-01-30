#arquivo temporário para executar comandos python de várias linhas sem precisar usar o terminal
#Este arquivo não altera em nada o nosso app. É apenas temporário!

from app import create_app, db
from app.models import Usuario

app = create_app()
with app.app_context():
    # Criar um usuário comum
    if not Usuario.query.filter_by(username="usuario_teste").first():  # Evita duplicação
        user = Usuario(username="usuario", role="comum")
        user.set_password("123456")  # Define a senha segura
        db.session.add(user)
        db.session.commit()
        print("Usuário 'usuario_teste' criado com sucesso!")

print("Banco de dados atualizado!")
