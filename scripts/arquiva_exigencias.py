#!/usr/bin/env python
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import date
from sqlalchemy import or_
from app import create_app, db
from app.models import PedidoAutorizacao, Exigencia  # Ajustado para a estrutura do seu projeto

# Cria a aplicação Flask (ajuste se necessário)
app = create_app()

with app.app_context():
    # Consulta exigências cujo prazo foi ultrapassado e que ainda não foram respondidas.
    exigencias = Exigencia.query.filter(
        Exigencia.prazo_exigencia < date.today(),
        or_(Exigencia.texto_resposta == None, Exigencia.texto_resposta == ''),
        Exigencia.data_resposta == None
    ).all()

    # Para cada exigência não atendida, atualiza o status do pedido para "rejeitado".
    for exigencia in exigencias:
        pedido = exigencia.pedido
        if pedido.status != "rejeitado":
            pedido.status = "rejeitado"
            app.logger.info(f"Pedido {pedido.id} arquivado/rejeitado pois a exigência {exigencia.id} não foi atendida.")

    db.session.commit()
    app.logger.info("Script de arquivamento de exigências concluído com sucesso.")
