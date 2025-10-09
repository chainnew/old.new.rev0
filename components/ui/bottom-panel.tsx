"use client";

import { useState } from "react";
import { Bug, Terminal, List, X } from "lucide-react";
import { cn } from "@/lib/utils";
import { DebugWindow } from "./debug-window";
import { TerminalWindow } from "./terminal-window";

type PanelTab = 'debug' | 'terminal' | 'logs';

interface BottomPanelProps {
  onClose: () => void;
}

export function BottomPanel({ onClose }: BottomPanelProps) {
  const [activeTab, setActiveTab] = useState<PanelTab>('terminal');

  const tabs = [
    { id: 'terminal' as PanelTab, label: 'Terminal', icon: Terminal },
    { id: 'debug' as PanelTab, label: 'Debug', icon: Bug },
    { id: 'logs' as PanelTab, label: 'Logs', icon: List },
  ];

  return (
    <div className="h-full flex flex-col bg-black/60 backdrop-blur-sm border-l border-white/10">
      {/* Tab Bar */}
      <div className="flex items-center justify-between bg-white/[0.02] border-b border-white/10">
        <div className="flex items-center">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={cn(
                  "flex items-center gap-2 px-4 py-2 text-xs font-medium transition-all border-b-2",
                  isActive
                    ? "text-white/90 border-violet-500 bg-white/5"
                    : "text-white/50 border-transparent hover:text-white/70 hover:bg-white/[0.02]"
                )}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
        
        <button
          onClick={onClose}
          className="p-2 mr-2 rounded hover:bg-white/10 text-white/50 hover:text-white/80 transition-colors"
          title="Close panel"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Panel Content */}
      <div className="flex-1 overflow-hidden">
        {activeTab === 'debug' && <DebugWindow />}
        {activeTab === 'terminal' && <TerminalWindow />}
        {activeTab === 'logs' && (
          <div className="h-full flex items-center justify-center text-white/30 text-sm">
            <div className="text-center">
              <List className="w-12 h-12 mx-auto mb-3 opacity-30" />
              <p>Application Logs</p>
              <p className="text-xs mt-1 text-white/20">Coming soon...</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
