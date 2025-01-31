#arquivo temporário para executar comandos python de várias linhas sem precisar usar o terminal
#Este arquivo não altera em nada o nosso app. É apenas temporário!

from app import create_app, db

app = create_app()

with app.app_context():
    db.create_all()
    print("Banco de dados atualizado! A tabela 'notificacoes' foi criada com sucesso.")

