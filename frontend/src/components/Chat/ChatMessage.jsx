import React from 'react';
import { Bot, User, Copy, Volume2, Check } from 'lucide-react';
import { formatTime, copyToClipboard } from '../../utils';

const ChatMessage = ({ message, darkMode, onSpeak }) => {
  const [copied, setCopied] = React.useState(false);

  const handleCopy = async () => {
    const success = await copyToClipboard(message.content);
    if (success) {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div
      className={`flex gap-4 animate-in fade-in slide-in-from-bottom-4 duration-500 ${
        message.role === 'user' ? 'flex-row-reverse' : 'flex-row'
      }`}
    >
      {/* Avatar */}
      <div className="flex-shrink-0">
        <div
          className={`w-11 h-11 rounded-2xl flex items-center justify-center shadow-lg ${
            message.role === 'user'
              ? darkMode 
                ? 'bg-gradient-to-br from-emerald-600 to-teal-600 shadow-emerald-500/50' 
                : 'bg-gradient-to-br from-emerald-400 to-teal-400 shadow-emerald-300/50'
              : darkMode 
                ? 'bg-gradient-to-br from-blue-600 via-cyan-600 to-sky-700 shadow-blue-500/50' 
                : 'bg-gradient-to-br from-blue-400 via-cyan-400 to-sky-500 shadow-blue-300/50'
          } ${message.role === 'user' ? 'rotate-3' : '-rotate-3'}`}
        >
          {message.role === 'user' ? (
            <User className="w-6 h-6 text-white" />
          ) : (
            <Bot className="w-6 h-6 text-white" />
          )}
        </div>
      </div>

      {/* Message Content */}
      <div className="flex-1 max-w-3xl">
        <div className="group">
          <div className="flex items-start gap-3 mb-2">
            <span className={`text-sm font-semibold ${
              message.role === 'user' 
                ? darkMode ? 'text-emerald-400' : 'text-emerald-700' 
                : darkMode ? 'text-blue-400' : 'text-blue-700'
            }`}>
              {message.role === 'user' ? 'You' : 'PolySage'}
            </span>
            <span className={`text-xs ${
              darkMode ? 'text-gray-500' : 'text-gray-400'
            } mt-0.5`}>
              {formatTime(message.timestamp)}
            </span>
          </div>
          
          <div
            className={`relative px-6 py-4 rounded-2xl shadow-lg ${
              message.role === 'user'
                ? darkMode 
                  ? 'bg-gradient-to-br from-emerald-900/40 to-teal-900/40 border border-emerald-700/50 text-gray-200'
                  : 'bg-gradient-to-br from-emerald-100 to-teal-100 border border-emerald-200 text-gray-800'
                : darkMode
                  ? 'backdrop-blur-xl bg-gray-800/90 border border-gray-700 text-gray-200'
                  : 'backdrop-blur-xl bg-white/90 border border-blue-200 text-gray-800'
            }`}
          >
            <p className="whitespace-pre-wrap break-words leading-relaxed">
              <div className="px-5 py-4  mx-auto text-lg">
              {message.content}
              </div>
            </p>
          </div>
          
          {/* Action Buttons */}
          <div className={`flex gap-2 mt-3 opacity-0 group-hover:opacity-100 transition-opacity ${
            message.role === 'user' ? 'justify-end' : 'justify-start'
          }`}>
            <button
              onClick={handleCopy}
              className={`p-2 ${
                darkMode 
                  ? 'bg-gray-700 hover:bg-gray-600 border-gray-600 text-gray-300' 
                  : 'bg-white hover:bg-blue-50 border-blue-200 text-blue-600'
              } border rounded-lg transition-all text-xs shadow-sm`}
              title="Copy message"
            >
              {copied ? (
                <Check className="w-3.5 h-3.5 text-green-500" />
              ) : (
                <Copy className="w-3.5 h-3.5" />
              )}
            </button>
            
            {message.role === 'assistant' && (
              <button
                onClick={() => onSpeak(message.content)}
                className={`p-2 ${
                  darkMode 
                    ? 'bg-gray-700 hover:bg-gray-600 border-gray-600 text-gray-300' 
                    : 'bg-white hover:bg-blue-50 border-blue-200 text-blue-600'
                } border rounded-lg transition-all text-xs shadow-sm`}
                title="Read aloud"
              >
                <Volume2 className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;