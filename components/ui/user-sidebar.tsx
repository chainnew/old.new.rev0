"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { getTheme, loadTheme } from "@/lib/themes";
import { 
  User, 
  FolderKanban, 
  MessageSquare, 
  Bell, 
  Settings, 
  HelpCircle,
  LogOut,
  ChevronRight,
  Hash,
  Users,
  Github,
  Sparkles,
  Shield
} from "lucide-react";

interface UserSidebarProps {
  onOpenSettings: () => void;
  onOpenMessages: () => void;
  onOpenChannel: () => void;
  onOpenGitHub: () => void;
  onOpenAuth: () => void;
  onOpenAIChat: () => void;
  onOpenAdmin: () => void;
}

export function UserSidebar({ onOpenSettings, onOpenMessages, onOpenChannel, onOpenGitHub, onOpenAuth, onOpenAIChat, onOpenAdmin }: UserSidebarProps) {
  const [unreadMessages] = useState(3);
  const [unreadNotifications] = useState(5);
  const [currentTheme, setCurrentTheme] = useState('midnight');

  useEffect(() => {
    const savedTheme = loadTheme();
    setCurrentTheme(savedTheme);
    
    // Listen for theme changes
    const handleStorage = () => {
      const theme = loadTheme();
      setCurrentTheme(theme);
    };
    
    window.addEventListener('storage', handleStorage);
    // Also check periodically for theme changes
    const interval = setInterval(handleStorage, 500);
    
    return () => {
      window.removeEventListener('storage', handleStorage);
      clearInterval(interval);
    };
  }, []);

  const theme = getTheme(currentTheme);

  return (
    <motion.div
      className="fixed left-0 top-0 right-0 z-[60] backdrop-blur-xl border-b"
      style={{
        backgroundColor: `${theme.panelBg}`,
        borderColor: theme.borderColor
      }}
    >
      <div className="flex items-center justify-between px-6 py-3">
        {/* Left: Avatar */}
        <button
          onClick={onOpenAuth}
          className="flex items-center gap-2 cursor-pointer hover:bg-white/5 rounded-lg px-3 py-1.5 transition-colors"
        >
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center shadow-lg flex-shrink-0">
            <User className="w-4 h-4 text-white" />
          </div>
          <span className="text-white font-medium text-sm">Sign In</span>
        </button>

        {/* Center: Navigation Items */}
        <div className="flex items-center gap-1">
          <NavItem icon={<Sparkles className="w-4 h-4" />} label="AI Chat" onClick={onOpenAIChat} highlight />
          <NavItem icon={<FolderKanban className="w-4 h-4" />} label="Projects" onClick={() => {}} />
          <NavItem icon={<MessageSquare className="w-4 h-4" />} label="Messages" badge={unreadMessages} onClick={onOpenMessages} />
          <NavItem icon={<Hash className="w-4 h-4" />} label="old.new" badge={12} onClick={onOpenChannel} highlight />
          <NavItem icon={<Users className="w-4 h-4" />} label="Community" onClick={() => {}} />
          <NavItem icon={<Github className="w-4 h-4" />} label="GitHub" onClick={onOpenGitHub} highlight />
          <NavItem icon={<Bell className="w-4 h-4" />} label="Notifications" badge={unreadNotifications} onClick={() => {}} />
          
          <div className="w-px h-6 bg-white/10" />
          
          <NavItem icon={<Shield className="w-4 h-4" />} label="Admin" onClick={onOpenAdmin} highlight />
          <NavItem icon={<Settings className="w-4 h-4" />} label="Settings" onClick={onOpenSettings} />
          <NavItem icon={<HelpCircle className="w-4 h-4" />} label="Support" onClick={() => {}} />
        </div>

        {/* Right: Logout */}
        <NavItem icon={<LogOut className="w-4 h-4" />} label="Logout" onClick={() => {}} danger />
      </div>
    </motion.div>
  );
}

interface NavItemProps {
  icon: React.ReactNode;
  label: string;
  badge?: number;
  onClick: () => void;
  highlight?: boolean;
  danger?: boolean;
}

function NavItem({ icon, label, badge, onClick, highlight, danger }: NavItemProps) {
  return (
    <motion.button
      onClick={onClick}
      className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-all relative text-sm ${
        danger 
          ? "hover:bg-red-500/10 text-red-400 hover:text-red-300"
          : highlight
          ? "bg-violet-500/10 text-violet-300 hover:bg-violet-500/20"
          : "hover:bg-white/5 text-white/60 hover:text-white"
      }`}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      title={label}
    >
      <div className="relative">
        {icon}
        {badge && badge > 0 && (
          <div className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full flex items-center justify-center">
            <span className="text-[9px] font-bold text-white">{badge > 9 ? '9+' : badge}</span>
          </div>
        )}
      </div>
      <span className="font-medium hidden xl:inline">{label}</span>
    </motion.button>
  );
}
