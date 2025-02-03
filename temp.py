#arquivo temporário para executar comandos python de várias linhas sem precisar usar o terminal
#Este arquivo não altera em nada o nosso app. É apenas temporário!

from app import create_app, db
from app.models import Usuario

app = create_app()  # Inicializa a aplicação

with app.app_context():

    # Criando um usuário comum
    usuario = Usuario(username="usuario2", role="comum")
    usuario.set_password("123456")  # Hash da senha

    # Adicionando ao banco de dados
    db.session.add(usuario)
    db.session.commit()

    print("Usuários criados com sucesso!")
