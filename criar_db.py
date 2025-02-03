from app import create_app, db

app = create_app()  # Inicializa a aplicação corretamente

with app.app_context():
    db.create_all()  # Cria todas as tabelas no banco de dados

print("Banco de dados criado com sucesso!")
