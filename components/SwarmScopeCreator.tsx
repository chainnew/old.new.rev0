'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Zap, Loader2, CheckCircle2, AlertCircle, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface SwarmResponse {
  status: string;
  message: string;
  swarm_id?: string;
  planner_url?: string;
}

export function SwarmScopeCreator() {
  const [input, setInput] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [response, setResponse] = useState<SwarmResponse | null>(null);
  const [isExpanded, setIsExpanded] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isSubmitting) return;

    setIsSubmitting(true);
    setResponse(null);

    try {
      const res = await fetch('http://localhost:8000/orchestrator/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: input,
          user_id: 'web-user'
        })
      });

      const data = await res.json();
      setResponse(data);

      // Auto-redirect to planner if successful
      if (data.status === 'success' && data.planner_url) {
        setTimeout(() => {
          window.location.href = data.planner_url;
        }, 2000);
      }
    } catch (error) {
      setResponse({
        status: 'error',
        message: 'Failed to connect to orchestrator. Is the backend running on :8000?'
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const examples = [
    'Build an e-commerce store with Stripe',
    'Create a task tracker like Trello',
    'Build a real-time chat app with WebSockets',
    'Make a SaaS dashboard with analytics'
  ];

  return (
    <motion.div
      className="fixed bottom-24 right-6 z-40"
      initial={{ scale: 0, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ type: 'spring', stiffness: 260, damping: 20 }}
    >
      <AnimatePresence>
        {!isExpanded ? (
          <motion.button
            key="button"
            onClick={() => setIsExpanded(true)}
            className="relative group"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            {/* Pulsing glow */}
            <motion.div
              className="absolute inset-0 rounded-full bg-gradient-to-r from-violet-600 to-purple-600 blur-xl opacity-70"
              animate={{
                scale: [1, 1.2, 1],
                opacity: [0.7, 0.9, 0.7]
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: 'easeInOut'
              }}
            />
            
            {/* Button */}
            <div className="relative h-16 w-16 rounded-full bg-gradient-to-br from-violet-600 to-purple-700 flex items-center justify-center shadow-2xl border border-violet-400/50">
              <Sparkles className="h-7 w-7 text-white" />
            </div>

            {/* Tooltip */}
            <div className="absolute bottom-full mb-2 right-0 px-3 py-1.5 bg-black/90 text-white text-sm rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
              Create AI Swarm
            </div>
          </motion.button>
        ) : (
          <motion.div
            key="form"
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.8, opacity: 0 }}
            className="bg-black/95 backdrop-blur-xl border border-violet-500/30 rounded-2xl p-6 w-96 shadow-2xl"
          >
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-violet-600 to-purple-700 flex items-center justify-center">
                  <Zap className="h-4 w-4 text-white" />
                </div>
                <h3 className="text-white font-semibold">AI Swarm Creator</h3>
              </div>
              <button
                onClick={() => setIsExpanded(false)}
                className="text-white/50 hover:text-white transition-colors"
              >
                ✕
              </button>
            </div>

            {/* Response */}
            <AnimatePresence>
              {response && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className={`mb-4 p-3 rounded-lg border ${
                    response.status === 'success'
                      ? 'bg-green-500/10 border-green-500/30 text-green-400'
                      : response.status === 'needs_clarification'
                      ? 'bg-yellow-500/10 border-yellow-500/30 text-yellow-400'
                      : 'bg-red-500/10 border-red-500/30 text-red-400'
                  }`}
                >
                  <div className="flex items-start gap-2">
                    {response.status === 'success' ? (
                      <CheckCircle2 className="h-5 w-5 flex-shrink-0 mt-0.5" />
                    ) : (
                      <AlertCircle className="h-5 w-5 flex-shrink-0 mt-0.5" />
                    )}
                    <div className="text-sm">{response.message}</div>
                  </div>
                  
                  {response.status === 'success' && response.planner_url && (
                    <div className="mt-2 text-xs opacity-70">
                      Redirecting to planner...
                    </div>
                  )}
                </motion.div>
              )}
            </AnimatePresence>

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="text-white/70 text-sm mb-2 block">
                  Describe your project
                </label>
                <textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="E.g., Build an e-commerce store with Stripe..."
                  className="w-full h-24 bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white placeholder-white/40 focus:outline-none focus:border-violet-500/50 resize-none"
                  disabled={isSubmitting}
                />
              </div>

              {/* Examples */}
              <div className="space-y-1">
                <div className="text-white/50 text-xs">Try these:</div>
                <div className="flex flex-wrap gap-1">
                  {examples.map((example, i) => (
                    <button
                      key={i}
                      type="button"
                      onClick={() => setInput(example)}
                      className="text-xs px-2 py-1 bg-violet-500/10 hover:bg-violet-500/20 text-violet-300 rounded border border-violet-500/30 transition-colors"
                      disabled={isSubmitting}
                    >
                      {example.split(' ').slice(0, 3).join(' ')}...
                    </button>
                  ))}
                </div>
              </div>

              {/* Submit */}
              <Button
                type="submit"
                disabled={!input.trim() || isSubmitting}
                className="w-full bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-700 hover:to-purple-700 text-white font-medium py-2 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Creating Swarm...
                  </>
                ) : (
                  <>
                    <Zap className="h-4 w-4 mr-2" />
                    Create AI Swarm
                  </>
                )}
              </Button>
            </form>

            {/* Footer */}
            <div className="mt-4 pt-4 border-t border-white/10 text-xs text-white/40 text-center">
              Grok-4-Fast will break down your scope into tasks
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
