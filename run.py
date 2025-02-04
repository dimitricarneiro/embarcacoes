from app import create_app, db
from app.models import Usuario
import os

app = create_app()

with app.app_context():
    db_path = app.config["SQLALCHEMY_DATABASE_URI"].replace("sqlite:///", "")
    
    # Se o arquivo do banco não existir, cria o banco e os usuários
    if not os.path.exists(db_path):  
        db.create_all()
        print("Banco de dados criado!")
        
        users_to_add = []

        if not Usuario.query.filter_by(username="admin").first():
            admin_user = Usuario(
                username="admin",
                role="RFB",
                nome_empresa="RFB",
                cnpj="26.994.558/0001-23"
            )
            admin_user.set_password("123456")
            users_to_add.append(admin_user)
            print("Usuário administrador criado!")

        if not Usuario.query.filter_by(username="usuario").first():
            user1 = Usuario(
                username="usuario",
                role="comum",
                nome_empresa="Empresa Usuario 1",
                cnpj="09.441.804/0001-09"
            )
            user1.set_password("123456")
            users_to_add.append(user1)
            print("Usuário 'usuario' criado!")

        if not Usuario.query.filter_by(username="usuario2").first():
            user2 = Usuario(
                username="usuario2",
                role="comum",
                nome_empresa="Empresa Usuario 2",
                cnpj="96.411.668/0001-09"
            )
            user2.set_password("123456")
            users_to_add.append(user2)
            print("Usuário 'usuario2' criado!")

        if users_to_add:
            db.session.add_all(users_to_add)
            db.session.commit()
            print("Todos os usuários foram adicionados ao banco!")
            
if __name__ == '__main__':
    app.run(debug=True)
