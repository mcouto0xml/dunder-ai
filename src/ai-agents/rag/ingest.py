from config import rag, rag_corpus

paths = ["gs://dunder-data/data/politica_compliance.txt"]


def make_ingest():
    # Import Files to the RagCorpus
    rag.import_files(
        rag_corpus.name,
        paths,
        # Optional
        transformation_config=rag.TransformationConfig(
            chunking_config=rag.ChunkingConfig(
                chunk_size=512,
                chunk_overlap=100,
            ),
        ),
        max_embedding_requests_per_min=1000,  # Optional
    )


make_ingest()