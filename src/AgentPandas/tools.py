# ARQUIVO: src/agentPandas/tools.py
import pandas as pd
import os
from dotenv import load_dotenv

# Carrega variáveis
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.abspath(os.path.join(current_dir, "..", "..", ".env"))
load_dotenv(env_path)

def _get_gs_path():
    """Helper interno para montar o caminho do GCS."""
    bucket = os.environ.get("BUCKET_NAME")
    blob = os.environ.get("BLOB_NAME")
    
    if not bucket or not blob:
        raise ValueError("Variáveis BUCKET_NAME ou BLOB_NAME não definidas no .env")
    
    # Monta o caminho no formato que o Pandas/GCSFS entende
    return f"gs://{bucket}/{blob}"

def download_csv_from_bucket():
    """
    Agora essa função apenas valida o acesso e retorna o caminho na nuvem.
    Mantivemos o nome 'download' para não precisar reescrever o prompt do agente,
    mas ele não baixa nada físico para o disco.
    """
    print("☁️ Verificando acesso ao arquivo na nuvem...")
    try:
        path = _get_gs_path()
        
        # Tenta ler apenas a primeira linha para validar se o acesso/credencial está ok
        # storage_options={"token": "google_default"} usa as credenciais do ambiente
        pd.read_csv(path, nrows=1)
        
        print(f"✅ Conexão GCS estabelecida: {path}")
        return {"success": True, "local_path": path} # O 'local_path' agora é um endereço gs://

    except Exception as e:
        return {"success": False, "error": f"Erro ao conectar no Bucket: {str(e)}"}

def load_csv_preview(local_path: str = None):
    # Se o agente não passar o path, pega o padrão
    path = local_path if local_path else _get_gs_path()
    try:
        df = pd.read_csv(path, sep=None, engine='python', nrows=5)
        return {
            "columns": list(df.columns),
            "preview": df.to_dict(orient="records")
        }
    except Exception as e:
        return {"error": str(e)}

def get_statistics(local_path: str = None):
    path = local_path if local_path else _get_gs_path()
    try:
        df = pd.read_csv(path, sep=None, engine='python')
        return df.describe(include='all').to_string()
    except Exception as e:
        return {"error": str(e)}

def execute_pandas_code(local_path: str, code: str):
    path = local_path if local_path else _get_gs_path()
    try:
        # Lê direto da nuvem
        df = pd.read_csv(path, sep=None, engine='python')
        
        # Limpeza de colunas
        df.columns = df.columns.str.strip()
        
        local_scope = {"df": df, "pd": pd}
        try:
            return str(eval(code, {}, local_scope))
        except:
            exec(code, {}, local_scope)
            if 'result' in local_scope:
                return str(local_scope['result'])
            return "Código executado."
    except Exception as e:
        return f"Erro no código: {str(e)}"

def detect_fraud_patterns(local_path: str = None):
    path = local_path if local_path else _get_gs_path()
    try:
        df = pd.read_csv(path, sep=None, engine='python')
        df.columns = df.columns.str.strip()
        
        report = {}
        col_valor = next((c for c in df.columns if c.lower() in ['valor', 'amount']), None)
        
        if col_valor:
            # Smurfing simples
            dups = df[df.duplicated(subset=[col_valor], keep=False)]
            # Filtra duplicatas de valor alto (>100)
            high_dups = dups[dups[col_valor] > 100]
            
            if not high_dups.empty:
                report['repeated_high_values'] = high_dups.head(5).to_dict(orient="records")
                
        return report if report else "Nenhum padrão óbvio."
    except Exception as e:
        return {"error": str(e)}