import { useState, useCallback } from 'react';
import { sendMessage } from '../services/api';

export const useChat = () => {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hello! I\'m your Polymarket assistant. Ask me anything about prediction markets, or provide a market ID for detailed analysis!',
      timestamp: new Date(),
    },
  ]);
  const [loading, setLoading] = useState(false);
  const [currentMarketId, setCurrentMarketId] = useState(null);

  const addMessage = useCallback((role, content) => {
    const newMessage = {
      role,
      content,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, newMessage]);
    return newMessage;
  }, []);

  const sendChatMessage = useCallback(async (userInput, marketId = null) => {
    if (!userInput.trim() || loading) return null;

    // Add user message
    addMessage('user', userInput.trim());
    setLoading(true);

    try {
      // Call backend API
      const response = await sendMessage(userInput.trim(), marketId);

      // Handle different response types
      if (response.type === 'chat') {
        // Simple chat response
        addMessage('assistant', response.response);
        return { type: 'chat', data: response.response };
      } else if (response.type === 'dashboard') {
        // Dashboard response
        addMessage('assistant', 'Here\'s the market analysis dashboard:');
        return { type: 'dashboard', data: response.data };
      } else if (response.type === 'error') {
        // Error response
        addMessage('assistant', response.message);
        return { type: 'error', data: response.message };
      } else {
        // Unexpected response format
        addMessage('assistant', 'I received an unexpected response format. Please try again.');
        return { type: 'error', data: 'Unexpected response format' };
      }
    } catch (error) {
      console.error('Chat error:', error);
      addMessage('assistant', 'Sorry, I encountered an error. Please try again.');
      return { type: 'error', data: error.message };
    } finally {
      setLoading(false);
    }
  }, [loading, addMessage]);

  const clearChat = useCallback(() => {
    setMessages([
      {
        role: 'assistant',
        content: 'Hello! I\'m your Polymarket assistant. Ask me anything about prediction markets, or provide a market ID for detailed analysis!',
        timestamp: new Date(),
      },
    ]);
    setCurrentMarketId(null);
  }, []);

  return {
    messages,
    loading,
    currentMarketId,
    setCurrentMarketId,
    sendMessage: sendChatMessage,
    clearChat,
  };
};

export default useChat;