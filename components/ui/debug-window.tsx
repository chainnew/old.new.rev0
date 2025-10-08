"use client";

import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, Trash2, Download, Globe, Brain, Database, List } from "lucide-react";
import { cn } from "@/lib/utils";

type LogCategory = 'site' | 'ai' | 'database' | 'all';

interface LogEntry {
  id: number;
  timestamp: string;
  type: 'log' | 'warn' | 'error';
  category: LogCategory;
  message: string;
  data?: any;
}

export function DebugWindow() {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [activeTab, setActiveTab] = useState<LogCategory>('all');
  const logsEndRef = useRef<HTMLDivElement>(null);
  const logIdCounter = useRef(0);

  useEffect(() => {
    // Intercept console methods
    const originalLog = console.log;
    const originalWarn = console.warn;
    const originalError = console.error;

    console.log = (...args: any[]) => {
      originalLog(...args);
      addLog('log', args);
    };

    console.warn = (...args: any[]) => {
      originalWarn(...args);
      addLog('warn', args);
    };

    console.error = (...args: any[]) => {
      originalError(...args);
      addLog('error', args);
    };

    // Cleanup
    return () => {
      console.log = originalLog;
      console.warn = originalWarn;
      console.error = originalError;
    };
  }, []);

  const determineCategory = (message: string): LogCategory => {
    const lowerMessage = message.toLowerCase();
    
    // AI-related keywords
    if (lowerMessage.includes('[ai]') || 
        lowerMessage.includes('grok') || 
        lowerMessage.includes('agent') || 
        lowerMessage.includes('openrouter') ||
        lowerMessage.includes('chat') ||
        lowerMessage.includes('message')) {
      return 'ai';
    }
    
    // Database-related keywords
    if (lowerMessage.includes('[db]') || 
        lowerMessage.includes('database') || 
        lowerMessage.includes('postgres') || 
        lowerMessage.includes('query') ||
        lowerMessage.includes('sql')) {
      return 'database';
    }
    
    // Site/UI-related keywords (default for most things)
    return 'site';
  };

  const addLog = (type: 'log' | 'warn' | 'error', args: any[]) => {
    const message = args.map(arg => {
      if (typeof arg === 'object') {
        try {
          return JSON.stringify(arg, null, 2);
        } catch {
          return String(arg);
        }
      }
      return String(arg);
    }).join(' ');

    const category = determineCategory(message);

    const newLog: LogEntry = {
      id: logIdCounter.current++,
      timestamp: new Date().toLocaleTimeString(),
      type,
      category,
      message,
      data: args.length > 1 ? args : undefined
    };

    setLogs(prev => [...prev.slice(-100), newLog]); // Keep last 100 logs
  };

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const clearLogs = () => {
    setLogs([]);
  };

  const downloadLogs = () => {
    const logText = logs.map(log => 
      `[${log.timestamp}] [${log.category.toUpperCase()}] ${log.type.toUpperCase()}: ${log.message}`
    ).join('\n');
    
    const blob = new Blob([logText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `debug-logs-${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const filteredLogs = activeTab === 'all' 
    ? logs 
    : logs.filter(log => log.category === activeTab);

  const tabs = [
    { id: 'all' as LogCategory, label: 'All', icon: List, count: logs.length },
    { id: 'site' as LogCategory, label: 'Site', icon: Globe, count: logs.filter(l => l.category === 'site').length },
    { id: 'ai' as LogCategory, label: 'AI', icon: Brain, count: logs.filter(l => l.category === 'ai').length },
    { id: 'database' as LogCategory, label: 'Database', icon: Database, count: logs.filter(l => l.category === 'database').length },
  ];

  return (
    <div className="h-full flex flex-col bg-black/60 backdrop-blur-sm border-l border-white/10 rounded-l-xl">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-white/10 bg-white/[0.02]">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
          <span className="text-xs font-semibold text-white/80">Debug Console</span>
          <span className="text-[10px] text-white/40">({logs.length})</span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={downloadLogs}
            className="p-1 rounded hover:bg-white/10 text-white/50 hover:text-white/80 transition-colors"
            title="Download logs"
          >
            <Download className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={clearLogs}
            className="p-1 rounded hover:bg-white/10 text-white/50 hover:text-white/80 transition-colors"
            title="Clear logs"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-1 px-2 py-2 bg-white/[0.01] border-b border-white/10">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                "flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all",
                isActive
                  ? "bg-white/10 text-white/90 shadow-sm"
                  : "text-white/50 hover:bg-white/5 hover:text-white/70"
              )}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{tab.label}</span>
              {tab.count > 0 && (
                <span className={cn(
                  "px-1.5 py-0.5 rounded-full text-[10px] font-bold",
                  isActive
                    ? "bg-violet-500/30 text-violet-300"
                    : "bg-white/10 text-white/40"
                )}>
                  {tab.count}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Logs Area */}
      <div className="flex-1 overflow-y-auto overflow-x-hidden p-3 space-y-2 font-mono text-xs">
        {filteredLogs.length === 0 ? (
          <div className="text-white/30 text-center py-8">
            {activeTab === 'all' 
              ? 'No logs yet. Interact with the app to see debug output.'
              : `No ${activeTab} logs yet.`
            }
          </div>
        ) : (
          filteredLogs.map((log) => (
            <div
              key={log.id}
              className={`p-2 rounded-md border ${
                log.type === 'error'
                  ? 'bg-red-500/10 border-red-500/30 text-red-300'
                  : log.type === 'warn'
                    ? 'bg-yellow-500/10 border-yellow-500/30 text-yellow-300'
                    : 'bg-white/5 border-white/10 text-white/70'
              }`}
            >
              <div className="flex items-start gap-2">
                <span className="text-white/40 text-[10px] mt-0.5 flex-shrink-0">
                  {log.timestamp}
                </span>
                <span
                  className={`text-[10px] font-bold mt-0.5 flex-shrink-0 ${
                    log.type === 'error'
                      ? 'text-red-400'
                      : log.type === 'warn'
                        ? 'text-yellow-400'
                        : 'text-blue-400'
                  }`}
                >
                  {log.type.toUpperCase()}
                </span>
                {activeTab === 'all' && (
                  <span className={cn(
                    "text-[9px] font-bold px-1.5 py-0.5 rounded mt-0.5 flex-shrink-0",
                    log.category === 'ai' && "bg-violet-500/20 text-violet-300",
                    log.category === 'database' && "bg-blue-500/20 text-blue-300",
                    log.category === 'site' && "bg-green-500/20 text-green-300"
                  )}>
                    {log.category.toUpperCase()}
                  </span>
                )}
                <pre className="whitespace-pre-wrap break-words flex-1 text-[11px]">
                  {log.message}
                </pre>
              </div>
            </div>
          ))
        )}
        <div ref={logsEndRef} />
      </div>

      {/* Footer Stats */}
      <div className="px-4 py-2 border-t border-white/10 bg-white/[0.02] text-[10px] text-white/40">
        <div className="flex justify-between">
          <span>
            {activeTab === 'all' ? 'Total' : activeTab.charAt(0).toUpperCase() + activeTab.slice(1)}: {filteredLogs.length}
          </span>
          <span>
            Errors: {filteredLogs.filter(l => l.type === 'error').length} | 
            Warns: {filteredLogs.filter(l => l.type === 'warn').length}
          </span>
        </div>
      </div>
    </div>
  );
}
