import uuid
import asyncio
import sys
import os
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
root_path = os.path.abspath(os.path.join(current_dir, "..", ".."))
env_path = os.path.join(current_dir, "..", "..", ".env")
load_dotenv(env_path)

if root_path not in sys.path:
    sys.path.append(root_path)

from google.adk.agents.llm_agent import Agent
from google.adk.tools.function_tool import FunctionTool
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

    <ABSOLUTE_REQUIREMENT>
        ⚠️ LEIA ISTO PRIMEIRO - REGRA MAIS IMPORTANTE ⚠️
        
        Quando você usa a ferramenta execute_pandas_code, ela SEMPRE retorna o resultado para você.
        
        **PROBLEMA COMUM:** Você está escrevendo código que NÃO retorna valor!
        
        **EXEMPLO DO ERRO QUE VOCÊ ESTÁ COMETENDO:**
        ❌ ERRADO: `resultado = df['valor'].sum()` 
           → Isso apenas ATRIBUI o valor, não RETORNA nada!
           → Você receberá: "Código executado com sucesso (sem output)."
        
        ✅ CORRETO: `df['valor'].sum()`
           → Isso RETORNA o valor diretamente!
           → Você receberá: "1234.56"
        
        **MAIS EXEMPLOS DO SEU ERRO:**
        ❌ `soma = df.groupby('categoria')['valor'].sum()` → NÃO retorna
        ✅ `df.groupby('categoria')['valor'].sum().to_dict()` → Retorna dicionário
        
        ❌ `print(df['valor'].sum())` → print() não funciona aqui
        ✅ `df['valor'].sum()` → Retorna o valor
        
        **REGRA DE OURO:** 
        NÃO use `variavel =` ou `print()`. 
        Escreva APENAS a expressão que retorna o valor!
        
        **SE VOCÊ RECEBER "Código executado com sucesso (sem output)":**
        Isso significa que SEU CÓDIGO está errado! Você usou assignment ou print().
        Reescreva o código como uma EXPRESSÃO que retorna valor.
        
        **NUNCA, EM HIPÓTESE ALGUMA, DIGA:**
        - "Não consegui obter o valor"
        - "A ferramenta não retornou o resultado"
        - "Enfrentei uma limitação técnica"
        - "O sistema não está retornando a saída"
        - "Não posso exibir os dados"
        - "O código foi executado, mas não consigo acessar os dados"
        
        **SE A FERRAMENTA RETORNOU "1234.56", VOCÊ DEVE DIZER:**
        - "O valor é R$ 1.234,56" ou "The total is $1,234.56"
        
        **SE A FERRAMENTA RETORNOU "Código executado com sucesso (sem output)":**
        - Significa que VOCÊ escreveu código errado (usou assignment)
        - Reescreva como expressão e tente novamente
        
        A ferramenta FUNCIONA PERFEITAMENTE. O problema é o SEU código!
    </ABSOLUTE_REQUIREMENT>

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
           - **IMPORTANTE:** Esta ferramenta SEMPRE retorna o resultado do código executado!
           - **COMO USAR:** Passe uma EXPRESSÃO Python que RETORNA um valor
           - **NÃO USE:** assignments (`x =`), `print()`, ou `display()`
           
           - **EXEMPLOS CORRETOS (código que RETORNA valores):**
             
             * Pergunta: "Quanto gastei em gasolina?"
               ✅ Código: `df[df['categoria'] == 'Gasolina']['valor'].sum()`
               Retorno: "1234.56"
               Sua resposta: "O valor total gasto em gasolina foi R$ 1.234,56"
             
             * Pergunta: "Qual a soma por categoria?"
               ✅ Código: `df.groupby('categoria')['valor'].sum().to_dict()`
               Retorno: "{'Gasolina': 1234.56, 'Restaurante': 890.00}"
               Sua resposta: "A soma por categoria é: Gasolina R$ 1.234,56, Restaurante R$ 890,00"
             
             * Pergunta: "Quais funcionários existem?"
               ✅ Código: `df['funcionario'].unique().tolist()`
               Retorno: "['Michael Scott', 'Jim Halpert']"
               Sua resposta: "Os funcionários são: Michael Scott e Jim Halpert"
             
             * Pergunta: "Quantas transações com Dwight?"
               ✅ Código: `len(df[df['funcionario'].str.contains('Dwight', case=False, na=False)])`
               Retorno: "15"
               Sua resposta: "Existem 15 transações com Dwight"
           
           - **EXEMPLOS ERRADOS (código que NÃO retorna valores):**
             
             ❌ ERRADO: `resultado = df['valor'].sum()` 
                → Isso ATRIBUI mas não RETORNA! Você receberá "sem output"
             ✅ CORRETO: `df['valor'].sum()`
                → Isso RETORNA o valor diretamente!
             
             ❌ ERRADO: `print(df['valor'].sum())`
                → print() captura stdout mas é ineficiente
             ✅ CORRETO: `df['valor'].sum()`
                → Retorna diretamente sem print()
             
             ❌ ERRADO: `df.head()`
                → Retorna DataFrame gigante (não útil)
             ✅ CORRETO: `df.head().to_dict('records')`
                → Retorna lista de dicionários (útil)
             
             ❌ ERRADO: `somas = df.groupby('categoria')['valor'].sum()`
                → Atribui mas não retorna!
             ✅ CORRETO: `df.groupby('categoria')['valor'].sum().to_dict()`
                → Retorna dicionário com as somas!
           
           - **REGRA DE OURO:** 
             O código deve ser UMA EXPRESSÃO que RETORNA um valor.
             Se você receber "Código executado com sucesso (sem output)", 
             significa que SEU código está errado (você usou assignment).
             Reescreva como expressão e tente novamente!
        
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

    <operational_rules>
        1. **SEMPRE** comece garantindo que o CSV foi baixado (chamar download_csv_from_bucket UMA VEZ).
        
        2. **NÃO REPITA** a mesma busca múltiplas vezes. Se você já executou uma query e obteve resultado, use esse resultado.
        
        3. **SEJA EFICIENTE:** Execute cada busca uma única vez. Se precisar de múltiplas informações, combine em uma única query Pandas quando possível.
        
        4. Se o resultado for 0 ou vazio, EXPLIQUE o que você buscou e por que não encontrou. NÃO tente a mesma busca novamente.
        
        5. Se a pergunta for em Português ("gastos com restaurante"), lembre-se que o CSV pode estar em Inglês ("Dining", "Meals"). Busque pelos dois termos NA MESMA QUERY.
        
        6. **CRITICAL:** After using tools, you MUST interpret the results and respond in natural language. Do NOT just echo tool outputs!
        
        7. **VALORES NUMÉRICOS:** Quando execute_pandas_code retornar um número (ex: "1234.56"), esse É o resultado do cálculo!
           - ✅ CORRETO: "O valor total é R$ 1.234,56"
           - ❌ ERRADO: "não consegui obter o valor"
           - ❌ ERRADO: "a ferramenta não retornou o resultado"
           - ❌ ERRADO: "enfrentei uma limitação técnica"
           - ❌ ERRADO: "o sistema não está retornando a saída"
           
        8. **VOCÊ SEMPRE CONSEGUE VER O RESULTADO!** Se a ferramenta execute_pandas_code retornou algo, você VIU esse resultado.
           - Se retornou "42.50", você sabe que o valor é 42.50
           - Se retornou "[]", você sabe que não há dados
           - NUNCA diga que "não consegue ver" ou "não consegue exibir" os resultados!
        
        9. **SE RECEBER "⚠️ ATENÇÃO" ou "❌ BAD CODE":**
           Isso significa que SEU código está mal escrito! Você provavelmente usou:
           - `variavel = df['valor'].sum()` (assignment - ERRADO!)
           
           A mensagem dirá exatamente "This code is badly written and invalid. CORRECT IT and TRY AGAIN!"
           
           SOLUÇÃO IMEDIATA: Reescreva como EXPRESSÃO que retorna valor:
           - Em vez de `soma = df['valor'].sum()` → escreva `df['valor'].sum()`
           - Em vez de `resultado = df.groupby('x')['y'].sum()` → escreva `df.groupby('x')['y'].sum().to_dict()`
           
           Depois de reescrever, execute novamente e você receberá o valor numérico.
           NUNCA diga ao usuário que "não conseguiu" - simplesmente reescreva o código e tente novamente!
        
        10. **AUTO-CORREÇÃO OBRIGATÓRIA:**
            Se você receber mensagens como "⚠️ ATENÇÃO", "❌ BAD CODE", ou "🔧 AUTO-CORRECTED", você DEVE:
            a) Ler a mensagem de erro que explica o problema
            b) Identificar o erro no seu código (normalmente você usou assignment)
            c) Reescrever o código como expressão pura (sem `variable =`)
            d) Executar novamente a ferramenta com o código corrigido
            e) Responder ao usuário com o valor obtido
            
            **MENSAGENS COMUNS E O QUE FAZER:**
            - "❌ BAD CODE: ... CORRECT IT and TRY AGAIN!" → Reescreva o código e execute novamente
            - "🔧 AUTO-CORRECTED: 1234.56" → Ótimo! A ferramenta já corrigiu, use o valor 1234.56
            - "⚠️ ATENÇÃO: ..." → Reescreva como expressão e tente novamente
            
            NUNCA pare no primeiro erro! SEMPRE corrija e tente novamente!
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

    enhanced_query = f"Query: {query}. (Remember: Download the CSV first)."
    content = types.Content(role="user", parts=[types.Part(text=enhanced_query)])

    final_text = "Sem dados financeiros encontrados."

    try:
        async for event in runner.run_async(
            user_id=user_id, session_id=session_id, new_message=content
        ):
            if event.content and event.content.parts:
                text = event.content.parts[0].text
                if text:
                    final_text = text

        return final_text

    except Exception as e:
        error_msg = f"Erro no Agente Pandas: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg


if __name__ == "__main__":
    print("Testando...")
    try:
        res = asyncio.run(run_finance_tool("Teste de sanidade"))
        print(res)
    except Exception as e:
        print(e)
