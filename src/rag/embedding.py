from config import rag, rag_corpus

def resolver_ids_por_nome(nomes_desejados):
    files = rag.list_files(rag_corpus.name)

    ids = []
    for f in files:
        if f.display_name in nomes_desejados:
            # ✅ Extrai somente o ID curto
            rag_file_id_curto = f.name.split("/ragFiles/")[-1]
            ids.append(f"{rag_file_id_curto}")

    if not ids:
        raise ValueError("Nenhum dos arquivos solicitados foi encontrado no corpus.")

    return ids


def make_embedding(text: str, files: list):
    print(rag_corpus.name)

    ids = resolver_ids_por_nome(files)

    i = 0
    print("Rodando a iteração sobre arquivos: ")
    for f in files:
        print(i)
        print("Arquivo:", f)
        i += 1

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
    print("Segue a resposta gerada pelo modelo: ", response)

make_embedding("Políticas de relacionamento amoroso", ["politica_compliance.txt"])