import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import About from './pages/About';
import OrchestratorChat from './pages/OrchestratorChat';
import AgentsChat from './pages/AgentsChat';
import MichaelChat from './pages/MichaelChat';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<About />} />
          <Route path="orchestrator" element={<OrchestratorChat />} />
          
          <Route path="finance" element={<AgentsChat type="finance" />} />
          <Route path="emails" element={<AgentsChat type="emails" />} />
          <Route path="compliance" element={<AgentsChat type="compliance" />} />
          
          <Route path="michael" element={<MichaelChat />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;