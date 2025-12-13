import React from 'react';
import { motion } from 'framer-motion';

const About = () => {
  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-4xl font-office font-bold uppercase mb-8 pb-4 border-b-4 border-dm-black inline-block">
        Sobre a Dunder Mifflin
      </h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center mb-12">
        <motion.div 
          initial={{ x: -50, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="prose prose-lg font-office"
        >
          <p className="text-xl font-bold mb-4">
            "Pessoas compram de pessoas."
          </p>
          <p>
            Fundada em 1949 por Robert Dunder e Robert Mifflin, a Dunder Mifflin Inc. começou como uma fornecedora de suportes metálicos para construção civil. No entanto, a verdadeira paixão dos fundadores sempre foi o papel.
          </p>
          <p>
            Hoje, somos uma empresa de médio porte fornecedora de papel regional com orgulho, sediada no nordeste dos Estados Unidos. Nossa filial de Scranton, PA, sob a gerência regional (muitas vezes questionável) de Michael Scott, consistentemente supera as expectativas, provando que o toque humano ainda importa num mundo cada vez mais digital.
          </p>
        </motion.div>
        <motion.div
          initial={{ x: 50, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ delay: 0.4 }}
        >
          <img 
            src="https://upload.wikimedia.org/wikipedia/commons/9/9c/Dunder_Mifflin%2C_Inc.svg" 
            alt="Dunder Mifflin Building HQ" 
            className="w-full border-4 border-dm-black shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] bg-white p-4"
          />
          <p className="text-center text-sm font-office mt-2 text-gray-600">Nossa sede corporativa em Nova York (Nós preferimos Scranton).</p>
        </motion.div>
      </div>

      <motion.div
          initial={{ y: 50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="bg-dm-gray border-2 border-dm-black p-6 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]"
      >
        <h2 className="text-2xl font-office font-bold uppercase mb-4">Nossa Missão</h2>
        <p className="font-office text-lg">
          Fornecer papel de qualidade superior para empresas locais, superando as grandes cadeias através de um serviço ao cliente inigualável, entrega rápida e, ocasionalmente, cestas de presentes com descontos questionáveis.
        </p>
      </motion.div>
    </div>
  );
};

export default About;