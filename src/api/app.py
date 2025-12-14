import sys
import os
import asyncio
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flasgger import Swagger
from dotenv import load_dotenv
import io
import base64

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
sys.path.append(os.path.join(project_root, "src"))

load_dotenv(os.path.join(project_root, ".env"))

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google.adk.agents.llm_agent import Agent

try:
    from elevenlabs.client import ElevenLabs
    
    eleven_key = os.getenv("ELEVENLABS_API_KEY")
    if eleven_key:
        eleven_client = ElevenLabs(api_key=eleven_key)
        MICHAEL_VOICE_ID = os.getenv("MICHAEL_VOICE_ID", "ErXwobaYiN019PkySvjV") 
        print("🔊 ElevenLabs carregado com sucesso.")
    else:
        print("⚠️ Aviso: ELEVENLABS_API_KEY não encontrada no .env")
        eleven_client = None
except ImportError:
    print("⚠️ Aviso: Biblioteca 'elevenlabs' não instalada.")
    eleven_client = None
except Exception as e:
    print(f"⚠️ Aviso: Erro ao configurar ElevenLabs: {e}")
    eleven_client = None

try:
    from orchestrator.agent import agent as orchestrator_agent
except ImportError:
    try:
        from orchestrator.agent import root_agent as orchestrator_agent
    except:
        print("⚠️ Orquestrador não encontrado.")
        orchestrator_agent = None

try:
    from agentPandas.agent import root_agent as finance_agent
except ImportError:
    print("⚠️ Agente Financeiro não encontrado.")
    finance_agent = None

try:
    from RAGEmails.agent import root_agent as profiler_agent
except ImportError:
    print("⚠️ Agente Profiler não encontrado.")
    profiler_agent = None

try:
    from michael.agent import chat_with_michael
    transform_to_michael_script = True
except ImportError:
    print("⚠️ Agente Michael Persona não encontrado.")
    transform_to_michael_script = None
    chat_with_michael = None

try:
    from agentCompliance.agent import agent_compliance as compliance_agent
except ImportError:
    print("⚠️ Agente de Compliance não encontrado.")
    compliance_agent = None


app = Flask(__name__)

CORS(
    app,
    resources={r"/api/*": {"origins": "*"}},
    supports_credentials=False
)

app.config['SWAGGER'] = {
    'title': 'Dunder AI - The Office API',
    'uiversion': 3,
    'description': """
    API de Auditoria Forense da Dunder Mifflin.
    
    **Integrantes:**
    1. **Michael Scott Experience:** Chat direto com a persona e voz.
    2. **Orquestrador:** O cérebro lógico.
    3. **Especialistas:** Financeiro, Profiler (E-mails) e Compliance (Regras).
    """,
    'specs_route': '/docs'
}
swagger = Swagger(app)

async def run_agent_session(target_agent: Agent, user_query: str, session_prefix: str):
    if not target_agent:
        return "Erro: Agente solicitado não está carregado no servidor (verifique imports)."

    session_service = InMemorySessionService()
    session_id = f"session_{session_prefix}_{os.urandom(4).hex()}" 
    user_id = "frontend_user"
    app_name = f"dunder_{session_prefix}"

    await session_service.create_session(session_id=session_id, user_id=user_id, app_name=app_name)

    runner = Runner(agent=target_agent, session_service=session_service, app_name=app_name)
    
    user_msg = types.Content(role="user", parts=[types.Part(text=user_query)])
    final_response = ""

    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_msg):
        if event.content and event.content.parts:
            final_response = event.content.parts[0].text
            
    return final_response


@app.before_request
def allow_options():
    if request.method == "OPTIONS":
        return "", 200

@app.route('/health', methods=['GET'])
def health():
    """
    Verificar saúde do sistema
    ---
    tags:
      - System
    responses:
      200:
        description: Status dos serviços
    """
    return jsonify({
        "status": "online", 
        "tts_enabled": eleven_client is not None,
        "agents": {
            "orchestrator": orchestrator_agent is not None,
            "finance": finance_agent is not None,
            "profiler": profiler_agent is not None,
            "michael_persona": chat_with_michael is not None,
            "compliance": compliance_agent is not None
        }
    })

@app.route('/api/michael/experience', methods=['POST'])
async def michael_full_experience():
    """
    Michael Scott Chat (Texto + Áudio)
    ---
    tags:
      - ★ Main Experience
    description: Conversa direta com Michael Scott. Ele responde em texto (Inglês) e Áudio.
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Michael, o que você acha do Toby?"
    responses:
      200:
        description: Sucesso
    """
    if not eleven_client:
        return jsonify({"error": "ElevenLabs não configurado"}), 500

    data = request.get_json()
    user_query = data.get('message', '')

    try:
        print(f"🎤 [Michael] Usuário disse: {user_query}")
        
        if chat_with_michael:
            michael_response = await chat_with_michael(user_query)
        else:
            michael_response = "I am currently eating tiramisu. Leave a message."
            
        print(f"🎬 [Michael] Resposta: {michael_response}")

        print(f"🔊 [TTS] Gerando áudio...")
        
        audio_generator = eleven_client.text_to_speech.convert(
            text=michael_response,
            voice_id=MICHAEL_VOICE_ID,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128"
        )
        
        audio_bytes = b"".join(audio_generator)
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')

        return jsonify({
            "success": True,
            "technical_data": "Chat direto - Sem auditoria.", 
            "michael_text": michael_response,
            "audio_base64": audio_base64
        })

    except Exception as e:
        print(f"❌ Erro no fluxo: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/orchestrator', methods=['POST'])
async def chat_orchestrator():
    """
    Falar com o Orquestrador (Texto Puro)
    ---
    tags:
      - Agents
    description: Acessa a lógica central.
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Faça uma varredura por fraudes."
    responses:
      200:
        description: Resposta técnica
    """
    data = request.get_json()
    res = await run_agent_session(orchestrator_agent, data.get('message'), "orch")
    return jsonify({"success": True, "response": res})

@app.route('/api/finance', methods=['POST'])
async def chat_finance():
    """
    Falar com o Agente Financeiro (Pandas)
    ---
    tags:
      - Agents
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Total gasto em restaurantes?"
    responses:
      200:
        description: Resposta do analista de dados
    """
    data = request.get_json()
    res = await run_agent_session(finance_agent, data.get('message'), "finance")
    return jsonify({"success": True, "text": res})

@app.route('/api/profiler', methods=['POST'])
async def chat_profiler():
    """
    Falar com o Agente Profiler (E-mails)
    ---
    tags:
      - Agents
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            message:
              type: string
              example: "O que dizem sobre armas?"
    responses:
      200:
        description: Evidências encontradas
    """
    data = request.get_json()
    res = await run_agent_session(profiler_agent, data.get('message'), "profiler")
    return jsonify({"success": True, "text": res})

@app.route('/api/compliance', methods=['POST'])
async def chat_compliance():
    """
    Falar com o Agente de Compliance (Regras)
    ---
    tags:
      - Agents
    description: Verifica violações de regras baseadas no manual de política.
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Posso gastar $1000 sem recibo?"
    responses:
      200:
        description: Veredito de compliance (JSON)
    """
    data = request.get_json()
    res = await run_agent_session(compliance_agent, data.get('message'), "compliance")
    return jsonify({"success": True, "text": res})

@app.route('/api/speak', methods=['POST'])
def speak_michael_direct():
    """
    Gerador de Voz (TTS Direto)
    ---
    tags:
      - Utils
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            text:
              type: string
    responses:
      200:
        description: MP3
    """
    if not eleven_client: return jsonify({"error": "ElevenLabs off"}), 500
    data = request.get_json()
    text = data.get('text', '')
    
    try:
        audio_gen = eleven_client.text_to_speech.convert(
            text=text,
            voice_id=MICHAEL_VOICE_ID,
            model_id="eleven_multilingual_v2"
        )
        audio_bytes = b"".join(audio_gen)
        return send_file(io.BytesIO(audio_bytes), mimetype="audio/mpeg", download_name="michael.mp3")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Dunder AI API (Completa) rodando na porta 5000...")
    print("📄 Swagger disponível em: http://localhost:5000/docs")
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)