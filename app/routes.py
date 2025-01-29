from flask import Blueprint, jsonify

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return jsonify({"message": "Bem-vindo ao Controle de Embarcações!"})

def register_routes(app):
    app.register_blueprint(main_bp)
