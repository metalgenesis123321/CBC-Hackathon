// // src/App.jsx
// import React, { useState, useRef, useEffect } from 'react';
// import { Bot, Trash2, Download, Volume2, Code } from 'lucide-react';
// import { useChat } from './hooks/useChat';
// import { useSpeech, useTheme } from './hooks';
// import { exportConversation, formatTime } from './utils';
// import ChatInput from './components/Chat/ChatInput';
// import ChatMessage from './components/Chat/ChatMessage';
// import ChatHeader from './components/Chat/ChatHeader';
// import BettingDashboard  from './components/Dashboard/BettingDashboard';
// import dummyDashboardData from './data/dummyDashboardData.json';


// function App() {
//   const {
//     messages,
//     loading,
//     currentMarketId,
//     setCurrentMarketId,
//     sendMessage,
//     clearChat,
//   } = useChat();

//   const { 
//     isListening, 
//     isSpeaking, 
//     startListening, 
//     stopListening, 
//     speak, 
//     stopSpeaking 
//   } = useSpeech();

//   const { darkMode, toggleTheme } = useTheme();

//   const [input, setInput] = useState('');
//   const [marketId, setMarketId] = useState('');
//   const [dashboardData, setDashboardData] = useState(null);
//   const [showDashboard, setShowDashboard] = useState(false);

//   const messagesEndRef = useRef(null);

//   const scrollToBottom = () => {
//     messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
//   };

//   useEffect(() => {
//     scrollToBottom();
//   }, [messages]);

//   const handleSend = async () => {
//     if (!input.trim() || loading) return;

//     const userInput = input.trim();
//     const market = marketId.trim() || null;
    
//     setInput('');
//     setCurrentMarketId(market);

//     // Send message to backend
//     const response = await sendMessage(userInput, market);

//     // Handle dashboard response
//     if (response?.type === 'dashboard') {
//       setDashboardData(response.data);
//       setShowDashboard(true);
//     }
//   };

//   const handleVoiceToggle = () => {
//     if (isListening) {
//       stopListening();
//     } else {
//       startListening((transcript) => {
//         setInput((prev) => prev + ' ' + transcript);
//       });
//     }
//   };

//   const handleClearChat = () => {
//     clearChat();
//     setDashboardData(null);
//     setShowDashboard(false);
//     setMarketId('');
//     stopSpeaking();
//   };

//   const handleExport = () => {
//     exportConversation(messages);
//   };

//   // Render dashboard view if available
//   if (showDashboard && dashboardData) {
//     return (
//     <BettingDashboard data={dashboardData} />
//   );
//   }

//   // Main chat interface
//   return (
//     <div className={`flex flex-col h-screen ${
//       darkMode 
//         ? 'bg-gradient-to-br from-slate-900 via-gray-900 to-slate-900' 
//         : 'bg-gradient-to-br from-sky-50 via-blue-50 to-cyan-50'
//     } relative overflow-hidden`}>
//       {/* Background effects */}
//       <div className="absolute inset-0 overflow-hidden pointer-events-none">
//         <div className={`absolute top-0 left-1/4 w-96 h-96 ${
//           darkMode ? 'bg-blue-500/10' : 'bg-blue-200/30'
//         } rounded-full blur-3xl animate-pulse`}></div>
//         <div className={`absolute bottom-0 right-1/4 w-96 h-96 ${
//           darkMode ? 'bg-cyan-500/10' : 'bg-cyan-200/30'
//         } rounded-full blur-3xl animate-pulse`} style={{animationDelay: '1s'}}></div>
//       </div>

//       {/* Header */}
//       <ChatHeader
//         darkMode={darkMode}
//         onToggleTheme={toggleTheme}
//         onExport={handleExport}
//         onClear={handleClearChat}
//         hasDashboard={!!dashboardData}
//         onViewDashboard={() => setShowDashboard(true)}
//         messagesCount={messages.length}
//       />

//       {/* Messages */}
//       <div className="flex-1 overflow-y-auto flex justify-center">
//         <div className="w-full max-w-2xl px-4 py-8 space-y-6">
//           {messages.map((message, index) => (
//             <ChatMessage
//               key={index}
//               message={message}
//               darkMode={darkMode}
//               onSpeak={speak}
//             />
//           ))}

//           {loading && (
//             <div className="flex gap-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
//               <div className={`w-11 h-11 rounded-2xl ${
//                 darkMode 
//                   ? 'bg-gradient-to-br from-blue-600 via-cyan-600 to-sky-700 shadow-blue-500/50' 
//                   : 'bg-gradient-to-br from-blue-400 via-cyan-400 to-sky-500 shadow-blue-300/50'
//               } shadow-lg flex items-center justify-center -rotate-3`}>
//                 <Bot className="w-6 h-6 text-white" />
//               </div>
//               <div className={`backdrop-blur-xl ${
//                 darkMode ? 'bg-gray-800/90 border-gray-700' : 'bg-white/90 border-blue-200'
//               } border px-6 py-4 rounded-2xl shadow-lg`}>
//                 <div className="flex items-center gap-3">
//                   <div className="flex space-x-1">
//                     <div className={`w-2 h-2 ${
//                       darkMode ? 'bg-blue-400' : 'bg-blue-500'
//                     } rounded-full animate-bounce`}></div>
//                     <div className={`w-2 h-2 ${
//                       darkMode ? 'bg-blue-400' : 'bg-blue-500'
//                     } rounded-full animate-bounce`} style={{animationDelay: '0.1s'}}></div>
//                     <div className={`w-2 h-2 ${
//                       darkMode ? 'bg-blue-400' : 'bg-blue-500'
//                     } rounded-full animate-bounce`} style={{animationDelay: '0.2s'}}></div>
//                   </div>
//                   <span className={`${
//                     darkMode ? 'text-gray-300' : 'text-gray-600'
//                   } text-sm`}>
//                     Analyzing...
//                   </span>
//                 </div>
//               </div>
//             </div>
//           )}

//           <div ref={messagesEndRef} />
//         </div>
//       </div>

//       {/* Speaking indicator */}
//       {isSpeaking && (
//         <div className={`mx-6 mb-4 px-6 py-3 backdrop-blur-xl ${
//           darkMode 
//             ? 'bg-blue-900/40 border-blue-700 text-blue-300' 
//             : 'bg-blue-100/80 border-blue-300 text-blue-800'
//         } border rounded-xl flex items-center justify-between shadow-lg`}>
//           <span className="text-sm flex items-center gap-3 font-medium">
//             <Volume2 className="w-5 h-5 animate-pulse" />
//             Speaking...
//           </span>
//           <button
//             onClick={stopSpeaking}
//             className={`text-sm px-3 py-1 ${
//               darkMode ? 'bg-gray-700 hover:bg-gray-600' : 'bg-white/80 hover:bg-white'
//             } rounded-lg transition-all`}
//           >
//             Stop
//           </button>
//         </div>
//       )}

//       {/* Input */}
//       <ChatInput
//         input={input}
//         setInput={setInput}
//         onSend={handleSend}
//         loading={loading}
//         isListening={isListening}
//         onToggleVoice={handleVoiceToggle}
//         marketId={marketId}
//         setMarketId={setMarketId}
//         darkMode={darkMode}
//       />
//     </div>
//   );
// }

// export default App;

// src/App.jsx
import React, { useState, useRef, useEffect } from 'react';
import { Bot, Trash2, Download, Volume2, Code } from 'lucide-react';
import { useChat } from './hooks/useChat';
import { useSpeech, useTheme } from './hooks';
import { exportConversation, formatTime } from './utils';
import ChatInput from './components/Chat/ChatInput';
import ChatMessage from './components/Chat/ChatMessage';
import ChatHeader from './components/Chat/ChatHeader';
import BettingDashboard from './components/Dashboard/BettingDashboard'; // Import your dashboard
import dummyDashboardData from './data/dummyDashboardData.json'; // Import dummy data

function App() {
  const {
    messages,
    loading,
    currentMarketId,
    setCurrentMarketId,
    sendMessage,
    clearChat,
  } = useChat();

  const { 
    isListening, 
    isSpeaking, 
    startListening, 
    stopListening, 
    speak, 
    stopSpeaking 
  } = useSpeech();

  const { darkMode, toggleTheme } = useTheme();

  const [input, setInput] = useState('');
  const [marketId, setMarketId] = useState('');
  const [dashboardData, setDashboardData] = useState(null);
  const [showDashboard, setShowDashboard] = useState(false);

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userInput = input.trim();
    const market = marketId.trim() || null;
    
    setInput('');
    setCurrentMarketId(market);

    // Send message to backend
    const response = await sendMessage(userInput, market);

    // Handle dashboard response
    if (response?.type === 'dashboard') {
      setDashboardData(response.data);
      setShowDashboard(true);
    }
  };

  const handleVoiceToggle = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening((transcript) => {
        setInput((prev) => prev + ' ' + transcript);
      });
    }
  };

  const handleClearChat = () => {
    clearChat();
    setDashboardData(null);
    setShowDashboard(false);
    setMarketId('');
    stopSpeaking();
  };

  const handleExport = () => {
    exportConversation(messages);
  };

  // TEST FUNCTION: Load dummy dashboard
  const handleTestDashboard = () => {
    setDashboardData(dummyDashboardData);
    setShowDashboard(true);
  };

  // Render dashboard view if available
  if (showDashboard && dashboardData) {
    return (
      <BettingDashboard 
        data={dashboardData} 
        onBack={() => setShowDashboard(false)}
      />
    );
  }

  // Main chat interface
  return (
    <div className={`flex flex-col h-screen ${
      darkMode 
        ? 'bg-gradient-to-br from-slate-900 via-gray-900 to-slate-900' 
        : 'bg-gradient-to-br from-sky-50 via-blue-50 to-cyan-50'
    } relative overflow-hidden`}>
      {/* Background effects */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className={`absolute top-0 left-1/4 w-96 h-96 ${
          darkMode ? 'bg-blue-500/10' : 'bg-blue-200/30'
        } rounded-full blur-3xl animate-pulse`}></div>
        <div className={`absolute bottom-0 right-1/4 w-96 h-96 ${
          darkMode ? 'bg-cyan-500/10' : 'bg-cyan-200/30'
        } rounded-full blur-3xl animate-pulse`} style={{animationDelay: '1s'}}></div>
      </div>

      {/* Header */}
      <ChatHeader
        darkMode={darkMode}
        onToggleTheme={toggleTheme}
        onExport={handleExport}
        onClear={handleClearChat}
        hasDashboard={!!dashboardData}
        onViewDashboard={() => setShowDashboard(true)}
        messagesCount={messages.length}
      />

      {/* TEST DASHBOARD BUTTON */}
      <div className="px-6 py-4">
        <button
          onClick={handleTestDashboard}
          className={`px-4 py-2 rounded-lg font-medium transition-all ${
            darkMode 
              ? 'bg-purple-600 hover:bg-purple-700 text-white' 
              : 'bg-purple-500 hover:bg-purple-600 text-white'
          } shadow-lg`}
        >
          🧪 Test Dashboard (Dummy Data)
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto flex justify-center">
        <div className="w-full max-w-2xl px-4 py-8 space-y-6">
          {messages.map((message, index) => (
            
              <div className={`
                
                w-[110%]
                rounded-2xl 
                px-5 py-4 
                center 
                text-lg 
                
              `}>
                <ChatMessage
                  message={message}
                  darkMode={darkMode}
                  onSpeak={speak}
                />
              </div>
            
          ))}

          {loading && (
            <div className="flex gap-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
              <div className={`w-11 h-11 rounded-2xl ${
                darkMode 
                  ? 'bg-gradient-to-br from-blue-600 via-cyan-600 to-sky-700 shadow-blue-500/50' 
                  : 'bg-gradient-to-br from-blue-400 via-cyan-400 to-sky-500 shadow-blue-300/50'
              } shadow-lg flex items-center justify-center -rotate-3`}>
                <Bot className="w-6 h-6 text-white" />
              </div>
              <div className={`backdrop-blur-xl ${
                darkMode ? 'bg-gray-800/90 border-gray-700' : 'bg-white/90 border-blue-200'
              } border px-6 py-4 rounded-2xl shadow-lg`}>
                <div className="flex items-center gap-3">
                  <div className="flex space-x-1">
                    <div className={`w-2 h-2 ${
                      darkMode ? 'bg-blue-400' : 'bg-blue-500'
                    } rounded-full animate-bounce`}></div>
                    <div className={`w-2 h-2 ${
                      darkMode ? 'bg-blue-400' : 'bg-blue-500'
                    } rounded-full animate-bounce`} style={{animationDelay: '0.1s'}}></div>
                    <div className={`w-2 h-2 ${
                      darkMode ? 'bg-blue-400' : 'bg-blue-500'
                    } rounded-full animate-bounce`} style={{animationDelay: '0.2s'}}></div>
                  </div>
                  <span className={`${
                    darkMode ? 'text-gray-300' : 'text-gray-600'
                  } text-sm`}>
                    Analyzing...
                  </span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Speaking indicator */}
      {isSpeaking && (
        <div className={`mx-6 mb-4 px-6 py-3 backdrop-blur-xl ${
          darkMode 
            ? 'bg-blue-900/40 border-blue-700 text-blue-300' 
            : 'bg-blue-100/80 border-blue-300 text-blue-800'
        } border rounded-xl flex items-center justify-between shadow-lg`}>
          <span className="text-sm flex items-center gap-3 font-medium">
            <Volume2 className="w-5 h-5 animate-pulse" />
            Speaking...
          </span>
          <button
            onClick={stopSpeaking}
            className={`text-sm px-3 py-1 ${
              darkMode ? 'bg-gray-700 hover:bg-gray-600' : 'bg-white/80 hover:bg-white'
            } rounded-lg transition-all`}
          >
            Stop
          </button>
        </div>
      )}

      {/* Input */}
      <ChatInput
        input={input}
        setInput={setInput}
        onSend={handleSend}
        loading={loading}
        isListening={isListening}
        onToggleVoice={handleVoiceToggle}
        marketId={marketId}
        setMarketId={setMarketId}
        darkMode={darkMode}
      />
    </div>
  );
}

export default App;
