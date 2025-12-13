import os
import sys
from dotenv import load_dotenv

print("--- 🕵️ DIAGNÓSTICO DUNDER AI ---")

# 1. Verifica onde estamos
current_dir = os.getcwd()
print(f"📂 Diretório Atual: {current_dir}")

# 2. Tenta carregar o .env
env_path = os.path.join(current_dir, ".env")
if os.path.exists(env_path):
    print("✅ Arquivo .env encontrado.")
    load_dotenv(env_path)
else:
    print("❌ Arquivo .env NÃO encontrado na raiz!")
    print(f"   Esperado em: {env_path}")

# 3. Verifica a Chave
api_key = os.getenv("ELEVENLABS_API_KEY")
if api_key:
    masked_key = api_key[:4] + "*" * (len(api_key)-8) + api_key[-4:]
    print(f"✅ Chave ElevenLabs detectada: {masked_key}")
else:
    print("❌ Variável 'ELEVENLABS_API_KEY' está vazia ou não existe no .env")

# 4. Verifica a Biblioteca e Conexão
print("\n--- TESTANDO BIBLIOTECA ---")
try:
    from elevenlabs.client import ElevenLabs
    print("✅ Biblioteca 'elevenlabs' instalada corretamente.")
    
    if api_key:
        print("🔄 Tentando conectar com a API da ElevenLabs...")
        try:
            client = ElevenLabs(api_key=api_key)
            # Tenta listar vozes para ver se a chave é válida
            voices = client.voices.get_all()
            print(f"🎉 SUCESSO! Conexão estabelecida. Você tem acesso a {len(voices.voices)} vozes.")
        except Exception as e:
            print(f"❌ Erro de Autenticação: A chave parece inválida.\n   Detalhe: {e}")
    else:
        print("⚠️ Pulando teste de conexão (sem chave).")

except ImportError:
    print("❌ Biblioteca 'elevenlabs' NÃO está instalada.")
    print("   Rode: pip install elevenlabs")
except Exception as e:
    print(f"❌ Erro inesperado na importação: {e}")

print("\n--- FIM DO DIAGNÓSTICO ---")