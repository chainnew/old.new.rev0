"use client";

import { useState, useRef, useEffect } from "react";
import { motion } from "framer-motion";
import { Terminal as TerminalIcon, Trash2, Download, Copy, Check } from "lucide-react";
import { cn } from "@/lib/utils";

interface CommandHistory {
  id: number;
  command: string;
  output: string;
  timestamp: string;
}

export function TerminalWindow() {
  const [history, setHistory] = useState<CommandHistory[]>([
    {
      id: 0,
      command: 'echo "Welcome to old.new Terminal"',
      output: 'Welcome to old.new Terminal',
      timestamp: new Date().toLocaleTimeString()
    }
  ]);
  const [currentCommand, setCurrentCommand] = useState('');
  const [copied, setCopied] = useState(false);
  const terminalRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const historyIdCounter = useRef(1);

  useEffect(() => {
    terminalRef.current?.scrollTo(0, terminalRef.current.scrollHeight);
  }, [history]);

  const handleCommand = async (cmd: string) => {
    if (!cmd.trim()) return;

    const newEntry: CommandHistory = {
      id: historyIdCounter.current++,
      command: cmd,
      output: 'Processing...',
      timestamp: new Date().toLocaleTimeString()
    };

    setHistory(prev => [...prev, newEntry]);
    setCurrentCommand('');

    // Simulate command execution
    setTimeout(() => {
      setHistory(prev => prev.map(entry => 
        entry.id === newEntry.id 
          ? { ...entry, output: `Executed: ${cmd}\n[Feature coming soon - Backend integration pending]` }
          : entry
      ));
    }, 500);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleCommand(currentCommand);
    }
  };

  const clearTerminal = () => {
    setHistory([]);
  };

  const copyAllOutput = () => {
    const text = history.map(h => `$ ${h.command}\n${h.output}`).join('\n\n');
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="h-full flex flex-col bg-black font-mono">
      {/* Terminal Header */}
      <div className="flex items-center justify-between px-4 py-2 bg-white/[0.02] border-b border-white/10 backdrop-blur-sm">
        <div className="flex items-center gap-2">
          <TerminalIcon className="w-4 h-4 text-green-400" />
          <span className="text-xs font-semibold text-white/80">Terminal</span>
          <span className="text-[10px] text-white/40">{history.length} commands</span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={copyAllOutput}
            className="p-1 rounded hover:bg-white/10 text-white/50 hover:text-white/80 transition-colors"
            title="Copy all"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-green-400" /> : <Copy className="w-3.5 h-3.5" />}
          </button>
          <button
            onClick={clearTerminal}
            className="p-1 rounded hover:bg-white/10 text-white/50 hover:text-white/80 transition-colors"
            title="Clear terminal"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Terminal Output */}
      <div 
        ref={terminalRef}
        className="flex-1 overflow-y-auto p-4 space-y-3 text-sm"
        onClick={() => inputRef.current?.focus()}
      >
        {history.map(entry => (
          <div key={entry.id} className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="text-green-400">$</span>
              <span className="text-white/90">{entry.command}</span>
              <span className="text-white/30 text-[10px]">{entry.timestamp}</span>
            </div>
            <div className="text-white/70 pl-4 whitespace-pre-wrap">
              {entry.output}
            </div>
          </div>
        ))}

        {/* Current Input Line */}
        <div className="flex items-center gap-2">
          <span className="text-green-400">$</span>
          <input
            ref={inputRef}
            type="text"
            value={currentCommand}
            onChange={(e) => setCurrentCommand(e.target.value)}
            onKeyDown={handleKeyDown}
            className="flex-1 bg-transparent border-none outline-none text-white/90"
            placeholder="Type a command..."
            autoFocus
          />
        </div>
      </div>

      {/* Terminal Footer */}
      <div className="px-4 py-1.5 bg-white/[0.02] border-t border-white/10 text-[10px] text-white/40 flex justify-between">
        <span>Ready</span>
        <span className="text-green-400">●</span>
      </div>
    </div>
  );
}
