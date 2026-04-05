import React, { useState, useEffect } from 'react';
import './App.css';
import TelegramLogin from './components/TelegramLogin';
import ChatInterface from './components/ChatInterface';
import StatisticsDashboard from './components/StatisticsDashboard';

function App() {
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState('chat');

  // Load user from localStorage on mount
  useEffect(() => {
    const savedUser = localStorage.getItem('tourstats_user');
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
  }, []);

  const handleLogin = (telegramAlias) => {
    const userData = { telegram_alias: telegramAlias, id: null };
    setUser(userData);
    localStorage.setItem('tourstats_user', JSON.stringify(userData));
    
    // Register user with backend
    registerUser(telegramAlias);
  };

  const registerUser = async (telegramAlias) => {
    try {
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/users/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ telegram_alias: telegramAlias })
      });
      
      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
        localStorage.setItem('tourstats_user', JSON.stringify(userData));
      }
    } catch (error) {
      console.error('Error registering user:', error);
    }
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('tourstats_user');
  };

  if (!user) {
    return <TelegramLogin onLogin={handleLogin} />;
  }

  return (
    <div className="App">
      <header className="app-header">
        <div className="header-content">
          <div>
            <h1>🎯 TourStats</h1>
            <p className="subtitle">AI-Powered Analytics for Tour Guides</p>
          </div>
          <div className="user-info">
            <span className="user-badge">👤 @{user.telegram_alias}</span>
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
        {activeTab === 'chat' && <ChatInterface user={user} />}
        {activeTab === 'statistics' && <StatisticsDashboard user={user} />}
      </main>
    </div>
  );
}

export default App;
