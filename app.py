#!/usr/bin/env python3
"""
Aplicativo Flask para exibir os cabeçalhos HTTP recebidos.
Use a rota /debug_headers para verificar os cabeçalhos enviados pelo Apache (incluindo os cabeçalhos SSL, se presentes).
"""

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/debug_headers', methods=['GET'])
def debug_headers():
    """
    Rota que retorna todos os cabeçalhos HTTP recebidos em formato JSON.
    Isso é útil para verificar se os cabeçalhos SSL (ex.: SSL_CLIENT_S_DN, SSL_CLIENT_VERIFY, etc.)
    estão sendo repassados corretamente pelo servidor.
    """
    headers = dict(request.headers)
    return jsonify(headers)

if __name__ == '__main__':
    # Executa o aplicativo na porta 5000 e escuta em todas as interfaces (0.0.0.0)
    app.run(host='0.0.0.0', port=5000, debug=True)
