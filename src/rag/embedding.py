from config import rag, rag_corpus


def make_embedding():
    print(rag_corpus.name)

    files = rag.list_files(rag_corpus.name)

    i = 0
    print("Rodando a iteração sobre arquivos: ")
    for f in files:
        print(i)
        print("Arquivo:", f.display_name, "| Status:")
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
            )
        ],
        text="Compra acima de US$ 500",
        rag_retrieval_config=rag_retrieval_config,
    )
    print("Segue a resposta gerada pelo modelo: ", response)

make_embedding()