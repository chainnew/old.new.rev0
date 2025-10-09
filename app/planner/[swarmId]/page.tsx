'use client';

import { useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import Plan from '@/components/ui/agent-plan';

export default function SwarmPlannerPage() {
  const params = useParams();
  const router = useRouter();
  const swarmId = params.swarmId as string;

  useEffect(() => {
    // Save to recent swarms in localStorage
    const recentSwarms = JSON.parse(localStorage.getItem('recent_swarms') || '[]');
    if (!recentSwarms.includes(swarmId)) {
      recentSwarms.unshift(swarmId);
      // Keep only last 20
      const updated = recentSwarms.slice(0, 20);
      localStorage.setItem('recent_swarms', JSON.stringify(updated));
    }
  }, [swarmId]);

  return (
    <div className="min-h-screen bg-black text-white flex flex-col">
      {/* Header */}
      <div className="border-b border-white/10 bg-black/50 backdrop-blur-sm z-10 flex-shrink-0">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link
                href="/planner"
                className="flex items-center gap-2 text-white/60 hover:text-white transition-colors"
              >
                <ArrowLeft className="w-4 h-4" />
                <span className="text-sm">All Projects</span>
              </Link>
              <div className="h-4 w-px bg-white/10"></div>
              <div>
                <h1 className="text-lg font-semibold">Swarm Planner</h1>
                <p className="text-xs text-white/40 font-mono">
                  {swarmId.slice(0, 8)}...{swarmId.slice(-8)}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <a
                href={`http://localhost:8000/api/planner/${swarmId}`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-white/40 hover:text-violet-400 transition-colors font-mono"
              >
                View JSON
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* Planner Component */}
      <div className="flex-1 overflow-auto pb-32 bg-black">
        <div className="max-w-7xl mx-auto p-6 h-full">
          <Plan 
            swarmId={swarmId} 
            enablePolling={true} 
            pollingInterval={3000}
          />
        </div>
        {/* Extra space to ensure black covers bottom */}
        <div className="h-48 bg-black"></div>
      </div>
    </div>
  );
}
