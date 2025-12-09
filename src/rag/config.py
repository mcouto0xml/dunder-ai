from vertexai import rag
import vertexai


"""
    Murilo: Utilizei o código diretamente da documentação (fiz algumas alterações): 
    Guia de início rápido da RAG no Vertex AI
    https://docs.cloud.google.com/vertex-ai/generative-ai/docs/rag-engine/rag-quickstart?hl=pt-br#generativeaionvertexai_rag_quickstart-python_vertex_ai_sdk
"""
# Create a RAG Corpus, Import Files, and Generate a response

# TODO(developer): Update and un-comment below lines
PROJECT_ID = "dunderai"
display_name = "projects/dunderai/locations/us-west1/ragCorpora/4035225266123964416"

# Initialize Vertex AI API once per session
vertexai.init(project=PROJECT_ID, location="us-west1")

# Create RagCorpus
# Configure embedding model, for example "text-embedding-005".
embedding_model_config = rag.RagEmbeddingModelConfig(
    vertex_prediction_endpoint=rag.VertexPredictionEndpoint(
        publisher_model="publishers/google/models/text-embedding-005"
    )
)

rag_corpus = rag.get_corpus(display_name)