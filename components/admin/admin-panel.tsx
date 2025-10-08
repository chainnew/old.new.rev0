"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { getTheme, loadTheme } from "@/lib/themes";
import {
  Users,
  Shield,
  Database,
  Activity,
  Mail,
  Settings,
  AlertCircle,
  TrendingUp,
  Key,
  Smartphone,
  Lock,
  Search,
  Filter,
  Download,
  RefreshCw,
  BarChart3,
  Zap
} from "lucide-react";

interface AdminPanelProps {
  onClose: () => void;
}

export function AdminPanel({ onClose }: AdminPanelProps) {
  const [activeSection, setActiveSection] = useState<'users' | 'security' | 'database' | 'analytics' | 'support' | 'settings' | 'errors' | 'agents'>('users');
  const [currentTheme, setCurrentTheme] = useState('midnight');

  useEffect(() => {
    const savedTheme = loadTheme();
    setCurrentTheme(savedTheme);
    
    const handleStorage = () => {
      const theme = loadTheme();
      setCurrentTheme(theme);
    };
    
    window.addEventListener('storage', handleStorage);
    const interval = setInterval(handleStorage, 500);
    
    return () => {
      window.removeEventListener('storage', handleStorage);
      clearInterval(interval);
    };
  }, []);

  const theme = getTheme(currentTheme);

  return (
    <motion.div
      className="fixed inset-0 z-[100] bg-black/60 backdrop-blur-sm flex items-center justify-end"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={onClose}
    >
      <motion.div
        className="h-full w-[1200px] backdrop-blur-xl border-l shadow-2xl flex"
        style={{
          backgroundColor: theme.panelBg,
          borderColor: theme.borderColor
        }}
        initial={{ x: 1200 }}
        animate={{ x: 0 }}
        exit={{ x: 1200 }}
        transition={{ type: "spring", stiffness: 300, damping: 30 }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Sidebar */}
        <div className="w-64 border-r p-6" style={{ backgroundColor: 'rgba(0,0,0,0.3)', borderColor: theme.borderColor }}>
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-white mb-1">Admin Panel</h1>
          <p className="text-xs text-white/50">System Management</p>
        </div>

        <nav className="space-y-2">
          <NavButton
            icon={<Users className="w-5 h-5" />}
            label="User Management"
            isActive={activeSection === 'users'}
            onClick={() => setActiveSection('users')}
            badge={1247}
          />
          <NavButton
            icon={<Shield className="w-5 h-5" />}
            label="Security & 2FA"
            isActive={activeSection === 'security'}
            onClick={() => setActiveSection('security')}
          />
          <NavButton
            icon={<BarChart3 className="w-5 h-5" />}
            label="Analytics"
            isActive={activeSection === 'analytics'}
            onClick={() => setActiveSection('analytics')}
          />
          <NavButton
            icon={<Zap className="w-5 h-5" />}
            label="Agent Config"
            isActive={activeSection === 'agents'}
            onClick={() => setActiveSection('agents')}
          />
          <NavButton
            icon={<Database className="w-5 h-5" />}
            label="Database"
            isActive={activeSection === 'database'}
            onClick={() => setActiveSection('database')}
          />
          <NavButton
            icon={<AlertCircle className="w-5 h-5" />}
            label="Error Logs"
            isActive={activeSection === 'errors'}
            onClick={() => setActiveSection('errors')}
            badge={12}
            badgeColor="red"
          />
          <NavButton
            icon={<Mail className="w-5 h-5" />}
            label="Support Tickets"
            isActive={activeSection === 'support'}
            onClick={() => setActiveSection('support')}
            badge={8}
            badgeColor="yellow"
          />
          <NavButton
            icon={<Settings className="w-5 h-5" />}
            label="Settings"
            isActive={activeSection === 'settings'}
            onClick={() => setActiveSection('settings')}
          />
        </nav>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-8">
          {activeSection === 'users' && <UserManagement />}
          {activeSection === 'security' && <SecuritySettings />}
          {activeSection === 'analytics' && <Analytics />}
          {activeSection === 'agents' && <AgentConfig />}
          {activeSection === 'database' && <DatabaseViewer />}
          {activeSection === 'errors' && <ErrorLogs />}
          {activeSection === 'support' && <SupportTickets />}
          {activeSection === 'settings' && <SystemSettings />}
        </div>
      </div>
      </motion.div>
    </motion.div>
  );
}

function NavButton({ icon, label, isActive, onClick, badge, badgeColor = 'violet' }: any) {
  return (
    <button
      onClick={onClick}
      className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
        isActive
          ? 'bg-violet-500/20 text-violet-300'
          : 'text-white/60 hover:bg-white/5 hover:text-white'
      }`}
    >
      {icon}
      <span className="flex-1 text-left text-sm font-medium">{label}</span>
      {badge && (
        <span className={`px-2 py-0.5 text-xs rounded-full ${
          badgeColor === 'red' ? 'bg-red-500/20 text-red-300' :
          badgeColor === 'yellow' ? 'bg-yellow-500/20 text-yellow-300' :
          'bg-violet-500/20 text-violet-300'
        }`}>
          {badge}
        </span>
      )}
    </button>
  );
}

function UserManagement() {
  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-white">User Management</h2>
          <p className="text-sm text-white/50 mt-1">Manage all registered users</p>
        </div>
        <div className="flex gap-2">
          <button className="px-4 py-2 bg-white/5 hover:bg-white/10 text-white rounded-lg text-sm flex items-center gap-2">
            <Download className="w-4 h-4" />
            Export CSV
          </button>
          <button className="px-4 py-2 bg-violet-500 hover:bg-violet-600 text-white rounded-lg text-sm flex items-center gap-2">
            <Users className="w-4 h-4" />
            Add User
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <StatCard label="Total Users" value="1,247" change="+12%" />
        <StatCard label="Active Today" value="423" change="+5%" />
        <StatCard label="Premium" value="89" change="+8%" />
        <StatCard label="Banned" value="3" change="-2%" color="red" />
      </div>

      {/* Search & Filters */}
      <div className="flex gap-3 mb-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/40" />
          <input
            type="text"
            placeholder="Search users by name, email, or ID..."
            className="w-full pl-10 pr-4 py-2 bg-white/5 border border-white/10 rounded-lg text-sm text-white placeholder-white/30 focus:outline-none focus:border-violet-500/50"
          />
        </div>
        <button className="px-4 py-2 bg-white/5 hover:bg-white/10 text-white rounded-lg text-sm flex items-center gap-2">
          <Filter className="w-4 h-4" />
          Filters
        </button>
      </div>

      {/* User Table */}
      <div className="bg-white/5 rounded-lg border border-white/10 overflow-hidden">
        <table className="w-full">
          <thead className="bg-white/5">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-white/70">User</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-white/70">Email</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-white/70">Role</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-white/70">Status</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-white/70">Joined</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-white/70">Actions</th>
            </tr>
          </thead>
          <tbody>
            {mockUsers.map((user) => (
              <tr key={user.id} className="border-t border-white/5 hover:bg-white/5">
                <td className="px-4 py-3 text-sm text-white">{user.name}</td>
                <td className="px-4 py-3 text-sm text-white/60">{user.email}</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    user.role === 'admin' ? 'bg-red-500/20 text-red-300' :
                    user.role === 'premium' ? 'bg-violet-500/20 text-violet-300' :
                    'bg-white/10 text-white/60'
                  }`}>
                    {user.role}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    user.status === 'active' ? 'bg-green-500/20 text-green-300' :
                    user.status === 'suspended' ? 'bg-yellow-500/20 text-yellow-300' :
                    'bg-red-500/20 text-red-300'
                  }`}>
                    {user.status}
                  </span>
                </td>
                <td className="px-4 py-3 text-sm text-white/60">{user.joined}</td>
                <td className="px-4 py-3">
                  <button className="text-sm text-violet-400 hover:text-violet-300">Edit</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function SecuritySettings() {
  return (
    <div>
      <h2 className="text-2xl font-bold text-white mb-6">Security & Authentication</h2>

      <div className="grid grid-cols-2 gap-6">
        {/* 2FA Settings */}
        <div className="bg-white/5 rounded-lg border border-white/10 p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-lg bg-violet-500/20 flex items-center justify-center">
              <Shield className="w-5 h-5 text-violet-400" />
            </div>
            <div>
              <h3 className="font-semibold text-white">Two-Factor Authentication</h3>
              <p className="text-xs text-white/50">Require 2FA for all admins</p>
            </div>
          </div>
          <div className="space-y-3">
            <ToggleOption label="Enforce 2FA for Admins" enabled={true} />
            <ToggleOption label="Allow SMS 2FA" enabled={true} />
            <ToggleOption label="Allow Authenticator Apps" enabled={true} />
            <ToggleOption label="Allow Security Keys" enabled={false} />
          </div>
        </div>

        {/* Security Keys */}
        <div className="bg-white/5 rounded-lg border border-white/10 p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center">
              <Key className="w-5 h-5 text-blue-400" />
            </div>
            <div>
              <h3 className="font-semibold text-white">Security Keys (WebAuthn)</h3>
              <p className="text-xs text-white/50">Hardware security keys</p>
            </div>
          </div>
          <div className="space-y-2">
            <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
              <span className="text-sm text-white">YubiKey 5C</span>
              <span className="text-xs text-green-400">Active</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
              <span className="text-sm text-white">Google Titan</span>
              <span className="text-xs text-white/40">Inactive</span>
            </div>
          </div>
        </div>

        {/* Phone Numbers */}
        <div className="bg-white/5 rounded-lg border border-white/10 p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-lg bg-green-500/20 flex items-center justify-center">
              <Smartphone className="w-5 h-5 text-green-400" />
            </div>
            <div>
              <h3 className="font-semibold text-white">SMS Verification</h3>
              <p className="text-xs text-white/50">Phone number authentication</p>
            </div>
          </div>
          <input
            type="tel"
            placeholder="+1 (555) 123-4567"
            className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-sm text-white placeholder-white/30 focus:outline-none focus:border-violet-500/50"
          />
        </div>

        {/* PIN Settings */}
        <div className="bg-white/5 rounded-lg border border-white/10 p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-lg bg-yellow-500/20 flex items-center justify-center">
              <Lock className="w-5 h-5 text-yellow-400" />
            </div>
            <div>
              <h3 className="font-semibold text-white">Admin PIN</h3>
              <p className="text-xs text-white/50">Additional security layer</p>
            </div>
          </div>
          <div className="space-y-3">
            <input
              type="password"
              placeholder="Enter 6-digit PIN"
              maxLength={6}
              className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-sm text-white placeholder-white/30 focus:outline-none focus:border-violet-500/50"
            />
            <button className="w-full py-2 bg-violet-500 hover:bg-violet-600 text-white rounded-lg text-sm">
              Update PIN
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function Analytics() {
  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-white">Analytics & Tokenomics</h2>
        <button className="px-4 py-2 bg-white/5 hover:bg-white/10 text-white rounded-lg text-sm flex items-center gap-2">
          <RefreshCw className="w-4 h-4" />
          Refresh
        </button>
      </div>

      <div className="grid grid-cols-4 gap-4 mb-6">
        <StatCard label="Total Revenue" value="$47,239" change="+18%" />
        <StatCard label="API Calls" value="2.4M" change="+23%" />
        <StatCard label="Tokens Used" value="15.7B" change="+31%" />
        <StatCard label="Avg Response" value="1.2s" change="-5%" color="green" />
      </div>

      {/* Charts Placeholder */}
      <div className="grid grid-cols-2 gap-6">
        <div className="bg-white/5 rounded-lg border border-white/10 p-6 h-64 flex items-center justify-center">
          <div className="text-center text-white/40">
            <BarChart3 className="w-12 h-12 mx-auto mb-2" />
            <p className="text-sm">Revenue Chart</p>
          </div>
        </div>
        <div className="bg-white/5 rounded-lg border border-white/10 p-6 h-64 flex items-center justify-center">
          <div className="text-center text-white/40">
            <TrendingUp className="w-12 h-12 mx-auto mb-2" />
            <p className="text-sm">Usage Trends</p>
          </div>
        </div>
      </div>
    </div>
  );
}

function AgentConfig() {
  return (
    <div>
      <h2 className="text-2xl font-bold text-white mb-6">AI Agent Configuration</h2>
      <div className="space-y-4">
        <ConfigSlider label="Temperature" value={0.7} min={0} max={1} step={0.1} />
        <ConfigSlider label="Top P" value={0.9} min={0} max={1} step={0.1} />
        <ConfigSlider label="Max Tokens" value={2048} min={100} max={4000} step={100} />
        <ConfigSlider label="Frequency Penalty" value={0.5} min={0} max={2} step={0.1} />
      </div>
    </div>
  );
}

function DatabaseViewer() {
  return (
    <div>
      <h2 className="text-2xl font-bold text-white mb-6">Database Viewer</h2>
      <div className="bg-white/5 rounded-lg border border-white/10 p-6">
        <p className="text-white/60 text-sm">PostgreSQL Database: <span className="text-green-400">Connected</span></p>
        <div className="mt-4 space-y-2">
          <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
            <span className="text-white">users</span>
            <span className="text-white/40 text-sm">1,247 rows</span>
          </div>
          <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
            <span className="text-white">conversations</span>
            <span className="text-white/40 text-sm">8,942 rows</span>
          </div>
          <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
            <span className="text-white">messages</span>
            <span className="text-white/40 text-sm">124,531 rows</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function ErrorLogs() {
  return (
    <div>
      <h2 className="text-2xl font-bold text-white mb-6">Error Logs</h2>
      <div className="space-y-2">
        {mockErrors.map((error) => (
          <div key={error.id} className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
            <div className="flex items-start justify-between mb-2">
              <span className="text-red-400 text-sm font-mono">{error.code}</span>
              <span className="text-xs text-white/40">{error.time}</span>
            </div>
            <p className="text-white text-sm">{error.message}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function SupportTickets() {
  return (
    <div>
      <h2 className="text-2xl font-bold text-white mb-6">Support Tickets</h2>
      <div className="space-y-2">
        {mockTickets.map((ticket) => (
          <div key={ticket.id} className="bg-white/5 border border-white/10 rounded-lg p-4 hover:bg-white/10 cursor-pointer">
            <div className="flex items-start justify-between mb-2">
              <div>
                <span className="text-white font-medium">{ticket.subject}</span>
                <p className="text-sm text-white/60 mt-1">{ticket.user}</p>
              </div>
              <span className={`px-2 py-1 text-xs rounded-full ${
                ticket.status === 'open' ? 'bg-yellow-500/20 text-yellow-300' :
                ticket.status === 'in-progress' ? 'bg-blue-500/20 text-blue-300' :
                'bg-green-500/20 text-green-300'
              }`}>
                {ticket.status}
              </span>
            </div>
            <p className="text-xs text-white/40">{ticket.time}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function SystemSettings() {
  return (
    <div>
      <h2 className="text-2xl font-bold text-white mb-6">System Settings</h2>
      <div className="space-y-4">
        <ToggleOption label="Maintenance Mode" enabled={false} />
        <ToggleOption label="New User Registration" enabled={true} />
        <ToggleOption label="Email Notifications" enabled={true} />
        <ToggleOption label="API Rate Limiting" enabled={true} />
      </div>
    </div>
  );
}

function StatCard({ label, value, change, color = 'green' }: any) {
  return (
    <div className="bg-white/5 rounded-lg border border-white/10 p-4">
      <p className="text-xs text-white/50 mb-1">{label}</p>
      <p className="text-2xl font-bold text-white mb-1">{value}</p>
      <p className={`text-xs ${color === 'green' ? 'text-green-400' : color === 'red' ? 'text-red-400' : 'text-white/60'}`}>
        {change}
      </p>
    </div>
  );
}

function ToggleOption({ label, enabled }: any) {
  return (
    <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
      <span className="text-sm text-white">{label}</span>
      <div className={`w-12 h-6 rounded-full transition-colors ${enabled ? 'bg-violet-500' : 'bg-white/20'}`}>
        <div className={`w-4 h-4 bg-white rounded-full mt-1 transition-transform ${enabled ? 'ml-7' : 'ml-1'}`} />
      </div>
    </div>
  );
}

function ConfigSlider({ label, value, min, max, step }: any) {
  return (
    <div className="bg-white/5 rounded-lg border border-white/10 p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-white">{label}</span>
        <span className="text-sm text-violet-400">{value}</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        defaultValue={value}
        className="w-full accent-violet-500"
      />
    </div>
  );
}

const mockUsers = [
  { id: 1, name: 'John Doe', email: 'john@example.com', role: 'admin', status: 'active', joined: '2024-01-15' },
  { id: 2, name: 'Jane Smith', email: 'jane@example.com', role: 'premium', status: 'active', joined: '2024-02-20' },
  { id: 3, name: 'Bob Wilson', email: 'bob@example.com', role: 'user', status: 'active', joined: '2024-03-10' },
  { id: 4, name: 'Alice Brown', email: 'alice@example.com', role: 'user', status: 'suspended', joined: '2024-01-05' },
];

const mockErrors = [
  { id: 1, code: 'ERR_API_TIMEOUT', message: 'API request timeout after 30s', time: '2 mins ago' },
  { id: 2, code: 'ERR_DB_CONNECTION', message: 'Database connection pool exhausted', time: '15 mins ago' },
];

const mockTickets = [
  { id: 1, subject: 'Cannot login to account', user: 'user@example.com', status: 'open', time: '5 mins ago' },
  { id: 2, subject: 'Billing issue with subscription', user: 'customer@example.com', status: 'in-progress', time: '1 hour ago' },
];
