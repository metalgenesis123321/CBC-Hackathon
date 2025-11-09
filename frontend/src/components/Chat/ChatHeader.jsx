// src/components/Chat/ChatHeader.jsx
import React from 'react';
import { Bot, Trash2, Download, Code, Sparkles, Zap } from 'lucide-react';

const ChatHeader = ({ 
  darkMode, 
  onToggleTheme, 
  onExport, 
  onClear, 
  hasDashboard,
  onViewDashboard,
  messagesCount 
}) => {
  return (
    <div className={`relative backdrop-blur-xl ${
      darkMode ? 'bg-gray-900/80 border-gray-700/50' : 'bg-white/80 border-blue-200/50'
    } border-b shadow-xl`}>
      <div className="px-8 py-5 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="relative">
            <div className={`w-14 h-14 ${
              darkMode 
                ? 'bg-gradient-to-br from-blue-600 via-cyan-600 to-sky-700' 
                : 'bg-gradient-to-br from-blue-400 via-cyan-400 to-sky-500'
            } rounded-2xl flex items-center justify-center shadow-lg shadow-blue-300/50 rotate-3 hover:rotate-0 transition-transform`}>
              <Bot className="w-8 h-8 text-white" />
            </div>
            <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-400 rounded-full border-2 border-white animate-pulse"></div>
          </div>
          <div>
            <h1 className={`text-2xl font-bold ${
              darkMode 
                ? 'bg-gradient-to-r from-blue-400 via-cyan-400 to-sky-400' 
                : 'bg-gradient-to-r from-blue-600 via-cyan-600 to-sky-600'
            } bg-clip-text text-transparent flex items-center gap-2`}>
              PolySage AI
              <Sparkles className="w-5 h-5 text-yellow-400 animate-pulse" />
            </h1>
            <p className={`text-sm ${
              darkMode ? 'text-blue-400/70' : 'text-blue-600/70'
            } flex items-center gap-2 mt-1`}>
              <Zap className="w-3 h-3" />
              Polymarket Analysis • Claude Sonnet 4.5
            </p>
          </div>
        </div>
        
        <div className="flex gap-3">
          <button
            onClick={onToggleTheme}
            className={`group px-4 py-2.5 ${
              darkMode 
                ? 'bg-yellow-500/20 hover:bg-yellow-500/30 border-yellow-500/30 hover:border-yellow-500/50 text-yellow-300' 
                : 'bg-gray-100 hover:bg-gray-200 border-gray-200 hover:border-gray-300 text-gray-700'
            } border rounded-xl flex items-center gap-2 transition-all shadow-md hover:shadow-lg`}
            title={darkMode ? 'Light mode' : 'Dark mode'}
          >
            {darkMode ? '☀️' : '🌙'}
            <span className="text-sm font-medium hidden sm:inline">
              {darkMode ? 'Light' : 'Dark'}
            </span>
          </button>
          
          {hasDashboard && (
            <button
              onClick={onViewDashboard}
              className="group px-4 py-2.5 bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white rounded-xl flex items-center gap-2 transition-all shadow-lg animate-pulse"
            >
              <Code className="w-4 h-4" />
              <span className="text-sm font-medium">View Dashboard</span>
            </button>
          )}
          
          <button
            onClick={onExport}
            className="group px-4 py-2.5 bg-cyan-50 hover:bg-cyan-100 border border-cyan-200 hover:border-cyan-300 text-cyan-700 rounded-xl flex items-center gap-2 transition-all shadow-md hover:shadow-lg"
          >
            <Download className="w-4 h-4 group-hover:translate-y-0.5 transition-transform" />
            <span className="text-sm font-medium hidden sm:inline">Export</span>
          </button>
          
          <button
            onClick={onClear}
            className="group px-4 py-2.5 bg-rose-50 hover:bg-rose-100 border border-rose-200 hover:border-rose-300 text-rose-700 rounded-xl flex items-center gap-2 transition-all shadow-md hover:shadow-lg"
          >
            <Trash2 className="w-4 h-4 group-hover:scale-110 transition-transform" />
            <span className="text-sm font-medium hidden sm:inline">Clear</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatHeader;