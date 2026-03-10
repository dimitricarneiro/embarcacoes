import os
import redis
from dotenv import load_dotenv

# Define o caminho para o arquivo .env que está um nível acima
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')

# Carrega especificamente desse caminho
load_dotenv(dotenv_path=dotenv_path)

# Recupera os dados das variáveis de ambiente
REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')

try:
    r = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        decode_responses=True
    )

    if r.ping():
        print(f"✅ Conectado com sucesso ao Redis em {REDIS_HOST}")

except Exception as e:
    print(f"❌ Erro ao conectar: {e}")