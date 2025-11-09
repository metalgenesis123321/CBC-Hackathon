// Format timestamp to readable time
export const formatTime = (timestamp) => {
  if (!timestamp) return '';
  return new Date(timestamp).toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
  });
};

// Format date
export const formatDate = (date) => {
  if (!date) return '';
  return new Date(date).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
};

// Format large numbers with K, M, B suffix
export const formatNumber = (num) => {
  if (!num) return '0';
  
  if (num >= 1000000000) {
    return `${(num / 1000000000).toFixed(1)}B`;
  }
  if (num >= 1000000) {
    return `${(num / 1000000).toFixed(1)}M`;
  }
  if (num >= 1000) {
    return `${(num / 1000).toFixed(1)}K`;
  }
  return num.toString();
};

// Format currency
export const formatCurrency = (amount, decimals = 2) => {
  if (!amount) return '$0';
  return `$${Number(amount).toLocaleString('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  })}`;
};

// Format percentage
export const formatPercentage = (value, decimals = 1) => {
  if (value === null || value === undefined) return '0%';
  return `${Number(value).toFixed(decimals)}%`;
};

// Copy text to clipboard
export const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (error) {
    console.error('Failed to copy:', error);
    return false;
  }
};

// Export conversation to text file
export const exportConversation = (messages) => {
  const conversationText = messages
    .map((msg) => {
      const role = msg.role === 'user' ? 'You' : 'Assistant';
      const time = formatTime(msg.timestamp);
      return `[${time}] ${role}:\n${msg.content}\n`;
    })
    .join('\n---\n\n');

  const blob = new Blob([conversationText], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `polysage-chat-${new Date().toISOString().slice(0, 10)}.txt`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};

// Constants
export const APP_NAME = 'PolySage';
export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
