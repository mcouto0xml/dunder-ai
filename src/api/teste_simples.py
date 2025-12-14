from flask import Flask, jsonify
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app)

@app.route('/health')
def health():
    """
    Teste de vida
    ---
    responses:
      200:
        description: O servidor está vivo
    """
    return jsonify({"status": "vivo"})

if __name__ == "__main__":
    print("Teste rodando em http://localhost:5000/docs")
    app.run(debug=True)