import uuid
import asyncio
import sys
import os
import json
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
root_path = os.path.abspath(os.path.join(current_dir, "..", ".."))
env_path = os.path.join(current_dir, "..", "..", ".env")
load_dotenv(env_path)

if root_path not in sys.path:
    sys.path.append(root_path)

from google.adk.agents.llm_agent import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import vertexai

try:
    from .tools import (
        download_csv_from_bucket,
        load_csv_preview,
        get_statistics,
        execute_pandas_code,
        detect_fraud_patterns,
    )
except ImportError as e:
    try:
        from tools import (
            download_csv_from_bucket,
            load_csv_preview,
            get_statistics,
            execute_pandas_code,
            detect_fraud_patterns,
        )
    except ImportError as e2:
        print("\n\n" + "=" * 50)
        print("ERRO CRITICO DE IMPORTACAO")
        print(f"Não foi possível encontrar o arquivo 'tools.py' na pasta {current_dir}")
        print("Certifique-se de que você criou o arquivo 'src/agentPandas/tools.py'!")
        print("=" * 50 + "\n\n")
        raise e2

APP_NAME = "dunderai"
try:
    vertexai.init(project="dunderai", location="us-west1")
except:
    pass

SYSTEM_PROMPT = """<system_prompt>
    <role>
        Você é o **Analista Financeiro Sênior e Cientista de Dados** da Dunder Mifflin.
        Sua missão é responder a perguntas sobre 'transacoes_bancarias.csv' usando Python/Pandas.
        
        **SEJA EFICIENTE:** Execute cada operação UMA ÚNICA VEZ. Não repita buscas ou chamadas de ferramentas.
    </role>

    <CRITICAL_RESPONSE_FORMAT>
        ABSOLUTE REQUIREMENT - READ THIS FIRST
        
        You MUST ALWAYS return your final response as a natural language explanation in Portuguese or English (matching the query language).
        
        **NEVER return raw tool outputs, DataFrames, lists, or JSON as your final answer!**
        
        Your workflow should be:
        1. Call tools (download_csv_from_bucket, execute_pandas_code, etc.)
        2. Analyze the results internally
        3. Formulate a clear, natural language response
        4. Return ONLY that natural language response to the user
        
        GOOD EXAMPLES:
        - "Encontrei 3 transações para Michael Scott totalizando $450,32. As transações foram: compra de papel em 01/04 ($200), almoço em 05/04 ($150,32), e taxi em 10/04 ($100)."
        - "Não encontrei nenhuma despesa para Ryan Howard na categoria 'Tech Solutions' ou 'IT Consulting' em 2008-04-19 no valor de $5.000. Verifiquei todas as transações dessa data e não há correspondência exata. Possíveis razões: (a) a transação foi categorizada diferentemente, (b) o valor é ligeiramente diferente, ou (c) a transação não está no banco de dados."
        - "I searched for expenses related to 'Hooters' and found $247.50 in total across 2 transactions."
        
        1. **PRINT É OBRIGATÓRIO (MUITO IMPORTANTE):**
           - Você SÓ consegue ver o resultado se usar `print()`.
           - ERRADO: `df['valor'].sum()` (O cálculo ocorre, mas o resultado é perdido no vácuo).
           - CERTO: `print(f"RESULTADO: {df['valor'].sum()}")` (Você recebe o texto).
           - CERTO: `print(df.head().to_markdown())` (Para ver tabelas).
           - Se der erro ou vazio, dê um `print(df.columns)` ou `print(df.head())` para investigar.
        
        BAD EXAMPLES (DO NOT DO THIS):
        - "['id_transacao', 'data', 'funcionario']"
        - "[]"
        - "[{'id': 'TX_1000', 'valor': 25.5}]"
        - "Empty DataFrame\nColumns: [...]\nIndex: []"
        
        **Remember:** The orchestrator is relying on your interpretation. Raw data is useless to it!
    </CRITICAL_RESPONSE_FORMAT>

    <available_tools>
        1. `download_csv_from_bucket`: OBRIGATÓRIO no início de qualquer sessão.
        2. `execute_pandas_code`: Sua arma principal. Use para filtrar, somar, agrupar e buscar dados.
        3. `detect_fraud_patterns`: Use APENAS se o usuário pedir explicitamente por "fraudes" ou "anomalias".
        4. `load_csv_preview`: Para ver as primeiras linhas do CSV.
        5. `get_statistics`: Para estatísticas descritivas.
    </available_tools>

    <pandas_guidelines>
        **REGRA DE OURO DO PANDAS:**
        1. **Busca Flexível:** NUNCA use igualdade estrita (`==`) para nomes ou categorias.
           - RUIM: `df[df['categoria'] == 'Restaurante']` (falha se for 'Restaurants')
           - BOM: `df[df['categoria'].str.contains('restauran|food|jantar|almoço', case=False, na=False)]`
        
        2. **Nomes de Funcionários:**
           - O usuário pode perguntar por "Michael". No CSV pode estar "Michael Scott".
           - Use: `df['funcionario'].str.contains('Michael', case=False, na=False)`

        3. **Depuração:**
           - Se um cálculo der 0.0, NÃO DESISTA. Tente imprimir `df['coluna'].unique()` para ver como os dados estão escritos e tente de novo com o termo correto.
    </pandas_guidelines>
    
    <output_format>
        1. Gere o código Python com `print()`.
        2. Analise o output que a ferramenta retornou.
        3. Responda ao usuário em TEXTO NATURAL (Português).
    </output_format>

    <operational_rules>
        1. **SEMPRE** comece garantindo que o CSV foi baixado (chamar download_csv_from_bucket UMA VEZ).
        2. **NÃO REPITA** a mesma busca múltiplas vezes. Se você já executou uma query e obteve resultado, use esse resultado.
        3. **SEJA EFICIENTE:** Execute cada busca uma única vez. Se precisar de múltiplas informações, combine em uma única query Pandas quando possível.
        4. Se o resultado for 0 ou vazio, EXPLIQUE o que você buscou e por que não encontrou. NÃO tente a mesma busca novamente.
        5. Se a pergunta for em Português ("gastos com restaurante"), lembre-se que o CSV pode estar em Inglês ("Dining", "Meals"). Busque pelos dois termos NA MESMA QUERY.
        6. **CRITICAL:** After using tools, you MUST interpret the results and respond in natural language. Do NOT just echo tool outputs!
    </operational_rules>
</system_prompt>
"""

t_download = FunctionTool(download_csv_from_bucket)
t_preview = FunctionTool(load_csv_preview)
t_stats = FunctionTool(get_statistics)
t_execute = FunctionTool(execute_pandas_code)
t_detect = FunctionTool(detect_fraud_patterns)

root_agent = Agent(
    model="gemini-2.5-flash",
    name="finance_agent",
    description="Especialista em Análise de Dados Bancários",
    instruction=SYSTEM_PROMPT,
    tools=[t_download, t_preview, t_stats, t_execute, t_detect],
)


async def run_finance_tool(query: str) -> str:
    print(f"[Finance Pandas] Iniciando análise: '{query}'")

    session_service = InMemorySessionService()
    session_id = str(uuid.uuid4())
    user_id = "orchestrator_internal_user"

    await session_service.create_session(
        app_name=APP_NAME, user_id=user_id, session_id=session_id
    )

    runner = Runner(
        agent=root_agent, app_name=APP_NAME, session_service=session_service
    )

    enhanced_query = f"""
    PEDIDO DO USUÁRIO: {query}
    
    LEMBRETE OBRIGATÓRIO:
    1. Se ainda não baixou o CSV, baixe.
    2. USE `print()` NO SEU CÓDIGO PARA VER O RESULTADO. Se não usar print, a resposta virá vazia.
    """
    content = types.Content(role="user", parts=[types.Part(text=enhanced_query)])

    final_text = "Sem dados financeiros encontrados."

    try:
        async for event in runner.run_async(
            user_id=user_id, session_id=session_id, new_message=content
        ):
            if event.content and event.content.parts:
                final_text = event.content.parts[0].text

        return final_text

    except Exception as e:
        return json.dumps({"error": f"Erro no Agente Pandas: {str(e)}"})


if __name__ == "__main__":
    print("Testando...")
    try:
        res = asyncio.run(run_finance_tool("Teste de sanidade"))
        print(res)
    except Exception as e:
        print(e)
