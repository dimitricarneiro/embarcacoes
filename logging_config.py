# Configurações do sistema de log, que guarda informações sobre ações realizadas no sistema.

import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging(app):
    # Cria a pasta de logs, se ela não existir
    if not os.path.exists('logs'):
        os.mkdir('logs')
   
    # Configura um handler que rotaciona os arquivos de log
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [em %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    
    # Adiciona o handler ao logger da aplicação
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Aplicação iniciada')
