from rag.config import rag, rag_corpus
from typing import List, Dict, Any

def resolver_ids_por_nome(nomes_desejados):
    files = rag.list_files(rag_corpus.name)

    ids = []
    for f in files:
        if f.display_name in nomes_desejados:
            rag_file_id_curto = f.name.split("/ragFiles/")[-1]
            ids.append(f"{rag_file_id_curto}")

    if not ids:
        raise ValueError("Nenhum dos arquivos solicitados foi encontrado no corpus.")

    return ids


def make_embedding(text: str, files: List[str]) -> Dict[str, Any]:
    """
    Retrieve relevant compliance document chunks from the RAG corpus.

    Args:
        text: User query.

    Returns:
        Dict with retrieved chunks, relevance score and sources.
    """

    print("Segue aqui os arquivos selecionados para compliance: ", files)

    ids = resolver_ids_por_nome(files)

    rag_retrieval_config = rag.RagRetrievalConfig(
        top_k=3,  # Optional
        filter=rag.Filter(vector_distance_threshold=0.5),  # Optional
    )

    response = rag.retrieval_query(
        rag_resources=[
            rag.RagResource(
                rag_corpus=rag_corpus.name,
                # Optional: supply IDs from `rag.list_files()`.
                # rag_file_ids=["rag-file-1", "rag-file-2", ...],
                rag_file_ids=ids,
            )
        ],
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

    return {
        "query": text,
        "chunks": results
    }

# make_embedding("A política permite $400 em 'Outros'?", ["politica_compliance.txt"])