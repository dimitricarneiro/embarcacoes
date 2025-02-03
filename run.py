from app import create_app, db
from app.models import Usuario  # 🔹 Importa o modelo de usuários
from flask import Flask
import os

app = create_app()

# 🔹 Criar banco de dados se não existir
with app.app_context():
    if not os.path.exists("database.db"):  # Verifica se o arquivo do banco já existe
        db.create_all()  # 🔹 Cria as tabelas no banco de dados
        print("Banco de dados criado!")

        # 🔹 Criar usuário administrador padrão se ainda não existir
        if not Usuario.query.filter_by(username="admin").first():
            admin_user = Usuario(username="admin", role="RFB")
            admin_user.set_password("123456")  # Define a senha do admin
            db.session.add(admin_user)
            db.session.commit()
            print("Usuário administrador criado!")

if __name__ == '__main__':
    app.run(debug=True)

