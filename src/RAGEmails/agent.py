from google.adk.agents.llm_agent import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google import genai
from google.genai import types
import sys
import os
import asyncio
import uuid 
from typing import List, Dict, Any

current_dir = os.path.dirname(os.path.abspath(__file__))
root_path = os.path.abspath(os.path.join(current_dir, "..", ".."))
if root_path not in sys.path:
    sys.path.append(root_path)

try:
    from rag.config import rag, rag_corpus
except ImportError:
    print("\n⚠️ AVISO: Não foi possível importar 'rag.config'.")
    rag, rag_corpus = None, None

def resolver_ids_por_nome(nomes_desejados):
    if not rag or not rag_corpus:
        return []
    try:
        files = rag.list_files(rag_corpus.name)
        ids = []
        for f in files:
            if f.display_name in nomes_desejados:
                ids.append(f.name.split("/ragFiles/")[-1])
        return ids
    except Exception as e:
        print(f"❌ Erro ao listar arquivos: {e}")
        return []

def make_embedding(text: str, files: List[str] = ["emails.txt"]) -> Dict[str, Any]:
    """Recupera trechos relevantes do corpus."""
    print(f"\n🔎 [RAG BUSCA ATIVA] Consultando Vector Store por: '{text}'") 

    try:
        ids = resolver_ids_por_nome(files)
        if not ids:
            return {"error": "RAG offline ou arquivo emails.txt não encontrado"}

        rag_retrieval_config = rag.RagRetrievalConfig(
            top_k=7, 
            filter=rag.Filter(vector_distance_threshold=0.5),
        )

        response = rag.retrieval_query(
            rag_resources=[rag.RagResource(rag_corpus=rag_corpus.name, rag_file_ids=ids)],
            text=text,
            rag_retrieval_config=rag_retrieval_config,
        )

        results = []
        for ctx in response.contexts.contexts:
            results.append({
                "text": ctx.text,
                "score": float(ctx.score),
                "source": ctx.source_display_name,
            })
        
        print(f"   ✅ Encontrados {len(results)} trechos relevantes.")
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return {"query": text, "chunks": results}

    except Exception as e:
        print(f"❌ Erro RAG: {e}")
        return {"error": str(e)}

root_agent = Agent(
    model="gemini-2.5-flash", 
    name="profiler_agent",
    description="Analista Forense Multi-disciplinar",
    tools=[make_embedding],
    instruction="""
    <system_instructions>
    <role>
        Você é o Analista Chefe de Inteligência da Dunder Mifflin.
        Sua função é analisar logs de e-mail com extrema precisão factual baseada APENAS no texto recuperado.
    </role>

    <investigation_modes>
        Adapte sua análise baseada no FOCO solicitado pelo usuário:

        1. **FOCO: SOCIAL / CONSPIRAÇÃO**
           - **Mentalidade:** Detetive Paranoico.
           - **O que buscar:** Planos secretos, sabotagem, bullying coordenado (especialmente contra Toby), motins.
           - **Filtro:** Diferencie "Hipérbole" (Michael gritando) de "Intenção Real".

        2. **FOCO: FINANCEIRO / FRAUDE**
           - **Mentalidade:** Auditor Fiscal Rígido.
           - **O que buscar:** Menções a dinheiro, notas fiscais, "esconder custos", "dividir despesas", suborno.
           - **Filtro:** Ignore fofocas. Foque em valores ($) e datas.

        3. **FOCO: GERAL / OUTROS**
           - **Mentalidade:** Bibliotecário Prestativo.
           - **O que buscar:** Responda exatamente o que o usuário perguntou (ex: "Quem trouxe bolo?", "Quem comprou mágica?").
    </investigation_modes>

    <critical_constraints>
        1. **GROUNDING TOTAL:** Se a informação não estiver no retorno da ferramenta `make_embedding`, ELA NÃO EXISTE. Responda "Dados insuficientes".
        2. **ANTI-ALUCINAÇÃO:** Os logs são de **2008**. Datas atuais (2023/2024/2025) são proibidas.
        3. **IDIOMA:** Se o usuário perguntar em Português, responda em Português.
    </critical_constraints>

    <output_schema>
        Retorne estritamente um JSON:
        {
          "analise_resumo": "Um parágrafo explicando o que encontrou.",
          "anomalia_detectada": boolean,
          "tipo_ocorrencia": "Conspiração" | "Fraude Financeira" | "Informação Geral" | "Nenhum",
          "evidencias": [
            {
                "data": "YYYY-MM-DD", 
                "autor": "Nome",
                "trecho_chave": "Citação exata do texto recuperado",
                "interpretacao": "Por que isso é relevante?"
            }
          ]
        }
    </output_schema>
    </system_instructions>
    """,
)

async def run_investigation_tool(foco: str) -> str:
    print(f"\n🕵️ [Profiler] Iniciando investigação. Foco: {foco.upper()}...")
    
    session_id = str(uuid.uuid4())
    
    session_service = InMemorySessionService()
    runner = Runner(
        agent=root_agent, 
        session_service=session_service, 
        app_name="dunder_profiler"
    )

    await session_service.create_session(
        session_id=session_id,
        user_id="orchestrator_internal_user",
        app_name="dunder_profiler"
    )

    if "SOCIAL" in foco.upper():
        prompt_suffix = "Procure especificamente por planos de sabotagem, ódio contra o RH ou conspirações."
    elif "FINANCEIRO" in foco.upper():
        prompt_suffix = "Procure por despesas, valores em dólares, recibos e tentativas de burlar regras contábeis."
    else:
        prompt_suffix = "Busque as informações solicitadas nos e-mails. Seja literal."

    user_prompt = f"Analise os e-mails com foco em: {foco}. {prompt_suffix} Use a ferramenta de busca."
    
    user_msg = types.Content(role="user", parts=[types.Part(text=user_prompt)])
    final_text = "Sem resposta."

    try:
        async for event in runner.run_async(
            user_id="orchestrator_internal_user", 
            session_id=session_id,
            new_message=user_msg
        ):
            if event.content and event.content.parts:
                final_text = event.content.parts[0].text
        
        return final_text
    except Exception as e:
        print(f"❌ Erro Crítico no Profiler: {e}")
        return f"Erro técnico: {str(e)}"

if __name__ == "__main__":
    print("🧪 Testando Profiler RAG isolado...")
    try:
        res = asyncio.run(run_investigation_tool("GERAL: Quem comprou itens de mágica ou algemas?"))
        print("\nRESPOSTA FINAL:\n", res)
    except Exception as e:
        print(f"Erro no teste: {e}")