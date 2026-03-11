import os
import time
import json
import redis
from dotenv import load_dotenv

# 1. Configurações Iniciais
load_dotenv()
STREAM_NAME = "fila:formularios"
GROUP_NAME = "grupo:processamento"
CONSUMER_NAME = "worker_171"

def connect_redis():
    return redis.Redis(
        host=os.getenv('REDIS_HOST'),
        port=os.getenv('REDIS_PORT'),
        password=os.getenv('REDIS_PASSWORD'),
        decode_responses=True
    )

def process_worker():
    r = connect_redis()
    print(f"🚀 Worker iniciado. Aguardando novos formulários em {STREAM_NAME}...")

    while True:
        try:
            # 2. LEITURA BLOQUANTE (O "Telefone fora do gancho")
            # block=0 significa esperar para sempre até chegar algo
            # count=1 pega uma tarefa por vez
            # '>' significa pegar apenas mensagens novas que ninguém leu
            mensagens = r.xreadgroup(GROUP_NAME, CONSUMER_NAME, {STREAM_NAME: '>'}, count=1, block=0)

            if not mensagens:
                continue

            for stream, dados in mensagens:
                for message_id, payload in dados:
                    print(f"\n📦 Nova tarefa recebida! ID: {message_id}")
                    
                    # O dado no Redis Streams vem como um dicionário
                    # Se você enviou um JSON na chave 'dados', nós o lemos aqui
                    conteudo_json = payload.get('dados')
                    
                    # --- SIMULAÇÃO DO PROCESSAMENTO ---
                    print(f"🛠️  Processando JSON: {conteudo_json}")
                    time.sleep(2) # Simula um trabalho pesado (ex: gerar PDF)
                    # ----------------------------------

                    # 3. CONFIRMAÇÃO (ACK)
                    # Avisa o Redis que a tarefa foi concluída com sucesso
                    r.xack(STREAM_NAME, GROUP_NAME, message_id)
                    print(f"✅ Tarefa {message_id} finalizada e removida da lista de pendentes.")

        except redis.exceptions.ConnectionError:
            print("⚠️ Conexão perdida com o 174. Tentando reconectar em 5 segundos...")
            time.sleep(5)
            r = connect_redis()
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            time.sleep(2)

if __name__ == "__main__":
    process_worker()