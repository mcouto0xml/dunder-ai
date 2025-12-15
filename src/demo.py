# ARQUIVO: src/demo.py
import asyncio
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.orchestrator.agent import root_agent as toby_orchestrator
from src.utils.voice import root_agent as michael_persona
from src.utils.voice import falar_como_michael

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

async def main():
    print("\nDUNDER MIFFLIN AI: O SISTEMA DE AUDITORIA")
    print("(Fale 'sair' para encerrar)\n")
    
    session_service = InMemorySessionService()
    
    await session_service.create_session("sess_toby", "user_demo", "app_toby")
    toby_runner = Runner(agent=toby_orchestrator, session_service=session_service, app_name="app_toby")

    await session_service.create_session("sess_michael", "user_demo", "app_michael")
    michael_runner = Runner(agent=michael_persona, session_service=session_service, app_name="app_michael")

    while True:
        query = input("\n👤 PERGUNTA DO CHEFE: ")
        if query.lower() in ["sair", "exit"]: break
        
        print("\n⚙️  Rodando Auditoria (Agentes: Compliance, Finance, RAG)...")
        
        relatorio_tecnico = ""
        msg_toby = types.Content(role="user", parts=[types.Part(text=query)])
        
        async for event in toby_runner.run_async("user_demo", "sess_toby", msg_toby):
            if event.content and event.content.parts:
                relatorio_tecnico = event.content.parts[0].text
        
        print(f"\n📄 RELATÓRIO TÉCNICO:\n{relatorio_tecnico}")
        
        print("\n🎬 Michael Scott está lendo o relatório...")
        
        prompt_michael = f"Aqui está o relatório técnico chato do Toby. Reaja a ele com sua personalidade:\n\n'{relatorio_tecnico}'"
        msg_michael = types.Content(role="user", parts=[types.Part(text=prompt_michael)])
        
        texto_michael = ""
        async for event in michael_runner.run_async("user_demo", "sess_michael", msg_michael):
            if event.content and event.content.parts:
                texto_michael = event.content.parts[0].text
                
        print(f"\n👔 MICHAEL SCOTT DIZ:\n{texto_michael}")
        
        falar_como_michael(texto_michael)

if __name__ == "__main__":
    asyncio.run(main())