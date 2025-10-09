'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { 
  Folder, Users, CheckCircle2, Clock, AlertCircle, 
  Activity, Zap, Settings, Home, ArrowRight, Sparkles 
} from 'lucide-react';

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

export default function PlannerIndex() {
  const [swarms, setSwarms] = useState<Swarm[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Fetch all swarms from API
    fetch('http://localhost:8000/swarms')
      .then(res => res.json())
      .then(data => {
        const swarmIds = data.swarms.map((s: any) => s.swarm_id);
        
        // Fetch full details for each swarm
        return Promise.all(
          swarmIds.map((swarmId: string) =>
            fetch(`http://localhost:8000/api/planner/${swarmId}`)
              .then(res => res.json())
              .catch(() => null)
          )
        );
      })
      .then(results => {
        setSwarms(results.filter(Boolean));
        setLoading(false);
      })
      .catch(err => {
        console.error('Error fetching swarms:', err);
        setError('Failed to load projects');
        setLoading(false);
      });
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-400 bg-green-500/20';
      case 'running': return 'text-blue-400 bg-blue-500/20';
      case 'error': return 'text-red-400 bg-red-500/20';
      case 'paused': return 'text-yellow-400 bg-yellow-500/20';
      default: return 'text-white/40 bg-white/10';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle2 className="w-4 h-4" />;
      case 'running': return <Clock className="w-4 h-4 animate-spin" />;
      case 'error': return <AlertCircle className="w-4 h-4" />;
      default: return <Clock className="w-4 h-4" />;
    }
  };

  if (loading) {
    return (
      <div className="h-screen bg-black flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-violet-500 mx-auto mb-4"></div>
          <p className="text-white/50">Loading projects...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-white overflow-auto pb-32">
      <div className="max-w-7xl mx-auto p-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2 bg-gradient-to-r from-violet-400 to-purple-400 bg-clip-text text-transparent">
            AI Swarm Planner
          </h1>
          <p className="text-white/50">
            High-level view of all active projects and agent operations
          </p>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white/[0.02] border border-white/10 rounded-lg p-4"
          >
            <div className="flex items-center gap-3">
              <Folder className="w-8 h-8 text-violet-400" />
              <div>
                <p className="text-2xl font-bold">{swarms.length}</p>
                <p className="text-xs text-white/50">Total Projects</p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white/[0.02] border border-white/10 rounded-lg p-4"
          >
            <div className="flex items-center gap-3">
              <Users className="w-8 h-8 text-blue-400" />
              <div>
                <p className="text-2xl font-bold">
                  {swarms.reduce((acc, s) => acc + (s.agents?.length || 0), 0)}
                </p>
                <p className="text-xs text-white/50">Active Agents</p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white/[0.02] border border-white/10 rounded-lg p-4"
          >
            <div className="flex items-center gap-3">
              <CheckCircle2 className="w-8 h-8 text-green-400" />
              <div>
                <p className="text-2xl font-bold">
                  {swarms.filter(s => s.status === 'completed').length}
                </p>
                <p className="text-xs text-white/50">Completed</p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-white/[0.02] border border-white/10 rounded-lg p-4"
          >
            <div className="flex items-center gap-3">
              <Clock className="w-8 h-8 text-yellow-400" />
              <div>
                <p className="text-2xl font-bold">
                  {swarms.filter(s => s.status === 'running').length}
                </p>
                <p className="text-xs text-white/50">Running</p>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Projects List */}
        {swarms.length === 0 ? (
          <div className="bg-white/[0.02] border border-white/10 rounded-lg p-12 text-center">
            <Folder className="w-16 h-16 text-white/20 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-white/70 mb-2">No Projects Yet</h3>
            <p className="text-white/40 mb-4">
              Start a new project by sending a message to the orchestrator
            </p>
            <code className="text-xs bg-black/50 px-4 py-2 rounded text-violet-300">
              curl -X POST http://localhost:8000/orchestrator/process -d '{"{"}message": "Build..."{"}"}'
            </code>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4">
            {swarms.map((swarm, idx) => (
              <motion.div
                key={swarm.swarm_id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.1 }}
              >
                <Link href={`/planner/${swarm.swarm_id}`}>
                  <div className="bg-white/[0.02] border border-white/10 rounded-lg p-6 hover:bg-white/[0.05] hover:border-violet-500/30 transition-all cursor-pointer group">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="text-xl font-semibold group-hover:text-violet-400 transition-colors">
                            {swarm.metadata?.project || swarm.name || 'Unnamed Project'}
                          </h3>
                          <span className={`flex items-center gap-1.5 px-2 py-1 rounded text-xs font-medium ${getStatusColor(swarm.status)}`}>
                            {getStatusIcon(swarm.status)}
                            {swarm.status}
                          </span>
                        </div>
                        <p className="text-sm text-white/50 mb-3">
                          {swarm.metadata?.goal || 'No description available'}
                        </p>
                        {swarm.metadata?.features && swarm.metadata.features.length > 0 && (
                          <div className="flex flex-wrap gap-2 mb-3">
                            {swarm.metadata.features.slice(0, 5).map((feature, i) => (
                              <span
                                key={i}
                                className="px-2 py-1 bg-violet-500/10 text-violet-300 rounded text-xs"
                              >
                                {feature}
                              </span>
                            ))}
                            {swarm.metadata.features.length > 5 && (
                              <span className="px-2 py-1 bg-white/5 text-white/40 rounded text-xs">
                                +{swarm.metadata.features.length - 5} more
                              </span>
                            )}
                          </div>
                        )}
                      </div>
                      <div className="text-right text-xs text-white/40 font-mono">
                        {swarm.swarm_id.slice(0, 8)}
                      </div>
                    </div>

                    <div className="flex items-center gap-6 text-sm">
                      <div className="flex items-center gap-2">
                        <Users className="w-4 h-4 text-white/40" />
                        <span className="text-white/60">
                          {swarm.agents?.length || 0} agents
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <CheckCircle2 className="w-4 h-4 text-white/40" />
                        <span className="text-white/60">
                          {swarm.tasks?.length || 0} tasks
                        </span>
                      </div>
                      <div className="ml-auto text-violet-400 text-xs group-hover:translate-x-1 transition-transform">
                        View Details →
                      </div>
                    </div>
                  </div>
                </Link>
              </motion.div>
            ))}
          </div>
        )}
      </div>
      
      {/* Extra space to ensure black covers bottom */}
      <div className="h-screen bg-black"></div>
    </div>
  );
}
