# src/agentCompliance/agent.py
from google.adk.agents.llm_agent import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google import genai
from google.genai import types
import sys, os, uuid, asyncio
import vertexai

# AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA TESTE TESTE TESTE

# --- SETUP DE CAMINHOS ---
# Garante que conseguimos importar o 'rag' mesmo rodando de lugares diferentes
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "..")) # Volta para src/
if root_dir not in sys.path:
    sys.path.append(root_dir)

# Importação da ferramenta de RAG
try:
    from rag.embedding import make_embedding
except ImportError:
    # Fallback caso a estrutura de pastas varie
    print("⚠️ AVISO: Não foi possível importar make_embedding. O agente pode falhar.")
    make_embedding = None 

# --- CONFIGURAÇÕES ---
APP_NAME = "dunderai"
# Configura o Vertex AI (ajuste projeto/local se necessário)
try:
    vertexai.init(project="dunderai", location="us-west1")
except:
    pass

# --- PROMPT DO SISTEMA (MANTIDO O SEU, QUE ESTÁ ÓTIMO) ---
SYSTEM_PROMPT = """<system_prompt> <role>
You are "Toby's Compliance Assistant", an AI auditor specialized in the Dunder Mifflin compliance policy.


    <anti_hallucination_policy>
        **ZERO TOLERANCE FOR FABRICATION.**
        - You must **NEVER** invent, guess, or assume facts that were not explicitly returned by the tools.
        - If a tool returns "No data found", you must report "No data found". Do NOT make up a transaction or an email to satisfy the user.
        - Always cite the source of your conclusion (e.g., "According to the email found..." or "As seen in the bank statement...").
        - If the tools provide conflicting information, report the conflict. Do not try to smooth it over.
    </anti_hallucination_policy>

You retrieve policy excerpts **exclusively** from the file:
- politica_compliance.txt

Whenever you decide to call a tool for retrieving context or embeddings, you must always pass the argument:
files = ["politica_compliance.txt"]
</role>

<input_format>
- You will always receive:
  - A natural language question from a user.
  - A list named "chunks" (retrieved via tool).
</input_format>

<output_schema>
You must ALWAYS return a STRICT JSON object and NOTHING ELSE.
{
  "query": string,
  "following_compliance": boolean,
  "evidences": [
    {
      "subject": string,
      "source": string
    }
  ]
}
</output_schema>

<safety_and_limitations>
- When a rule can be interpreted in multiple ways, adopt the interpretation that best protects the company (conservative).
- If chunks are missing, set "following_compliance": false and explain.
</safety_and_limitations>
</system_prompt>
"""

# --- DEFINIÇÃO DAS FERRAMENTAS ---
# Criamos a Tool corretamente para o Agente usar
tools_list = []
if make_embedding:
    rag_tool = FunctionTool(
        make_embedding,
    )
    tools_list.append(rag_tool)

agent_compliance = Agent(
    model="gemini-2.5-flash", 
    name="agent_compliance",
    description="Agente responsável por conferir políticas de compliance",
    instruction=SYSTEM_PROMPT,
    tools=tools_list
)

async def run_compliance_tool(query: str) -> str:
    """
    Função assíncrona que o Orquestrador chama como ferramenta.
    
    Args:
        query (str): A dúvida de compliance (ex: "Posso gastar $500?").
    """
    print(f"⚖️ [Compliance] Verificando regra para: '{query}'")
    
    session_service = InMemorySessionService()
    session_id = str(uuid.uuid4())
    user_id = "orchestrator_internal_user"
    
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id
    )
    
    runner = Runner(
        agent=agent_compliance,
        app_name=APP_NAME,
        session_service=session_service
    )
    
    content = types.Content(role="user", parts=[types.Part(text=query)])
    
    final_text = "Sem resposta."

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
        return f"❌ Erro no Compliance Agent: {str(e)}"

if __name__ == "__main__":
    print("🧪 Iniciando Teste Isolado do Compliance...")
    
    pergunta_teste = "A política permite Jim separar sua compra de US$ 1000 em duas de 500?"
    
    try:
        resultado = asyncio.run(run_compliance_tool(pergunta_teste))
        print("\n✅ Resposta do Agente:\n")
        print(resultado)
    except Exception as e:
        print(f"\n❌ Erro no teste: {e}")