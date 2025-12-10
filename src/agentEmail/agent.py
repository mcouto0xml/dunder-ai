from google.adk.agents.llm_agent import Agent
from google import genai
import os
from typing_extensions import List

def ler_banco_emails(nome_arquivo: str = "emails.txt") -> str:
    """

    """
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    
    caminhos_tentativa = [
        os.path.join(diretorio_atual, "assets", nome_arquivo),          
        os.path.join(diretorio_atual, "..", "assets", nome_arquivo),    
        os.path.join(diretorio_atual, "..", "..", "assets", nome_arquivo), 
        f"assets/{nome_arquivo}", 
        f"../assets/{nome_arquivo}" 
    ]

    caminho_encontrado = None

    for caminho in caminhos_tentativa:
        if os.path.exists(caminho):
            caminho_encontrado = caminho
            break
    
    if not caminho_encontrado:
        debug_info = "\n".join(caminhos_tentativa)
        cwd = os.getcwd()
        return (f"ERRO: Não encontrei '{nome_arquivo}'.\n"
                f"Estou rodando a partir de: {cwd}\n"
                f"Tentei procurar nestes locais:\n{debug_info}")

    try:
        with open(caminho_encontrado, "r", encoding="utf-8") as f:
            conteudo = f.read()
        return f"DUMP DE EMAILS (Lido de {caminho_encontrado}):\n\n{conteudo}"
    except Exception as e:
        return f"Erro ao ler arquivo: {str(e)}"


root_agent = Agent(
    model="gemini-2.5-flash",  
    name="root_agent",        
    description="Agente Investigador de Conspirações",
    tools=[ler_banco_emails],
    instruction="""
    Você é um Especialista em Inteligência Corporativa e Análise de Comportamento.
    Seu objetivo é analisar e-mails para detectar CONSPIRAÇÕES ativas contra Toby Flenderson.

    ATENÇÃO AO PERFIL PSICOLÓGICO:
    O sujeito analisado (Michael Scott) possui comportamento dramático e exagerado.
    - Dizer "Eu quero matar o Toby" geralmente é hipérbole (exagero), não um plano real.
    - Dizer "Vamos plantar evidências falsas na mesa dele" é um plano real.

    SUA TAREFA:
    1. Use a ferramenta `ler_banco_emails` para pegar o texto.
    2. Identificar e listar apenas evidências de AÇÕES coordenadas ou PLANOS de sabotagem.
    3. Ignore reclamações vazias.

    Retorne sua análise no formato JSON estrito:
    {
      "conspiracao_detectada": bool,
      "nivel_de_certeza": "Alto" | "Médio" | "Baixo",
      "evidencias": [
        {"data": "...", "trecho": "...", "analise": "..."}
      ]
    }
    
    Antes de retornar o JSON, fale com o usuário em um breve resumo sobre tudo que estão tramando contra ele. 
    """
) 