import React from 'react';
import ChatInterface from '../components/ChatInterface';

const OrchestratorChat = () => {
  return (
    <div className="h-full">
      <h1 className="text-3xl font-office font-bold uppercase mb-6 pb-2 border-b-4 border-dm-black inline-block">
        Central DunderAI (Orquestrador)
      </h1>
      <p className="mb-6 font-office text-lg max-w-2xl">
        Este é o sistema central. Faça uma pergunta complexa e ele coordenará os departamentos financeiro, de e-mails e de compliance para te dar uma resposta completa.
      </p>
      <div className="h-[calc(100%-150px)]">
         <ChatInterface 
            title="Orquestrador Central" 
            endpoint="/api/orchestrator"
            placeholder="Ex: Verifique se há fraudes financeiras envolvendo o Oscar em 2008."
            initialMessage="Sistema DunderAI online. Estou pronto para coordenar a auditoria. Qual a sua solicitação?"
         />
      </div>
    </div>
  );
};

export default OrchestratorChat;