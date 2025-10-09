'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Clock } from 'lucide-react';
import GlobalPlannerPanel from './GlobalPlannerPanel';

export default function GlobalPlannerToggle() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      {/* Floating Toggle Button */}
      <motion.button
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ delay: 0.5, type: 'spring', damping: 15 }}
        onClick={() => setIsOpen(!isOpen)}
        className={`fixed bottom-6 right-6 z-40 ${
          isOpen ? 'opacity-0 pointer-events-none' : 'opacity-100'
        } transition-opacity`}
        title="Open Swarm Planner"
      >
        <div className="relative group">
          <div className="absolute inset-0 bg-gradient-to-r from-violet-600 to-purple-600 rounded-full blur-lg opacity-75 group-hover:opacity-100 transition-opacity"></div>
          <div className="relative bg-gradient-to-r from-violet-500 to-purple-500 hover:from-violet-400 hover:to-purple-400 text-white p-4 rounded-full shadow-2xl transition-all transform hover:scale-110">
            <Clock className="w-6 h-6" />
          </div>
          
          {/* Pulse animation */}
          <div className="absolute inset-0 rounded-full bg-violet-500 animate-ping opacity-20"></div>
        </div>
      </motion.button>

      {/* Global Planner Panel */}
      <GlobalPlannerPanel isOpen={isOpen} onClose={() => setIsOpen(false)} />
    </>
  );
}
