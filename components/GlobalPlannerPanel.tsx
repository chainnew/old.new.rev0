'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  X, ChevronDown, ChevronUp, Maximize2, Minimize2, 
  Activity, Users, CheckCircle2, Clock, AlertCircle,
  Folder, Zap, Eye, ArrowRight, RefreshCw
} from 'lucide-react';
import Link from 'next/link';

interface Swarm {
  swarm_id: string;
  name: string;
  status: 'idle' | 'running' | 'paused' | 'completed' | 'error';
  agents: any[];
  tasks: any[];
  metadata: {
    project?: string;
    goal?: string;
    features?: string[];
  };
}

interface GlobalPlannerPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function GlobalPlannerPanel({ isOpen, onClose }: GlobalPlannerPanelProps) {
  const [swarms, setSwarms] = useState<Swarm[]>([]);
  const [loading, setLoading] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const fetchSwarms = () => {
    setLoading(true);
    fetch('http://localhost:8000/swarms')
      .then(res => res.json())
      .then(data => {
        const swarmIds = data.swarms.map((s: any) => s.swarm_id);
        // Fetch full details for each swarm
        return Promise.all(
          swarmIds.map((swarmId: string) =>
            fetch(`http://localhost:8000/api/planner/${swarmId}`)
              .then(res => res.json())
              .then(data => {
                // Skip swarms with errors
                if (data.error) {
                  console.warn(`Skipping swarm ${swarmId}:`, data.error);
                  return null;
                }
                return data;
              })
              .catch(err => {
                console.error(`Error fetching swarm ${swarmId}:`, err);
                return null;
              })
          )
        );
      })
      .then(results => {
        setSwarms(results.filter(Boolean));
        setLoading(false);
      })
      .catch(() => setLoading(false));
  };

  useEffect(() => {
    if (isOpen) {
      fetchSwarms();
      // Auto-refresh every 5 seconds
      const interval = setInterval(fetchSwarms, 5000);
      return () => clearInterval(interval);
    }
  }, [isOpen]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-400 bg-green-500/20';
      case 'running': return 'text-blue-400 bg-blue-500/20';
      case 'error': return 'text-red-400 bg-red-500/20';
      default: return 'text-white/40 bg-white/10';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle2 className="w-3 h-3" />;
      case 'running': return <Clock className="w-3 h-3 animate-spin" />;
      case 'error': return <AlertCircle className="w-3 h-3" />;
      default: return <Clock className="w-3 h-3" />;
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0, x: 400 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: 400 }}
          transition={{ type: 'spring', damping: 25, stiffness: 200 }}
          className={`fixed ${isExpanded ? 'inset-4' : 'right-4 top-4 bottom-4'} ${isMinimized ? 'h-auto bottom-auto' : ''} z-50`}
          style={{ width: isExpanded ? 'auto' : '420px' }}
        >
          <div className="h-full flex flex-col bg-gradient-to-br from-black via-violet-950/20 to-black border border-violet-500/30 rounded-xl shadow-2xl shadow-violet-500/20 backdrop-blur-xl overflow-hidden">
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-violet-500/30 bg-black/40">
              <div className="flex items-center gap-2">
                <Zap className="w-4 h-4 text-violet-400" />
                <h3 className="text-sm font-semibold text-white">AI Swarm Planner</h3>
                <span className="text-xs text-white/40 font-mono">
                  {swarms.length} active
                </span>
              </div>
              
              <div className="flex items-center gap-1">
                <button
                  onClick={fetchSwarms}
                  disabled={loading}
                  className="p-1.5 hover:bg-white/10 rounded transition-colors"
                  title="Refresh"
                >
                  <RefreshCw className={`w-3.5 h-3.5 text-white/60 ${loading ? 'animate-spin' : ''}`} />
                </button>
                <button
                  onClick={() => setIsMinimized(!isMinimized)}
                  className="p-1.5 hover:bg-white/10 rounded transition-colors"
                  title={isMinimized ? 'Expand' : 'Minimize'}
                >
                  {isMinimized ? (
                    <ChevronDown className="w-3.5 h-3.5 text-white/60" />
                  ) : (
                    <ChevronUp className="w-3.5 h-3.5 text-white/60" />
                  )}
                </button>
                <button
                  onClick={() => setIsExpanded(!isExpanded)}
                  className="p-1.5 hover:bg-white/10 rounded transition-colors"
                  title={isExpanded ? 'Collapse' : 'Expand'}
                >
                  {isExpanded ? (
                    <Minimize2 className="w-3.5 h-3.5 text-white/60" />
                  ) : (
                    <Maximize2 className="w-3.5 h-3.5 text-white/60" />
                  )}
                </button>
                <button
                  onClick={onClose}
                  className="p-1.5 hover:bg-white/10 rounded transition-colors"
                  title="Close"
                >
                  <X className="w-3.5 h-3.5 text-white/60" />
                </button>
              </div>
            </div>

            {/* Content */}
            {!isMinimized && (
              <div className="flex-1 overflow-hidden flex flex-col">
                {/* Stats */}
                <div className="grid grid-cols-3 gap-2 p-3 border-b border-white/5">
                  <div className="bg-white/5 rounded-lg p-2">
                    <div className="flex items-center gap-1.5 mb-1">
                      <Activity className="w-3 h-3 text-violet-400" />
                      <span className="text-[10px] text-white/50">Active</span>
                    </div>
                    <p className="text-lg font-bold text-white">
                      {swarms.filter(s => s.status === 'running').length}
                    </p>
                  </div>
                  
                  <div className="bg-white/5 rounded-lg p-2">
                    <div className="flex items-center gap-1.5 mb-1">
                      <Users className="w-3 h-3 text-blue-400" />
                      <span className="text-[10px] text-white/50">Agents</span>
                    </div>
                    <p className="text-lg font-bold text-white">
                      {swarms.reduce((acc, s) => acc + (s.agents?.length || 0), 0)}
                    </p>
                  </div>
                  
                  <div className="bg-white/5 rounded-lg p-2">
                    <div className="flex items-center gap-1.5 mb-1">
                      <CheckCircle2 className="w-3 h-3 text-green-400" />
                      <span className="text-[10px] text-white/50">Done</span>
                    </div>
                    <p className="text-lg font-bold text-white">
                      {swarms.filter(s => s.status === 'completed').length}
                    </p>
                  </div>
                </div>

                {/* Swarms List */}
                <div className="flex-1 overflow-y-auto p-3 space-y-2">
                  {loading && swarms.length === 0 ? (
                    <div className="flex items-center justify-center h-32">
                      <div className="text-center">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-violet-400 mx-auto mb-2"></div>
                        <p className="text-xs text-white/40">Loading swarms...</p>
                      </div>
                    </div>
                  ) : swarms.length === 0 ? (
                    <div className="flex items-center justify-center h-32">
                      <div className="text-center">
                        <Folder className="w-12 h-12 text-white/20 mx-auto mb-2" />
                        <p className="text-xs text-white/40">No active swarms</p>
                      </div>
                    </div>
                  ) : (
                    swarms.map((swarm, idx) => (
                      <motion.div
                        key={swarm.swarm_id}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: idx * 0.05 }}
                        className="bg-white/5 hover:bg-white/10 border border-white/10 hover:border-violet-500/30 rounded-lg p-3 transition-all group"
                      >
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1">
                              <h4 className="text-sm font-medium text-white truncate">
                                {swarm.metadata?.project || swarm.name}
                              </h4>
                              <span className={`flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-medium ${getStatusColor(swarm.status)}`}>
                                {getStatusIcon(swarm.status)}
                                {swarm.status}
                              </span>
                            </div>
                            <p className="text-xs text-white/40 line-clamp-2 mb-2">
                              {swarm.metadata?.goal || 'No description'}
                            </p>
                          </div>
                        </div>

                        <div className="flex items-center justify-between text-xs">
                          <div className="flex items-center gap-3 text-white/50">
                            <span className="flex items-center gap-1">
                              <Users className="w-3 h-3" />
                              {swarm.agents?.length || 0}
                            </span>
                            <span className="flex items-center gap-1">
                              <Activity className="w-3 h-3" />
                              {swarm.tasks?.length || 0}
                            </span>
                          </div>
                          
                          <Link
                            href={`/planner/${swarm.swarm_id}`}
                            className="flex items-center gap-1 text-violet-400 hover:text-violet-300 transition-colors"
                          >
                            <Eye className="w-3 h-3" />
                            <span className="text-[10px]">View</span>
                            <ArrowRight className="w-3 h-3" />
                          </Link>
                        </div>

                        {swarm.metadata?.features && swarm.metadata.features.length > 0 && (
                          <div className="flex flex-wrap gap-1 mt-2 pt-2 border-t border-white/5">
                            {swarm.metadata.features.slice(0, 3).map((feature, i) => (
                              <span
                                key={i}
                                className="px-1.5 py-0.5 bg-violet-500/10 text-violet-300 rounded text-[9px]"
                              >
                                {feature}
                              </span>
                            ))}
                            {swarm.metadata.features.length > 3 && (
                              <span className="px-1.5 py-0.5 bg-white/5 text-white/40 rounded text-[9px]">
                                +{swarm.metadata.features.length - 3}
                              </span>
                            )}
                          </div>
                        )}
                      </motion.div>
                    ))
                  )}
                </div>
              </div>
            )}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
