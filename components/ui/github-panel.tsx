"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Github, 
  X, 
  GitBranch, 
  GitCommit, 
  GitPullRequest, 
  Star, 
  Eye,
  GitFork,
  Calendar,
  Code,
  FileCode,
  CheckCircle2,
  Circle,
  AlertCircle,
  Search,
  RefreshCw
} from "lucide-react";

interface GitHubPanelProps {
  onClose: () => void;
}

interface Repo {
  id: string;
  name: string;
  description: string;
  language: string;
  stars: number;
  forks: number;
  isPrivate: boolean;
  updatedAt: string;
}

interface Commit {
  id: string;
  message: string;
  author: string;
  timestamp: string;
  branch: string;
  sha: string;
}

interface PullRequest {
  id: string;
  title: string;
  number: number;
  status: 'open' | 'closed' | 'merged';
  author: string;
  createdAt: string;
}

const mockRepos: Repo[] = [
  { id: '1', name: 'old.new.rev0', description: 'AI-powered IDE with Grok integration', language: 'TypeScript', stars: 125, forks: 34, isPrivate: false, updatedAt: '2h ago' },
  { id: '2', name: 'ai-chat-ui', description: 'Beautiful chat interface for AI apps', language: 'React', stars: 89, forks: 12, isPrivate: false, updatedAt: '1d ago' },
  { id: '3', name: 'mobile-simulator', description: 'iPhone & Android simulators', language: 'TypeScript', stars: 45, forks: 8, isPrivate: true, updatedAt: '3d ago' },
];

const mockCommits: Commit[] = [
  { id: '1', message: 'feat: Add GitHub integration panel', author: 'You', timestamp: '2m ago', branch: 'main', sha: 'a1b2c3d' },
  { id: '2', message: 'fix: XSS vulnerabilities in iframes', author: 'You', timestamp: '1h ago', branch: 'main', sha: 'e4f5g6h' },
  { id: '3', message: 'feat: User authentication with OAuth', author: 'You', timestamp: '3h ago', branch: 'feature/auth', sha: 'i7j8k9l' },
];

const mockPRs: PullRequest[] = [
  { id: '1', title: 'Add messaging system and channels', number: 42, status: 'open', author: 'You', createdAt: '1h ago' },
  { id: '2', title: 'Security fixes for iframe URLs', number: 41, status: 'merged', author: 'You', createdAt: '2h ago' },
  { id: '3', title: 'Theme system with 10 backgrounds', number: 40, status: 'closed', author: 'Collaborator', createdAt: '1d ago' },
];

export function GitHubPanel({ onClose }: GitHubPanelProps) {
  const [activeTab, setActiveTab] = useState<'repos' | 'commits' | 'prs'>('repos');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRepo, setSelectedRepo] = useState<string | null>(null);

  return (
    <motion.div
      className="fixed inset-0 z-[90] flex items-center justify-center bg-black/60 backdrop-blur-sm"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={onClose}
    >
      <motion.div
        className="w-[1100px] h-[700px] bg-black/90 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl overflow-hidden flex flex-col"
        initial={{ scale: 0.9, y: 20 }}
        animate={{ scale: 1, y: 0 }}
        exit={{ scale: 0.9, y: 20 }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="px-6 py-4 border-b border-white/10 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-gray-700 to-gray-900 flex items-center justify-center">
              <Github className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-white">GitHub Integration</h2>
              <p className="text-xs text-white/50">Connected as @your-username</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button className="p-2 rounded-lg hover:bg-white/5 transition-colors">
              <RefreshCw className="w-4 h-4 text-white/70" />
            </button>
            <button onClick={onClose} className="p-2 rounded-lg hover:bg-white/10 transition-colors">
              <X className="w-5 h-5 text-white/70" />
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="px-6 py-3 border-b border-white/10 flex items-center gap-6">
          <TabButton
            label="Repositories"
            icon={<Code className="w-4 h-4" />}
            isActive={activeTab === 'repos'}
            onClick={() => setActiveTab('repos')}
            count={mockRepos.length}
          />
          <TabButton
            label="Commits"
            icon={<GitCommit className="w-4 h-4" />}
            isActive={activeTab === 'commits'}
            onClick={() => setActiveTab('commits')}
            count={mockCommits.length}
          />
          <TabButton
            label="Pull Requests"
            icon={<GitPullRequest className="w-4 h-4" />}
            isActive={activeTab === 'prs'}
            onClick={() => setActiveTab('prs')}
            count={mockPRs.length}
          />
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {activeTab === 'repos' && <ReposTab repos={mockRepos} searchQuery={searchQuery} setSearchQuery={setSearchQuery} />}
          {activeTab === 'commits' && <CommitsTab commits={mockCommits} />}
          {activeTab === 'prs' && <PRsTab prs={mockPRs} />}
        </div>
      </motion.div>
    </motion.div>
  );
}

function TabButton({ label, icon, isActive, onClick, count }: any) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
        isActive ? 'bg-violet-500/20 text-violet-300' : 'text-white/60 hover:bg-white/5 hover:text-white'
      }`}
    >
      {icon}
      <span className="text-sm font-medium">{label}</span>
      <span className={`text-xs px-2 py-0.5 rounded-full ${
        isActive ? 'bg-violet-500/30' : 'bg-white/10'
      }`}>{count}</span>
    </button>
  );
}

function ReposTab({ repos, searchQuery, setSearchQuery }: any) {
  return (
    <div>
      {/* Search */}
      <div className="mb-6 relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/40" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search repositories..."
          className="w-full pl-10 pr-4 py-2 bg-white/5 border border-white/10 rounded-lg text-sm text-white placeholder-white/30 focus:outline-none focus:border-violet-500/50"
        />
      </div>

      {/* Repos Grid */}
      <div className="grid grid-cols-2 gap-4">
        {repos.map((repo: Repo) => (
          <motion.div
            key={repo.id}
            className="p-4 rounded-lg bg-white/5 border border-white/10 hover:border-violet-500/30 transition-all cursor-pointer"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-2">
                <FileCode className="w-5 h-5 text-violet-400" />
                <h3 className="font-semibold text-white text-sm">{repo.name}</h3>
              </div>
              {repo.isPrivate && (
                <span className="px-2 py-0.5 text-[10px] bg-yellow-500/20 text-yellow-300 rounded-full">Private</span>
              )}
            </div>
            <p className="text-xs text-white/50 mb-3 line-clamp-2">{repo.description}</p>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3 text-xs text-white/40">
                <span className="flex items-center gap-1">
                  <Circle className="w-2 h-2 fill-blue-400 text-blue-400" />
                  {repo.language}
                </span>
                <span className="flex items-center gap-1">
                  <Star className="w-3 h-3" />
                  {repo.stars}
                </span>
                <span className="flex items-center gap-1">
                  <GitFork className="w-3 h-3" />
                  {repo.forks}
                </span>
              </div>
              <span className="text-xs text-white/40">{repo.updatedAt}</span>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}

function CommitsTab({ commits }: any) {
  return (
    <div className="space-y-3">
      {commits.map((commit: Commit) => (
        <motion.div
          key={commit.id}
          className="p-4 rounded-lg bg-white/5 border border-white/10 hover:border-violet-500/30 transition-all"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center flex-shrink-0">
              <GitCommit className="w-4 h-4 text-white" />
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-white mb-1">{commit.message}</p>
              <div className="flex items-center gap-3 text-xs text-white/50">
                <span>{commit.author}</span>
                <span>•</span>
                <span className="flex items-center gap-1">
                  <GitBranch className="w-3 h-3" />
                  {commit.branch}
                </span>
                <span>•</span>
                <span className="font-mono">{commit.sha}</span>
                <span>•</span>
                <span>{commit.timestamp}</span>
              </div>
            </div>
          </div>
        </motion.div>
      ))}
    </div>
  );
}

function PRsTab({ prs }: any) {
  return (
    <div className="space-y-3">
      {prs.map((pr: PullRequest) => (
        <motion.div
          key={pr.id}
          className="p-4 rounded-lg bg-white/5 border border-white/10 hover:border-violet-500/30 transition-all"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="flex items-start gap-3">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
              pr.status === 'open' ? 'bg-green-500/20' :
              pr.status === 'merged' ? 'bg-violet-500/20' : 'bg-red-500/20'
            }`}>
              {pr.status === 'open' ? <Circle className="w-4 h-4 text-green-400" /> :
               pr.status === 'merged' ? <CheckCircle2 className="w-4 h-4 text-violet-400" /> :
               <AlertCircle className="w-4 h-4 text-red-400" />}
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <p className="text-sm font-medium text-white">{pr.title}</p>
                <span className="text-xs text-white/40">#{pr.number}</span>
              </div>
              <div className="flex items-center gap-3 text-xs text-white/50">
                <span className={`px-2 py-0.5 rounded-full ${
                  pr.status === 'open' ? 'bg-green-500/20 text-green-300' :
                  pr.status === 'merged' ? 'bg-violet-500/20 text-violet-300' : 'bg-red-500/20 text-red-300'
                }`}>
                  {pr.status.charAt(0).toUpperCase() + pr.status.slice(1)}
                </span>
                <span>{pr.author}</span>
                <span>•</span>
                <span>{pr.createdAt}</span>
              </div>
            </div>
          </div>
        </motion.div>
      ))}
    </div>
  );
}
