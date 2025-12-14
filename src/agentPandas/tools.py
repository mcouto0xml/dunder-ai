# ARQUIVO: src/agentPandas/tools.py
import pandas as pd
import os
import sys
import io
from typing import Optional, Dict, Any, Union
from dotenv import load_dotenv

# Carrega variáveis
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.abspath(os.path.join(current_dir, "..", "..", ".env"))
load_dotenv(env_path)

# Cache global para armazenar o DataFrame
_dataframe_cache: Dict[str, Any] = {"df": None, "path": None}


def _get_gs_path() -> str:
    """Helper interno para montar o caminho do GCS."""
    bucket = os.environ.get("BUCKET_NAME")
    blob = os.environ.get("BLOB_NAME")

    if not bucket or not blob:
        raise ValueError("Variáveis BUCKET_NAME ou BLOB_NAME não definidas no .env")

    # Monta o caminho no formato que o Pandas/GCSFS entende
    return f"gs://{bucket}/{blob}"


def _load_dataframe(path: str) -> pd.DataFrame:
    """Carrega ou retorna o DataFrame do cache."""
    global _dataframe_cache

    # Se já temos o DataFrame no cache para esse caminho, retorna
    if (
        isinstance(_dataframe_cache["df"], pd.DataFrame)
        and _dataframe_cache["path"] == path
    ):
        return _dataframe_cache["df"]

    # Caso contrário, carrega da nuvem e armazena no cache
    print(f"Carregando DataFrame de {path}...")
    df = pd.read_csv(path, sep=None, engine="python")
    # Limpeza básica de colunas
    df.columns = df.columns.str.strip()
    
    _dataframe_cache["df"] = df
    _dataframe_cache["path"] = path

    return df


def download_csv_from_bucket() -> Dict[str, Any]:
    """
    Valida o acesso ao CSV na nuvem e pré-carrega o DataFrame no cache.
    """
    print("Verificando acesso ao arquivo na nuvem...")
    try:
        path = _get_gs_path()
        _load_dataframe(path)
        print(f"Conexão GCS estabelecida: {path}")
        return {"success": True, "local_path": path}

    except Exception as e:
        return {"success": False, "error": f"Erro ao conectar no Bucket: {str(e)}"}


def load_csv_preview(local_path: str = "") -> Dict[str, Any]:
    path = local_path if local_path else _get_gs_path()
    try:
        df = _load_dataframe(path)
        preview_df = df.head(5)
        return {
            "columns": list(df.columns),
            "preview": preview_df.to_dict(orient="records"),
        }
    except Exception as e:
        return {"error": str(e)}


def get_statistics(local_path: str = "") -> Dict[str, Any]:
    path = local_path if local_path else _get_gs_path()
    try:
        df = _load_dataframe(path)
        return {"statistics": df.describe(include="all").to_string()}
    except Exception as e:
        return {"error": str(e)}


# --- AQUI ESTÁ A CORREÇÃO CRÍTICA ---
def execute_pandas_code(local_path: str, code: str) -> str:
    path = local_path if local_path else _get_gs_path()
    
    # 1. Preparar captura de output (print)
    old_stdout = sys.stdout
    redirected_output = io.StringIO()
    sys.stdout = redirected_output

    try:
        # Carrega DF
        df = _load_dataframe(path)
        
        # Define escopo local para o exec
        local_scope = {"df": df, "pd": pd}
        
        # 2. Executa o código
        exec(code, {}, local_scope)
        
        # 3. Pega o que foi impresso
        output = redirected_output.getvalue()
        
        # Lógica de fallback: se não imprimiu nada, tenta achar variável 'result'
        if not output.strip():
            if "result" in local_scope:
                return str(local_scope["result"])
            return "Código executado com sucesso, mas NADA foi impresso. Use print() para ver o valor."
            
        return output

    except Exception as e:
        return f"Erro na execução do código Python: {str(e)}"
    
    finally:
        # 4. IMPORTANTE: Restaurar o stdout original para não quebrar o servidor
        sys.stdout = old_stdout


def detect_fraud_patterns(local_path: str = "") -> Dict[str, Any]:
    path = local_path if local_path else _get_gs_path()
    try:
        df = _load_dataframe(path)

        report: Dict[str, Any] = {}
        # Tenta achar coluna de valor flexivelmente
        col_valor = next(
            (c for c in df.columns if c.lower() in ["valor", "amount", "value", "total"]), None
        )

        if col_valor:
            # Smurfing simples: duplicatas exatas de valor alto
            dups = df[df.duplicated(subset=[col_valor], keep=False)]
            
            # Garante que é numérico
            if pd.api.types.is_numeric_dtype(df[col_valor]):
                high_dups_mask = dups[col_valor] > 100 
                high_dups = dups[high_dups_mask]

                if len(high_dups) > 0:
                    report["repeated_high_values"] = high_dups.head(5).to_dict(orient="records")
            else:
                 report["warning"] = f"Coluna {col_valor} não é numérica."

        return report if report else {"message": "Nenhum padrão óbvio detectado."}
    except Exception as e:
        return {"error": str(e)}