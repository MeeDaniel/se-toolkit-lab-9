import React, { useState, useEffect } from 'react';
import './App.css';
import Auth from './components/Auth';
import ChatInterface from './components/ChatInterface';
import StatisticsDashboard from './components/StatisticsDashboard';

function App() {
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState('chat');

  const handleLogin = (userData) => {
    setUser(userData);
    localStorage.setItem('hackathon_user', JSON.stringify(userData));
  };

  const handleLogout = () => {
    setUser(null);
    setActiveTab('chat');
    localStorage.removeItem('hackathon_user');
  };

  // Check for saved session on mount
  useEffect(() => {
    const savedUser = localStorage.getItem('hackathon_user');
    if (savedUser) {
      try {
        setUser(JSON.parse(savedUser));
      } catch (e) {
        localStorage.removeItem('hackathon_user');
      }
    }
  }, []);

  if (!user) {
    return <Auth onLogin={handleLogin} />;
  }

  return (
    <div className="App">
      <header className="app-header">
        <div className="header-content">
          <div>
            <h1>🎯 Tour Statistics Assistant</h1>
            <p className="subtitle">AI-Powered Analytics for Tour Guides</p>
          </div>
          <div className="user-info">
            <span className="user-badge">👤 {user.login}</span>
            <button className="logout-btn" onClick={handleLogout}>Logout</button>
          </div>
        </div>
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
        {/* Both pages exist simultaneously, only visibility changes */}
        <div className={`page-container ${activeTab === 'chat' ? 'page-visible' : 'page-hidden'}`}>
          <ChatInterface user={user} />
        </div>
        <div className={`page-container ${activeTab === 'statistics' ? 'page-visible' : 'page-hidden'}`}>
          <StatisticsDashboard user={user} refreshTrigger={activeTab === 'statistics'} />
        </div>
      </main>
    </div>
  );
}

export default App;
