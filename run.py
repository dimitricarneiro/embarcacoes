from app import create_app, db
from app.models import Usuario  # 🔹 Importa o modelo de usuários
import os

app = create_app()

# 🔹 Criar banco de dados se não existir
with app.app_context():
    db_path = os.path.join(app.instance_path, "database.db")  # 🔹 Caminho correto para o banco
    if not os.path.exists(db_path):  
        db.create_all()  # 🔹 Cria as tabelas no banco de dados
        print("Banco de dados criado!")

        users_to_add = []  # Lista para armazenar os usuários que precisam ser adicionados

        # 🔹 Criar usuário administrador padrão se ainda não existir
        if not Usuario.query.filter_by(username="admin").first():
            admin_user = Usuario(username="admin", role="RFB")
            admin_user.set_password("123456")  # Define a senha do admin
            users_to_add.append(admin_user)
            print("Usuário administrador criado!")

        # 🔹 Criar usuário comum 1
        if not Usuario.query.filter_by(username="usuario").first():
            user1 = Usuario(username="usuario", role="comum")
            user1.set_password("123456")
            users_to_add.append(user1)
            print("Usuário 'usuario' criado!")

        # 🔹 Criar usuário comum 2
        if not Usuario.query.filter_by(username="usuario2").first():
            user2 = Usuario(username="usuario2", role="comum")
            user2.set_password("123456")
            users_to_add.append(user2)
            print("Usuário 'usuario2' criado!")

        # 🔹 Adicionar todos os usuários e salvar no banco **apenas uma vez**
        if users_to_add:
            db.session.add_all(users_to_add)
            db.session.commit()
            print("Todos os usuários foram salvos no banco!")

if __name__ == '__main__':
    app.run(debug=True)
