from google.adk.agents.llm_agent import Agent
from google.adk.runners import Runner
import asyncio
import sys
import os


current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

if parent_dir not in sys.path:
    sys.path.append(parent_dir)

try:
    from RAGEmails.agent import run_investigation_tool
    from agentCompliance.agent import run_compliance_tool
    
except ImportError as e:
    raise ImportError(f"❌ O Orquestrador não achou os agentes irmãos. Erro: {e}")

root_agent = Agent(
    model="gemini-2.5-flash",
    name="michael_orchestrator",
    description="Orquestrador Central",
    tools=[run_investigation_tool, run_compliance_tool
],
    
    instruction="""
    Você é o Gerente. 
    Para investigar e-mails, use a ferramenta `run_investigation_tool`. 
    Para entender se determinada ação está dentro do compliance, use o `run_compliance_tool`. 
    
    Sua função é entender quem deve ser utilizado e utilizá-los
    ...
    """
)