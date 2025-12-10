from google.adk.agents.llm_agent import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google import genai
from google.genai import types
import sys
import os
import asyncio
from typing import List, Dict, Any

current_dir = os.path.dirname(os.path.abspath(__file__))
root_path = os.path.abspath(os.path.join(current_dir, "..", "..")) 
if root_path not in sys.path:
    sys.path.append(root_path)

try:
    from rag.config import rag, rag_corpus
except ImportError:
    print("ERRO: Não foi possível importar 'rag.config'.")
    raise

def resolver_ids_por_nome(nomes_desejados):
    files = rag.list_files(rag_corpus.name)
    ids = []
    for f in files:
        if f.display_name in nomes_desejados:
            rag_file_id_curto = f.name.split("/ragFiles/")[-1]
            ids.append(f"{rag_file_id_curto}")

    if not ids:
        print(f"Aviso: Arquivos {nomes_desejados} não encontrados.")
        return [] 
    return ids

def make_embedding(text: str, files: List[str] = ["emails.txt"]) -> Dict[str, Any]:
    """Retrieve relevant compliance document chunks."""
    print("Segue aqui os arquivos selecionados para compliance: ", files)

    try:
        ids = resolver_ids_por_nome(files)
        
        if not ids:
            return {"query": text, "chunks": [], "error": "Arquivos não encontrados"}

        rag_retrieval_config = rag.RagRetrievalConfig(
            top_k=3,
            filter=rag.Filter(vector_distance_threshold=0.5),
        )

        response = rag.retrieval_query(
            rag_resources=[rag.RagResource(rag_corpus=rag_corpus.name, rag_file_ids=ids)],
            text=text,
            rag_retrieval_config=rag_retrieval_config,
        )

        results: List[Dict[str, Any]] = []
        for ctx in response.contexts.contexts:
            results.append({
                "text": ctx.text,
                "score": float(ctx.score),
                "source": ctx.source_display_name,
                "uri": ctx.source_uri,
            })

        results.sort(key=lambda x: x["score"], reverse=True)
        return {"query": text, "chunks": results}
    
    except Exception as e:
        return {"error": f"Erro na busca RAG: {str(e)}"}

root_agent = Agent(
    model="gemini-2.5-flash",
    name="root_agent",
    description="Agente Investigador de Conspirações",
    tools=[make_embedding],
    instruction="""
    <system_instructions>
    <role>
        You are a Senior Corporate Intelligence Analyst.
    </role>
    <language_rules>
        If user asks in Portuguese, output strings in Portuguese. Keep JSON keys in English.
    </language_rules>
    <operational_steps>
        1. DATA INGESTION: Use `make_embedding`.
        2. TRIAGE: Discard gossip.
        3. INTENT ANALYSIS: SOCIAL Risk (Plans vs Rants) vs FINANCIAL Risk.
        4. STRUCTURING: Return STRICT JSON.
    </operational_steps>
    <output_schema>
        Return STRICT JSON with 'investigation_type', 'anomaly_detected', 'evidence'.
    </output_schema>
    </system_instructions>
    """,
)


async def run_investigation_tool(foco: str) -> str:
    print(f"[Profiler RAG] Iniciando Runner com foco: {foco}...")
    
    session_service = InMemorySessionService()
    user_id = "orchestrator_internal_user"
    session_id = "session_rag_investigation"
    app_name = "dunderai" 
    
    await session_service.create_session(
        session_id=session_id,
        user_id=user_id,
        app_name=app_name 
    )
    
    runner = Runner(
        agent=root_agent, 
        session_service=session_service,
        app_name=app_name 
    )

    user_prompt = f"Analyze emails focusing on: {foco} Risk."
    user_msg = types.Content(role="user", parts=[types.Part(text=user_prompt)])
    
    final_text = "No response generated."

    try:
        async for event in runner.run_async(
            user_id=user_id, 
            session_id=session_id, 
            new_message=user_msg
        ):
            if event.content and event.content.parts:
                final_text = event.content.parts[0].text
        
        return final_text

    except Exception as e:
        return f"Erro no Profiler Agent: {str(e)}"

if __name__ == "__main__":
    print("🧪 Testando Profiler RAG isolado...")
    try:
        res = asyncio.run(run_investigation_tool("SOCIAL"))
        print("\nRESPOSTA FINAL:\n", res)
    except Exception as e:
        print(f"Erro no teste: {e}")