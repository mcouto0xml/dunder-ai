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
        detect_fraud_patterns
    )
except ImportError as e:
    try:
        from tools import (
            download_csv_from_bucket,
            load_csv_preview,
            get_statistics,
            execute_pandas_code,
            detect_fraud_patterns
        )
    except ImportError as e2:
        print("\n\n" + "="*50)
        print("❌ ERRO CRÍTICO DE IMPORTAÇÃO")
        print(f"Não foi possível encontrar o arquivo 'tools.py' na pasta {current_dir}")
        print("Certifique-se de que você criou o arquivo 'src/agentPandas/tools.py'!")
        print("="*50 + "\n\n")
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
    </role>

    <available_tools>
        1. `download_csv_from_bucket`: OBRIGATÓRIO no início de qualquer sessão.
        2. `execute_pandas_code`: Sua arma principal. Use para filtrar, somar, agrupar e buscar dados.
        3. `detect_fraud_patterns`: Use APENAS se o usuário pedir explicitamente por "fraudes" ou "anomalias".
    </available_tools>

    <pandas_guidelines>
        **REGRA DE OURO DO PANDAS:**
        1. **Busca Flexível:** NUNCA use igualdade estrita (`==`) para nomes ou categorias.
           - ❌ `df[df['categoria'] == 'Restaurante']` (Ruim, falha se for 'Restaurants')
           - ✅ `df[df['categoria'].str.contains('restauran|food|jantar|almoço', case=False, na=False)]` (Bom!)
        
        2. **Nomes de Funcionários:**
           - O usuário pode perguntar por "Michael". No CSV pode estar "Michael Scott".
           - Use: `df['funcionario'].str.contains('Michael', case=False, na=False)`

        3. **Depuração:**
           - Se um cálculo der 0.0, NÃO DESISTA. Tente imprimir `df['coluna'].unique()` para ver como os dados estão escritos e tente de novo com o termo correto.
    </pandas_guidelines>

    <operational_rules>
        1. **SEMPRE** comece garantindo que o CSV foi baixado.
        2. Se o resultado for 0, reporte "O valor encontrado foi 0". Não diga "não consegui acessar".
        3. Se a pergunta for em Português ("gastos com restaurante"), lembre-se que o CSV pode estar em Inglês ("Dining", "Meals"). Busque pelos dois termos.
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
    tools=[t_download, t_preview, t_stats, t_execute, t_detect] 
)

async def run_finance_tool(query: str) -> str:
    print(f"💰 [Finance Pandas] Iniciando análise: '{query}'")
    
    session_service = InMemorySessionService()
    session_id = str(uuid.uuid4())
    user_id = "orchestrator_internal_user"
    
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id
    )

    runner = Runner(
        agent=root_agent, 
        app_name=APP_NAME, 
        session_service=session_service
    )

    enhanced_query = f"Query: {query}. (Remember: Download the CSV first)."
    content = types.Content(role="user", parts=[types.Part(text=enhanced_query)])
    
    final_text = "Sem dados financeiros encontrados."

    try:
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content
        ):
            if event.content and event.content.parts:
                final_text = event.content.parts[0].text
        
        return final_text

    except Exception as e:
        return json.dumps({"error": f"Erro no Agente Pandas: {str(e)}"})

if __name__ == "__main__":
    print("🧪 Testando...")
    try:
        res = asyncio.run(run_finance_tool("Teste de sanidade"))
        print(res)
    except Exception as e:
        print(e)