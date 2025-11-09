//src/components/Dashboard/DashboardView.jsx
import React from 'react';
import { ArrowLeft, TrendingUp, TrendingDown, Activity } from 'lucide-react';
import { formatCurrency, formatPercentage } from '../../utils';

const DashboardView = ({ data, darkMode, onBack }) => {
  if (!data) return null;

  return (
    <div className={`flex flex-col h-screen ${
      darkMode 
        ? 'bg-gradient-to-br from-gray-900 via-slate-900 to-gray-900' 
        : 'bg-gradient-to-br from-sky-50 via-blue-50 to-cyan-50'
    }`}>
      {/* Header */}
      <div className={`backdrop-blur-xl ${
        darkMode ? 'bg-gray-800/80 border-gray-700/50' : 'bg-white/80 border-blue-200/50'
      } border-b shadow-xl px-8 py-4`}>
        <div className="flex items-center justify-between">
          <button
            onClick={onBack}
            className={`flex items-center gap-2 px-4 py-2 ${
              darkMode 
                ? 'bg-gray-700 hover:bg-gray-600 text-gray-200' 
                : 'bg-blue-100 hover:bg-blue-200 text-blue-700'
            } rounded-lg transition-all`}
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Chat
          </button>
          <h1 className={`text-xl font-bold ${
            darkMode ? 'text-blue-400' : 'text-blue-700'
          }`}>
            Market Dashboard
          </h1>
        </div>
      </div>

      {/* Dashboard Content */}
      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-7xl mx-auto space-y-6">
          {/* Market Question */}
          <div className={`p-6 rounded-2xl ${
            darkMode ? 'bg-gray-800/50 border-gray-700' : 'bg-white/80 border-blue-200'
          } border shadow-lg`}>
            <h2 className={`text-2xl font-bold ${
              darkMode ? 'text-gray-100' : 'text-gray-900'
            }`}>
              {data.question}
            </h2>
          </div>

          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <MetricCard
              title="Health Score"
              value={`${data.healthScore}/100`}
              icon={<Activity className="w-6 h-6" />}
              darkMode={darkMode}
              color="blue"
            />
            <MetricCard
              title="Liquidity Score"
              value={`${data.liquidityScore}/10`}
              icon={<TrendingUp className="w-6 h-6" />}
              darkMode={darkMode}
              color="green"
            />
            <MetricCard
              title="Volume 24h"
              value={formatCurrency(data.volumeData?.['24h']?.reduce((sum, v) => sum + v.volume, 0) || 0, 0)}
              icon={<Activity className="w-6 h-6" />}
              darkMode={darkMode}
              color="purple"
            />
          </div>

          {/* Odds Comparison */}
          {data.oddsComparison && (
            <div className={`p-6 rounded-2xl ${
              darkMode ? 'bg-gray-800/50 border-gray-700' : 'bg-white/80 border-blue-200'
            } border shadow-lg`}>
              <h3 className={`text-lg font-bold mb-4 ${
                darkMode ? 'text-gray-100' : 'text-gray-900'
              }`}>
                Odds Comparison
              </h3>
              <div className="grid grid-cols-3 gap-4">
                {Object.entries(data.oddsComparison).map(([option, odds]) => (
                  <div key={option} className="text-center">
                    <h4 className={`font-semibold mb-2 capitalize ${
                      darkMode ? 'text-gray-300' : 'text-gray-700'
                    }`}>
                      {option}
                    </h4>
                    <div className="space-y-1 text-sm">
                      <div>Polymarket: {formatPercentage(odds.polymarket)}</div>
                      <div>News: {formatPercentage(odds.news)}</div>
                      <div>Expert: {formatPercentage(odds.expert)}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* AI Summary */}
          {data.aiSummary && (
            <div className={`p-6 rounded-2xl ${
              darkMode ? 'bg-gray-800/50 border-gray-700' : 'bg-white/80 border-blue-200'
            } border shadow-lg`}>
              <h3 className={`text-lg font-bold mb-4 ${
                darkMode ? 'text-gray-100' : 'text-gray-900'
              }`}>
                AI Analysis
              </h3>
              <div className="space-y-4">
                {data.aiSummary.map((section, index) => (
                  <div key={index}>
                    <h4 className={`font-semibold mb-2 ${
                      darkMode ? 'text-blue-400' : 'text-blue-600'
                    }`}>
                      {section.title}
                    </h4>
                    <p className={`text-sm ${
                      darkMode ? 'text-gray-300' : 'text-gray-700'
                    }`}>
                      {section.content}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* News */}
          {data.news && data.news.length > 0 && (
            <div className={`p-6 rounded-2xl ${
              darkMode ? 'bg-gray-800/50 border-gray-700' : 'bg-white/80 border-blue-200'
            } border shadow-lg`}>
              <h3 className={`text-lg font-bold mb-4 ${
                darkMode ? 'text-gray-100' : 'text-gray-900'
              }`}>
                Recent News
              </h3>
              <div className="space-y-3">
                {data.news.map((article, index) => (
                  <div key={index} className={`p-3 rounded-lg ${
                    darkMode ? 'bg-gray-700/50' : 'bg-gray-50'
                  }`}>
                    <h4 className={`font-medium mb-1 ${
                      darkMode ? 'text-gray-200' : 'text-gray-900'
                    }`}>
                      {article.title}
                    </h4>
                    <p className={`text-xs ${
                      darkMode ? 'text-gray-400' : 'text-gray-600'
                    }`}>
                      {article.source} • {article.date}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const MetricCard = ({ title, value, icon, darkMode, color }) => {
  const colorClasses = {
    blue: darkMode ? 'text-blue-400' : 'text-blue-600',
    green: darkMode ? 'text-green-400' : 'text-green-600',
    purple: darkMode ? 'text-purple-400' : 'text-purple-600',
  };

  return (
    <div className={`p-6 rounded-2xl ${
      darkMode ? 'bg-gray-800/50 border-gray-700' : 'bg-white/80 border-blue-200'
    } border shadow-lg`}>
      <div className="flex items-center justify-between mb-2">
        <span className={`text-sm ${
          darkMode ? 'text-gray-400' : 'text-gray-600'
        }`}>
          {title}
        </span>
        <div className={colorClasses[color]}>
          {icon}
        </div>
      </div>
      <div className={`text-2xl font-bold ${
        darkMode ? 'text-gray-100' : 'text-gray-900'
      }`}>
        {value}
      </div>
    </div>
  );
};

export default DashboardView;


