import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { Building2, Bot, LineChart, Mail, Scale, User } from 'lucide-react';
import { motion } from 'framer-motion';
import logoImg from '../assets/dm-logo.png'; // Certifique-se de ter essa imagem

const SidebarItem = ({ to, icon: Icon, label }) => {
  const location = useLocation();
  const isActive = location.pathname === to;

  return (
    <NavLink to={to} className="block">
      <motion.div 
        className={`flex items-center px-4 py-3 my-1 mx-2 rounded-md transition-colors border-l-4 ${
          isActive 
            ? 'bg-dm-gray border-dm-black font-bold' 
            : 'hover:bg-gray-100 border-transparent'
        }`}
        whileHover={{ x: 5 }}
      >
        <Icon size={20} className={`mr-3 ${isActive ? 'text-dm-black' : 'text-dm-darkgray'}`} />
        <span className="font-office text-sm uppercase tracking-wider">{label}</span>
      </motion.div>
    </NavLink>
  );
};

const Sidebar = () => {
  return (
    <div className="w-72 h-screen bg-white border-r-2 border-dm-black flex flex-col shadow-xl z-10 overflow-y-auto">
      <div className="p-6 border-b-2 border-dm-black text-center">
        <img src={logoImg} alt="Dunder Mifflin Logo" className="w-40 mx-auto mb-2 filter contrast-125" />
        <p className="text-xs font-office uppercase text-dm-darkgray mt-2">Limitless Paper in a Paperless World</p>
      </div>
      
      <nav className="flex-1 py-6 overflow-y-auto">
        <SidebarItem to="/" icon={Building2} label="Sobre a Dunder Mifflin" />
        
        <div className="my-4 border-t border-gray-200 mx-4"></div>
        <h3 className="px-6 mb-2 text-xs font-bold text-dm-darkgray uppercase">Sistemas Centrais</h3>
        <SidebarItem to="/orchestrator" icon={Bot} label="Converse com DunderAI" />
        
        <div className="my-4 border-t border-gray-200 mx-4"></div>
        <h3 className="px-6 mb-2 text-xs font-bold text-dm-darkgray uppercase">Departamentos</h3>
        <SidebarItem to="/finance" icon={LineChart} label="Dunder AI Financeiro" />
        <SidebarItem to="/emails" icon={Mail} label="Dunder AI Emails" />
        <SidebarItem to="/compliance" icon={Scale} label="Dunder AI Compliance" />
        
        <div className="my-4 border-t border-dm-black mx-4"></div>
        <SidebarItem to="/michael" icon={User} label="Converse com o Michael" />
      </nav>

      <div className="p-4 border-t-2 border-dm-black text-center text-xs font-office text-dm-darkgray">
        © {new Date().getFullYear()} Dunder Mifflin Inc.<br/>Scranton Branch
      </div>
    </div>
  );
};

export default Sidebar;