import React, { useState, useRef, useEffect } from 'react';
import { Send, User, Bot, PlayCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { motion, AnimatePresence } from 'framer-motion';

// URL base da sua API Flask rodando localmente
const API_BASE_URL = 'http://34.111.115.133';

const ChatInterface = ({ title, endpoint, personaImage, placeholder, initialMessage }) => {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: initialMessage || `Olá. Sou a interface ${title}. Como posso ajudar?` }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const audioRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Define o corpo da requisição baseado no endpoint
      let body = { message: input };
      
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      const data = await response.json();

      if (data.success) {
        let botContent = '';
        let audioSrc = null;

        // Tratamento especial para a rota do Michael (Áudio)
        if (data.audio_base64) {
          botContent = data.michael_text; // Mostra o texto (legenda)
          audioSrc = `data:audio/mp3;base64,${data.audio_base64}`;
          // Toca o áudio automaticamente
          if (audioRef.current) {
             audioRef.current.src = audioSrc;
             audioRef.current.play().catch(err => console.log("Autoplay bloqueado pelo browser:", err));
          }
        } 
        // Tratamento para respostas padrão (Orquestrador/Agentes)
        else if (data.response) {
            botContent = data.response;
        } else if (data.text) {
            botContent = data.text;
        }
        
        setMessages(prev => [...prev, { 
            role: 'assistant', 
            content: botContent,
            audio: audioSrc, // Guarda a referência do áudio se houver
            technicalData: data.technical_data // Guarda dados técnicos se houver
        }]);
      } else {
        throw new Error(data.error || "Erro desconhecido na API");
      }
    } catch (error) {
      setMessages(prev => [...prev, { role: 'assistant', content: `⚠️ Erro de comunicação: ${error.message}`, isError: true }]);
    } finally {
      setIsLoading(false);
    }
  };

  // Função para retocar o áudio se o usuário quiser
  const playAudio = (src) => {
    if (audioRef.current && src) {
        audioRef.current.src = src;
        audioRef.current.play();
    }
  };

  return (
    <div className="flex flex-col h-full bg-white border-2 border-dm-black shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
      {/* Player de áudio invisível para o Michael */}
      <audio ref={audioRef} className="hidden" />

      <div className="p-4 border-b-2 border-dm-black bg-dm-gray flex items-center">
        {personaImage ? (
           <img src={personaImage} alt="Persona" className="w-12 h-12 rounded-full border-2 border-black mr-4 object-cover filter grayscale contrast-125" />
        ) : (
           <div className="w-10 h-10 bg-dm-black text-white rounded-sm flex items-center justify-center mr-3">
             <Bot size={24} />
           </div>
        )}
        <h2 className="text-xl font-office font-bold uppercase tracking-wider">{title}</h2>
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-stone-50">
        {messages.map((msg, index) => (
          <motion.div 
            key={index} 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div className={`flex items-start max-w-[80%] ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
              <div className={`flex-shrink-0 w-8 h-8 rounded-sm flex items-center justify-center border-2 border-black ${msg.role === 'user' ? 'bg-dm-black text-white ml-3' : 'bg-white text-black mr-3'}`}>
                {msg.role === 'user' ? <User size={18} /> : (personaImage ? <Bot size={18} /> : <Bot size={18} />)}
              </div>
              
              <div className={`p-4 border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,0.2)] ${msg.role === 'user' ? 'bg-dm-black text-white' : 'bg-white text-black'} ${msg.isError ? 'border-red-500 bg-red-50' : ''}`}>
                {/* Área de Conteúdo Principal */}
                <div className="prose prose-sm font-office leading-relaxed max-w-none">
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                </div>

                {/* Botão de Replay de Áudio (para o Michael) */}
                {msg.audio && (
                    <button 
                        onClick={() => playAudio(msg.audio)}
                        className="mt-3 flex items-center gap-2 text-xs uppercase font-bold border-2 border-black px-2 py-1 hover:bg-gray-200 transition-colors"
                    >
                        <PlayCircle size={16} /> Replay Áudio
                    </button>
                )}

                 {/* Área de Dados Técnicos (Expansível - Opcional) */}
                {msg.technicalData && (
                    <details className="mt-3 border-t-2 border-dashed border-gray-400 pt-2">
                        <summary className="text-xs cursor-pointer font-bold uppercase hover:underline">Ver Relatório Técnico (Confidencial)</summary>
                        <pre className="text-xs mt-2 bg-gray-100 p-2 border border-gray-300 overflow-x-auto font-mono">
                            {msg.technicalData}
                        </pre>
                    </details>
                )}
              </div>
            </div>
          </motion.div>
        ))}
        
        {isLoading && (
           <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex justify-start">
             <div className="bg-white border-2 border-black p-3 flex items-center shadow-[4px_4px_0px_0px_rgba(0,0,0,0.2)] ml-11">
               <div className="flex space-x-2 animate-pulse">
                 <div className="w-2 h-2 bg-dm-black rounded-full"></div>
                 <div className="w-2 h-2 bg-dm-black rounded-full"></div>
                 <div className="w-2 h-2 bg-dm-black rounded-full"></div>
               </div>
               <span className="ml-3 font-office text-xs uppercase">Processando requisição...</span>
             </div>
           </motion.div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSend} className="p-4 bg-white border-t-2 border-dm-black flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={placeholder || "Digite sua mensagem para o sistema..."}
          disabled={isLoading}
          className="flex-1 p-3 border-2 border-dm-black font-office focus:outline-none focus:ring-2 focus:ring-dm-darkgray focus:border-transparent placeholder-gray-500 bg-gray-50"
        />
        <button 
          type="submit" 
          disabled={isLoading || !input.trim()}
          className="bg-dm-black text-white p-3 border-2 border-dm-black hover:bg-white hover:text-dm-black transition-all disabled:opacity-50 disabled:cursor-not-allowed active:transform active:translate-y-1 shadow-[4px_4px_0px_0px_rgba(0,0,0,0.5)] hover:shadow-none"
        >
          <Send size={20} />
        </button>
      </form>
    </div>
  );
};

export default ChatInterface;