import React from 'react';
import Sidebar from './Sidebar';
import { Outlet } from 'react-router-dom';
import { motion } from 'framer-motion';

const Layout = () => {
  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      <Sidebar />
      <main className="flex-1 overflow-auto relative">
        {/* Uma textura de papel sutil sobre o conteúdo */}
        <div className="absolute inset-0 pointer-events-none opacity-5 bg-[url('https://www.transparenttextures.com/patterns/old-map.png')]"></div>
        <motion.div 
          className="h-full p-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Outlet />
        </motion.div>
      </main>
    </div>
  );
};

export default Layout;