from app import db, create_app
from app.models import Usuario

if __name__ == '__main__':
    app = create_app()
    password = input('Digite a senha:')
    with app.app_context():
        usuario: Usuario = Usuario.query.filter_by(username="admin").first()
        usuario.set_password(password)
        db.session.add(usuario)
        db.session.commit()
        print('Senha do usuário admin mudada!')
