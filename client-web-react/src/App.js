import React, { useState, useEffect } from 'react';
import './App.css';
import ChatInterface from './components/ChatInterface';
import StatisticsDashboard from './components/StatisticsDashboard';

function App() {
  const [activeTab, setActiveTab] = useState('chat');

  return (
    <div className="App">
      <header className="app-header">
        <h1>🎯 TourStats</h1>
        <p className="subtitle">AI-Powered Analytics for Tour Guides</p>
      </header>

      <nav className="tab-navigation">
        <button 
          className={activeTab === 'chat' ? 'active' : ''} 
          onClick={() => setActiveTab('chat')}
        >
          💬 Chat
        </button>
        <button 
          className={activeTab === 'statistics' ? 'active' : ''} 
          onClick={() => setActiveTab('statistics')}
        >
          📊 Statistics
        </button>
      </nav>

      <main className="app-main">
        {activeTab === 'chat' && <ChatInterface />}
        {activeTab === 'statistics' && <StatisticsDashboard />}
      </main>
    </div>
  );
}

export default App;
