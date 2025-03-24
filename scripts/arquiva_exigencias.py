#!/usr/bin/env python
# arquiva_exigencias.py

from datetime import date
from sqlalchemy import or_
from app import create_app, db
from models import PedidoAutorizacao, Exigencia

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
        # Opcional: atualiza somente se o status não for "rejeitado" já
        if pedido.status != "rejeitado":
            pedido.status = "rejeitado"
            app.logger.info(
                f"Pedido {pedido.id} arquivado/rejeitado pois a exigência {exigencia.id} não foi atendida."
            )

    # Comita as alterações no banco de dados
    db.session.commit()

    app.logger.info("Script de arquivamento de exigências concluído com sucesso.")
