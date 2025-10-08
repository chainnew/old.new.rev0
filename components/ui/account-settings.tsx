"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, Palette, User, Bell, Shield, Sliders } from "lucide-react";
import { themes, Theme } from "@/lib/themes";
import { Check } from "lucide-react";

interface AccountSettingsProps {
  onClose: () => void;
  currentTheme: string;
  onThemeChange: (themeId: string) => void;
}

export function AccountSettings({ onClose, currentTheme, onThemeChange }: AccountSettingsProps) {
  const [activeTab, setActiveTab] = useState<'profile' | 'appearance' | 'notifications' | 'privacy'>('appearance');

  return (
    <motion.div
      className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={onClose}
    >
      <motion.div
        className="w-[900px] h-[600px] bg-black/90 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl overflow-hidden flex"
        initial={{ scale: 0.9, y: 20 }}
        animate={{ scale: 1, y: 0 }}
        exit={{ scale: 0.9, y: 20 }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Sidebar */}
        <div className="w-64 border-r border-white/10 p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-white">Settings</h2>
            <button
              onClick={onClose}
              className="p-1 rounded-lg hover:bg-white/10 transition-colors"
            >
              <X className="w-5 h-5 text-white/70" />
            </button>
          </div>

          <div className="space-y-1">
            <TabButton
              icon={<User className="w-5 h-5" />}
              label="Profile"
              isActive={activeTab === 'profile'}
              onClick={() => setActiveTab('profile')}
            />
            <TabButton
              icon={<Palette className="w-5 h-5" />}
              label="Appearance"
              isActive={activeTab === 'appearance'}
              onClick={() => setActiveTab('appearance')}
            />
            <TabButton
              icon={<Bell className="w-5 h-5" />}
              label="Notifications"
              isActive={activeTab === 'notifications'}
              onClick={() => setActiveTab('notifications')}
            />
            <TabButton
              icon={<Shield className="w-5 h-5" />}
              label="Privacy"
              isActive={activeTab === 'privacy'}
              onClick={() => setActiveTab('privacy')}
            />
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 p-8 overflow-y-auto">
          {activeTab === 'profile' && <ProfileTab />}
          {activeTab === 'appearance' && (
            <AppearanceTab currentTheme={currentTheme} onThemeChange={onThemeChange} />
          )}
          {activeTab === 'notifications' && <NotificationsTab />}
          {activeTab === 'privacy' && <PrivacyTab />}
        </div>
      </motion.div>
    </motion.div>
  );
}

function TabButton({ icon, label, isActive, onClick }: any) {
  return (
    <button
      onClick={onClick}
      className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
        isActive
          ? "bg-violet-500/20 text-violet-300"
          : "text-white/60 hover:bg-white/5 hover:text-white"
      }`}
    >
      {icon}
      <span className="text-sm font-medium">{label}</span>
    </button>
  );
}

function ProfileTab() {
  return (
    <div>
      <h3 className="text-2xl font-semibold text-white mb-6">Profile Settings</h3>
      <div className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-white/70 mb-2">Display Name</label>
          <input
            type="text"
            className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white placeholder-white/30 focus:outline-none focus:border-violet-500/50"
            placeholder="Your Name"
            defaultValue="Your Name"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-white/70 mb-2">Email</label>
          <input
            type="email"
            className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white placeholder-white/30 focus:outline-none focus:border-violet-500/50"
            placeholder="you@email.com"
            defaultValue="you@email.com"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-white/70 mb-2">Avatar</label>
          <div className="flex items-center gap-4">
            <div className="w-20 h-20 rounded-full bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center">
              <span className="text-white font-bold text-2xl">N</span>
            </div>
            <button className="px-4 py-2 bg-violet-500/20 hover:bg-violet-500/30 text-violet-300 rounded-lg text-sm font-medium transition-colors">
              Change Avatar
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function AppearanceTab({ currentTheme, onThemeChange }: { currentTheme: string; onThemeChange: (id: string) => void }) {
  return (
    <div>
      <h3 className="text-2xl font-semibold text-white mb-6">Appearance</h3>
      
      <div className="mb-8">
        <h4 className="text-sm font-medium text-white/70 mb-4">Theme</h4>
        <div className="grid grid-cols-3 gap-3">
          {themes.map((theme) => (
            <button
              key={theme.id}
              onClick={() => onThemeChange(theme.id)}
              className="relative group"
            >
              <div
                className={`rounded-lg overflow-hidden border-2 transition-all ${
                  currentTheme === theme.id ? "border-violet-500" : "border-white/10"
                }`}
              >
                <div
                  className={`h-20 bg-gradient-to-br ${theme.background} relative`}
                >
                  {currentTheme === theme.id && (
                    <div className="absolute top-2 right-2 w-6 h-6 rounded-full bg-violet-500 flex items-center justify-center">
                      <Check className="w-4 h-4 text-white" />
                    </div>
                  )}
                </div>
                <div className="p-2 bg-black/60">
                  <p className="text-xs font-medium text-white truncate">{theme.name}</p>
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      <div>
        <h4 className="text-sm font-medium text-white/70 mb-4">Chat Width</h4>
        <input
          type="range"
          min="600"
          max="1000"
          defaultValue="768"
          className="w-full accent-violet-500"
        />
      </div>
    </div>
  );
}

function NotificationsTab() {
  return (
    <div>
      <h3 className="text-2xl font-semibold text-white mb-6">Notifications</h3>
      <div className="space-y-4">
        <ToggleSetting label="Desktop Notifications" description="Show notifications on your desktop" />
        <ToggleSetting label="Message Sounds" description="Play sound when receiving messages" />
        <ToggleSetting label="Email Notifications" description="Receive email updates" />
        <ToggleSetting label="Channel Mentions" description="Notify when mentioned in channels" />
      </div>
    </div>
  );
}

function PrivacyTab() {
  return (
    <div>
      <h3 className="text-2xl font-semibold text-white mb-6">Privacy</h3>
      <div className="space-y-4">
        <ToggleSetting label="Show Online Status" description="Let others see when you're online" defaultChecked />
        <ToggleSetting label="Read Receipts" description="Show when you've read messages" defaultChecked />
        <ToggleSetting label="Allow DMs" description="Allow direct messages from anyone" defaultChecked />
        <ToggleSetting label="Public Profile" description="Make your profile visible to everyone" />
      </div>
    </div>
  );
}

function ToggleSetting({ label, description, defaultChecked }: any) {
  const [checked, setChecked] = useState(defaultChecked || false);

  return (
    <div className="flex items-center justify-between p-4 rounded-lg bg-white/5">
      <div>
        <p className="text-sm font-medium text-white">{label}</p>
        <p className="text-xs text-white/50 mt-1">{description}</p>
      </div>
      <button
        onClick={() => setChecked(!checked)}
        className={`relative w-12 h-6 rounded-full transition-colors ${
          checked ? "bg-violet-500" : "bg-white/20"
        }`}
      >
        <motion.div
          className="absolute top-1 w-4 h-4 bg-white rounded-full"
          animate={{ x: checked ? 26 : 2 }}
          transition={{ type: "spring", stiffness: 500, damping: 30 }}
        />
      </button>
    </div>
  );
}
