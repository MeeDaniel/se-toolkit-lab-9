import React, { useState } from 'react';
import './TelegramLogin.css';

function TelegramLogin({ onLogin }) {
  const [telegramAlias, setTelegramAlias] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!telegramAlias.trim()) {
      setError('Please enter your Telegram username');
      return;
    }
    
    if (telegramAlias.length < 3) {
      setError('Username must be at least 3 characters');
      return;
    }
    
    // Remove @ if present
    const cleanAlias = telegramAlias.replace(/^@/, '');
    onLogin(cleanAlias);
  };

  return (
    <div className="telegram-login">
      <div className="login-card">
        <div className="login-header">
          <div className="telegram-icon">
            <svg viewBox="0 0 24 24" width="64" height="64">
              <path fill="#2AABEE" d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.53 8.09l-1.77 8.33c-.13.6-.5.74-.99.46l-2.74-2.02-1.32 1.27c-.15.15-.27.27-.55.27l.2-2.78 5.07-4.58c.22-.2-.05-.3-.34-.12l-6.27 3.95-2.7-.84c-.59-.19-.6-.59.12-.87l10.55-4.07c.49-.18.92.12.74.87z"/>
            </svg>
          </div>
          <h1>TourStats</h1>
          <p className="subtitle">AI-Powered Analytics for Tour Guides</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="telegram">Enter your Telegram username:</label>
            <input
              type="text"
              id="telegram"
              value={telegramAlias}
              onChange={(e) => {
                setTelegramAlias(e.target.value);
                setError('');
              }}
              placeholder="@username or username"
              className="input-field"
              autoFocus
            />
            {error && <div className="error-message">{error}</div>}
          </div>

          <button type="submit" className="login-button">
            Continue to TourStats →
          </button>

          <div className="info-box">
            <p>💡 <strong>Note:</strong> This web app mirrors the Telegram bot experience. Your data will be associated with this username.</p>
          </div>
        </form>
      </div>
    </div>
  );
}

export default TelegramLogin;
