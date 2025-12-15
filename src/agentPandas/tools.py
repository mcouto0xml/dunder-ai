import pandas as pd
import os
import sys
import io
from typing import Dict, Any
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

    return f"gs://{bucket}/{blob}"


def _load_dataframe(path: str) -> pd.DataFrame:
    """Carrega ou retorna o DataFrame do cache."""
    global _dataframe_cache

    if (
        isinstance(_dataframe_cache["df"], pd.DataFrame)
        and _dataframe_cache["path"] == path
    ):
        return _dataframe_cache["df"]

    print(f"Carregando DataFrame de {path}...")
    df = pd.read_csv(path, sep=None, engine="python")
    df.columns = df.columns.str.strip()

    _dataframe_cache["df"] = df
    _dataframe_cache["path"] = path

    return df


def download_csv_from_bucket() -> Dict[str, Any]:
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


def execute_pandas_code(local_path: str, code: str) -> str:
    """
    Executa código Pandas e SEMPRE retorna um resultado válido ou erro instrutivo.

    Espera-se que o código seja UMA EXPRESSÃO.
    Ex:
      ✅ df["valor"].sum()
      ❌ soma = df["valor"].sum()
    """
    path = local_path if local_path else _get_gs_path()

    try:
        df = _load_dataframe(path)
        local_scope = {"df": df, "pd": pd}

        print(f"[execute_pandas_code] Código recebido: {code[:100]}...")

        code_stripped = code.strip()

        # Detecta assignment simples
        import re

        simple_assignment = re.match(
            r"^\s*(\w+)\s*=\s*(.+)$", code_stripped, re.DOTALL
        )

        if simple_assignment and "\n" not in code_stripped:
            var_name = simple_assignment.group(1)
            expression = simple_assignment.group(2).strip()

            print(
                f"[execute_pandas_code] ⚠️ Assignment detectado '{var_name} = ...'. Tentando auto-correção..."
            )

            try:
                result = eval(expression, {}, local_scope)
                if result is None:
                    return (
                        "❌ BAD CODE: Expression returns None. "
                        "Remove assignment and return a value."
                    )
                return f"🔧 AUTO-CORRECTED: {str(result)}"
            except Exception as e:
                return (
                    f"❌ BAD CODE: Invalid assignment. Error: {str(e)}. "
                    f"Use only the expression: {expression}"
                )

        # Tenta avaliar diretamente como expressão
        try:
            result = eval(code, {}, local_scope)
            if result is None:
                return (
                    "❌ BAD CODE: Code returns None. "
                    "Write an expression that returns a value."
                )
            return str(result)

        except Exception:
            # Fallback para exec()
            old_stdout = sys.stdout
            sys.stdout = captured_output = io.StringIO()

            try:
                exec(code, {}, local_scope)
            finally:
                sys.stdout = old_stdout

            output = captured_output.getvalue().strip()

            if "result" in local_scope:
                return str(local_scope["result"])

            if output:
                return output

            return (
                "❌ BAD CODE: Code did not return any value. "
                "Avoid assignments and return an expression directly."
            )

    except Exception as e:
        return f"Erro no código: {str(e)}"


def detect_fraud_patterns(local_path: str = "") -> Dict[str, Any]:
    path = local_path if local_path else _get_gs_path()
    try:
        df = _load_dataframe(path)

        report: Dict[str, Any] = {}

        col_valor = next(
            (
                c
                for c in df.columns
                if c.lower() in ["valor", "amount", "value", "total"]
            ),
            None,
        )

        if col_valor:
            dups = df[df.duplicated(subset=[col_valor], keep=False)]

            if pd.api.types.is_numeric_dtype(df[col_valor]):
                high_dups = dups[dups[col_valor] > 100]

                if len(high_dups) > 0:
                    report["repeated_high_values"] = high_dups.head(5).to_dict(
                        orient="records"
                    )
            else:
                report["warning"] = f"Coluna {col_valor} não é numérica."

        return report if report else {"message": "Nenhum padrão óbvio detectado."}

    except Exception as e:
        return {"error": str(e)}
