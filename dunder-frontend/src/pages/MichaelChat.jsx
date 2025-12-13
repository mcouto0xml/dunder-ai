import React from 'react';
import ChatInterface from '../components/ChatInterface';
import michaelImg from '../assets/michael.jpg'; // Sua foto do Michael

const MichaelChat = () => {
  return (
    <div className="h-full bg-stone-100 p-2 border-4 border-double border-dm-black">
      <div className="h-full border-2 border-dm-black bg-white p-4 shadow-inner">
        <h1 className="text-3xl font-office font-bold uppercase mb-2 text-center underline decoration-wavy">
            A Experiência Michael Scott
        </h1>
        <p className="mb-4 font-office text-center text-sm italic">
            "Eu sou Beyoncé, sempre." — M.G.S.
        </p>
        <div className="h-[calc(100%-100px)]">
            <ChatInterface 
                title="Gerente Regional Michael Scott" 
                endpoint="/api/michael/experience"
                personaImage={michaelImg}
                placeholder="Pergunte algo ao melhor chefe do mundo..."
                initialMessage="Olá! Bem-vindo à minha sala. Pode entrar. O que você quer? Seja rápido, tenho muitas reuniões... mentira, não tenho. Senta aí."
            />
        </div>
      </div>
    </div>
  );
};

export default MichaelChat;