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
    """
    Executa código Pandas e SEMPRE retorna o resultado.

    O código deve ser UMA EXPRESSÃO que retorna um valor:
    - CORRETO: df['valor'].sum()
    - ERRADO: resultado = df['valor'].sum()

    Se detectarmos um assignment simples, tentamos corrigi-lo automaticamente.
    """
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
<<<<<<< HEAD
        
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
=======

        # Log do código recebido para debug
        print(f"[execute_pandas_code] Código recebido: {code[:100]}...")

        # Validação prévia: detecta código claramente mal escrito
        code_stripped = code.strip()

        # Verifica se é um assignment simples de uma linha (caso comum de erro)
        import re

        simple_assignment = re.match(r"^\s*(\w+)\s*=\s*(.+)$", code_stripped, re.DOTALL)

        if simple_assignment and "\n" not in code_stripped:
            var_name = simple_assignment.group(1)
            expression = simple_assignment.group(2).strip()

            # Se detectamos assignment simples, avisa antes de tentar executar
            print(
                f"[execute_pandas_code] ⚠️ AVISO: Detectado assignment simples '{var_name} = ...'. Tentando auto-correção..."
            )

            # Tenta executar apenas a expressão diretamente
            try:
                result = eval(expression, {}, local_scope)
                if result is None:
                    return "❌ BAD CODE: Your expression returns None. The code is invalid. CORRECT IT and TRY AGAIN!"
                print(
                    f"[execute_pandas_code] ✅ AUTO-CORRIGIDO: Executei apenas a expressão, ignorando o assignment"
                )
                return f"🔧 AUTO-CORRECTED (removed assignment): {str(result)}"
            except Exception as e:
                print(f"[execute_pandas_code] ❌ Falha na auto-correção: {str(e)}")
                return f"❌ BAD CODE: This code is badly written and invalid. Error: {str(e)}. CORRECT IT: Remove the assignment '{var_name} =' and write only the expression '{expression}'. TRY AGAIN!"

        # Primeiro tenta avaliar como expressão (para retornar o resultado diretamente)
        try:
            result = eval(code, {}, local_scope)
            # Se o resultado for None, pode ser que o código não retornou nada
            if result is None:
                return "❌ BAD CODE: Your code returns None (no value). This is invalid. CORRECT IT to return an actual value and TRY AGAIN!"
            print(f"[execute_pandas_code] Resultado via eval(): {str(result)[:200]}")
            return str(result)
        except Exception as eval_error:
            # Se eval() falhar por QUALQUER motivo, tenta exec()
            # Isso inclui SyntaxError, NameError, etc.
            print(f"[execute_pandas_code] eval() falhou, tentando exec()...")

            import io
            import sys

            old_stdout = sys.stdout
            sys.stdout = captured_output = io.StringIO()

            try:
                exec(code, {}, local_scope)

                # Restaura stdout
                sys.stdout = old_stdout
                output = captured_output.getvalue()

                # Se há uma variável 'result' definida, retorna ela
                if "result" in local_scope:
                    result_value = local_scope["result"]
                    if result_value is None:
                        return "None (a variável 'result' está vazia)"
                    print(
                        f"[execute_pandas_code] Resultado via local_scope['result']: {str(result_value)[:200]}"
                    )
                    return str(result_value)

                # Se há output capturado, retorna
                if output.strip():
                    print(
                        f"[execute_pandas_code] Resultado via stdout: {output.strip()[:200]}"
                    )
                    return output.strip()

                # Se chegou aqui, o código não retornou nada
                # Vamos tentar detectar assignments simples e corrigir automaticamente
                print(
                    f"[execute_pandas_code] Código não retornou valor, tentando detectar assignment..."
                )

                # Detecta padrão: variavel = expressao
                import re

                assignment_match = re.match(
                    r"^\s*(\w+)\s*=\s*(.+)$", code.strip(), re.DOTALL
                )

                if assignment_match:
                    var_name = assignment_match.group(1)
                    expression = assignment_match.group(2)

                    # Verifica se a variável foi criada no local_scope
                    if var_name in local_scope:
                        auto_corrected_value = local_scope[var_name]
                        print(
                            f"[execute_pandas_code] 🔧 AUTO-CORREÇÃO: Detectado assignment '{var_name} = ...', retornando valor de '{var_name}'"
                        )
                        return f"🔧 AUTO-CORRIGIDO: {str(auto_corrected_value)}"

                    # Se não está no local_scope, tenta executar apenas a expressão
                    try:
                        print(
                            f"[execute_pandas_code] 🔧 Tentando executar apenas a expressão: {expression[:100]}"
                        )
                        result = eval(expression, {}, local_scope)
                        print(
                            f"[execute_pandas_code] ✅ Expressão executada com sucesso!"
                        )
                        return f"🔧 AUTO-CORRIGIDO (executei apenas a expressão): {str(result)}"
                    except:
                        pass

                # Se não conseguimos corrigir automaticamente, retorna mensagem de erro instrutiva
                return "❌ BAD CODE: This code is badly written and invalid. You used assignment (variable = ...) instead of returning a value. CORRECT IT: Remove the variable assignment and write only the expression. Example: instead of 'soma = df[\"valor\"].sum()' write just 'df[\"valor\"].sum()'. TRY AGAIN with the corrected code!"

            finally:
                sys.stdout = old_stdout

    except Exception as e:
        error_msg = f"Erro no código: {str(e)}"
        print(f"[execute_pandas_code] ❌ {error_msg}")
        return error_msg
>>>>>>> 9846f4717f6560c13876ec337e944a5090664172


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