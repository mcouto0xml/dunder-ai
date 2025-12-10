from flask import Flask, request, jsonify
from embedding import make_embedding

app = Flask(__name__)

@app.post("/process-rag")
def process_rag():
    data = request.get_json(silent=True) or {}

    query = data.get("query")
    user_id = data.get("user_id")
    files = data.get("files")

    if not query or not files:
        return jsonify({"error": "tá faltando dados guerreiro..."}), 400
    
    print(f"[ragWorker] Recebido a query: {query} para os files: {files}, do user_id: {user_id}")

    answer = make_embedding(query, files)

    return jsonify(
        {
            "status": "ok",
            "user_id": user_id,
            "query": query,
            "answer": answer
        }
    ), 200