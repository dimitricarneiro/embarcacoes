import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging(app):
    env = os.environ.get('FLASK_ENV', 'development')
    
    if env == 'production':
        log_dir = '/var/log/embarcacoes'
    else:
        # Em desenvolvimento, os logs ficarão na pasta 'logs' do projeto
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, 'app.log')
    file_handler = RotatingFileHandler(log_file, maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [em %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Aplicação iniciada')
