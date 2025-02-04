from app import create_app, db
from app.models import Usuario

# Criar contexto da aplicação
app = create_app()
with app.app_context():
    users_to_add = []

    # Criar usuário admin
    if not Usuario.query.filter_by(username="admin").first():
        admin = Usuario(
            username="admin",
            role="RFB",
            nome_empresa="RFB",
            cnpj="26.994.558/0001-23"
        )
        admin.set_password("123456")
        users_to_add.append(admin)
        print("Usuário admin criado!")

    # Criar usuário comum 1
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

    # Criar usuário comum 2
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

    # Adicionar usuários ao banco e commitar
    if users_to_add:
        db.session.add_all(users_to_add)
        db.session.commit()
        print("Todos os usuários foram adicionados ao banco!")
