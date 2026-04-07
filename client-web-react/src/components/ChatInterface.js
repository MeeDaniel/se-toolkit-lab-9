import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import './ChatInterface.css';

const WS_URL = process.env.REACT_APP_WS_URL || `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws`;
const ACCESS_KEY = process.env.REACT_APP_NANOBOT_ACCESS_KEY || 'changeme_nanobot_key_123';

function ChatInterface({ user }) {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const wsRef = useRef(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    connectWebSocket();
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const connectWebSocket = () => {
    const wsUrlWithKey = `${WS_URL}?access_key=${ACCESS_KEY}`;
    const ws = new WebSocket(wsUrlWithKey);
    
    ws.onopen = () => {
      console.log('WebSocket connected');
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('Received:', data);
      
      if (data.type === 'welcome') {
        // Don't add to messages, just log
      } else if (data.type === 'chat_response') {
        setMessages(prev => [...prev, { type: 'bot', message: data.message }]);
        setIsLoading(false);

        // If excursion was stored, create a system message
        if (data.excursion_stored) {
          setMessages(prev => [...prev, {
            type: 'system',
            message: '✅ Excursion data saved to your statistics!'
          }]);
        }

        // If excursion was updated, create a system message
        if (data.excursion_updated) {
          setMessages(prev => [...prev, {
            type: 'system',
            message: '📝 Excursion updated successfully!'
          }]);
        }

        // If excursion was deleted, create a system message
        if (data.excursion_deleted) {
          setMessages(prev => [...prev, {
            type: 'system',
            message: `🗑️ ${data.delete_message || 'Excursion deleted successfully!'}`
          }]);
        }
      } else if (data.type === 'error') {
        setMessages(prev => [...prev, { type: 'error', message: data.message }]);
        setIsLoading(false);
      }
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
      // Try to reconnect after 3 seconds
      setTimeout(connectWebSocket, 3000);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
    };

    wsRef.current = ws;
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    // Add user message
    setMessages(prev => [...prev, { type: 'user', message: inputMessage }]);
    setIsLoading(true);

    // Send via WebSocket
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'chat',
        message: inputMessage
      }));
    }

    setInputMessage('');
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <h2>AI Assistant</h2>
        <div className="connection-status">
          <span className={isConnected ? 'status-connected' : 'status-disconnected'}>
            {isConnected ? '● Connected' : '● Disconnected'}
          </span>
        </div>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="welcome-message">
            <h3>👋 Welcome to Tour Statistics Assistant!</h3>
            <p>Describe your completed excursion and I'll extract statistics automatically.</p>
            <p><strong>Example:</strong> "Just finished a tour with 15 people, mostly young adults around 25. They were really energetic and interested in robotics and AI."</p>
          </div>
        )}
        
        {messages.map((msg, idx) => (
          <div key={idx} className={`message message-${msg.type}`}>
            <div className="message-bubble">
              {msg.type === 'bot' ? (
                <ReactMarkdown>{msg.message}</ReactMarkdown>
              ) : (
                msg.message
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="message message-bot">
            <div className="message-bubble loading">
              <span className="dot"></span>
              <span className="dot"></span>
              <span className="dot"></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input">
        <textarea
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Describe your excursion or ask about statistics..."
          disabled={!isConnected || isLoading}
          rows="3"
        />
        <button 
          onClick={sendMessage}
          disabled={!isConnected || isLoading || !inputMessage.trim()}
        >
          Send
        </button>
      </div>

      <div className="chat-examples">
        <p className="examples-title">Example messages:</p>
        <div className="examples-list">
          <button onClick={() => setInputMessage("Just finished a tour with 15 people, mostly young adults around 25. They were really energetic and super interested in tech parts, especially robotics and AI.")}>
            "Just finished a tour with 15 people, mostly young adults around 25..."
          </button>
          <button onClick={() => setInputMessage("Had 20 tourists, average age 30. Very interested in education history, less in tech. Energy level was moderate.")}>
            "Had 20 tourists, average age 30..."
          </button>
        </div>
      </div>
    </div>
  );
}

export default ChatInterface;
