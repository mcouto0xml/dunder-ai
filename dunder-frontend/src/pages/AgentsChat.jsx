import React from 'react';
import ChatInterface from '../components/ChatInterface';
import { LineChart, Mail, Scale } from 'lucide-react';

const agentConfigs = {
    finance: {
        title: "Departamento Financeiro",
        endpoint: "/api/finance",
        description: "Acesso direto aos registros CSV bancários. Ideal para perguntas numéricas exatas.",
        icon: LineChart,
        placeholder: "Ex: Qual o total gasto pelo Michael em restaurantes?"
    },
    emails: {
        title: "Investigação de E-mails (Profiler)",
        endpoint: "/api/profiler",
        description: "Busca vetorial (RAG) no arquivo morto de e-mails de 2008.",
        icon: Mail,
        placeholder: "Ex: O que o Dwight falou sobre planos de segurança?"
    },
    compliance: {
        title: "Compliance & Regras",
        endpoint: "/api/compliance", 
        description: "Verificação de regras e políticas da empresa.",
        icon: Scale,
        placeholder: "Ex: É permitido gastar mais de $100 sem recibo?"
    }
};

const AgentsChat = ({ type }) => {
  const config = agentConfigs[type];
  const Icon = config.icon;

  if (!config) return <div>Agente não encontrado.</div>;

  return (
    <div className="h-full">
       <div className="flex items-center mb-6 pb-2 border-b-4 border-dm-black">
         <Icon size={32} className="mr-4" />
         <h1 className="text-3xl font-office font-bold uppercase">
            {config.title}
         </h1>
       </div>
      <p className="mb-6 font-office text-lg max-w-2xl">
        {config.description}
      </p>
      <div className="h-[calc(100%-150px)]">
         <ChatInterface 
            title={`Agente ${config.title}`}
            endpoint={config.endpoint}
            placeholder={config.placeholder}
         />
      </div>
    </div>
  );
};

export default AgentsChat;