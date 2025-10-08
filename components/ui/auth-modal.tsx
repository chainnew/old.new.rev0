"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Github, Mail, X, Sparkles } from "lucide-react";

interface AuthModalProps {
  onClose: () => void;
}

export function AuthModal({ onClose }: AuthModalProps) {
  const [isLoading, setIsLoading] = useState<string | null>(null);

  const handleOAuthLogin = async (provider: 'github' | 'google' | 'xai') => {
    setIsLoading(provider);
    
    // Simulate OAuth redirect
    setTimeout(() => {
      console.log(`Logging in with ${provider}...`);
      // In production: window.location.href = `/api/auth/signin/${provider}`
      setIsLoading(null);
    }, 1500);
  };

  return (
    <motion.div
      className="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 backdrop-blur-sm"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={onClose}
    >
      <motion.div
        className="w-[450px] bg-gradient-to-br from-black via-gray-900 to-black border border-white/10 rounded-2xl shadow-2xl overflow-hidden"
        initial={{ scale: 0.9, y: 20 }}
        animate={{ scale: 1, y: 0 }}
        exit={{ scale: 0.9, y: 20 }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="relative px-8 pt-8 pb-6">
          <button
            onClick={onClose}
            className="absolute top-4 right-4 p-2 rounded-lg hover:bg-white/10 transition-colors"
          >
            <X className="w-4 h-4 text-white/70" />
          </button>
          
          <div className="text-center">
            <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center">
              <span className="text-2xl font-bold text-white">N</span>
            </div>
            <h2 className="text-2xl font-bold text-white mb-2">Welcome to old.new</h2>
            <p className="text-sm text-white/60">Sign in to access your AI workspace</p>
          </div>
        </div>

        {/* OAuth Buttons */}
        <div className="px-8 pb-8 space-y-3">
          {/* GitHub */}
          <OAuthButton
            icon={<Github className="w-5 h-5" />}
            label="Continue with GitHub"
            onClick={() => handleOAuthLogin('github')}
            isLoading={isLoading === 'github'}
            color="from-gray-700 to-gray-800"
          />

          {/* Google */}
          <OAuthButton
            icon={
              <svg className="w-5 h-5" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
            }
            label="Continue with Google"
            onClick={() => handleOAuthLogin('google')}
            isLoading={isLoading === 'google'}
            color="from-white to-gray-100"
            textColor="text-gray-900"
          />

          {/* xAI */}
          <OAuthButton
            icon={<Sparkles className="w-5 h-5" />}
            label="Continue with xAI"
            onClick={() => handleOAuthLogin('xai')}
            isLoading={isLoading === 'xai'}
            color="from-violet-600 to-purple-600"
          />

          {/* Divider */}
          <div className="relative py-4">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-white/10"></div>
            </div>
            <div className="relative flex justify-center text-xs">
              <span className="px-2 bg-gray-900 text-white/40">or</span>
            </div>
          </div>

          {/* Email */}
          <OAuthButton
            icon={<Mail className="w-5 h-5" />}
            label="Continue with Email"
            onClick={() => {}}
            isLoading={false}
            color="from-white/10 to-white/5"
            border
          />
        </div>

        {/* Footer */}
        <div className="px-8 py-4 bg-white/5 border-t border-white/10">
          <p className="text-xs text-center text-white/40">
            By continuing, you agree to our{' '}
            <a href="#" className="text-violet-400 hover:text-violet-300">Terms</a>
            {' '}and{' '}
            <a href="#" className="text-violet-400 hover:text-violet-300">Privacy Policy</a>
          </p>
        </div>
      </motion.div>
    </motion.div>
  );
}

interface OAuthButtonProps {
  icon: React.ReactNode;
  label: string;
  onClick: () => void;
  isLoading: boolean;
  color: string;
  textColor?: string;
  border?: boolean;
}

function OAuthButton({ icon, label, onClick, isLoading, color, textColor = "text-white", border }: OAuthButtonProps) {
  return (
    <motion.button
      onClick={onClick}
      disabled={isLoading}
      className={`w-full flex items-center justify-center gap-3 px-6 py-3 rounded-lg bg-gradient-to-r ${color} ${textColor} font-medium transition-all ${
        border ? 'border border-white/20' : ''
      } ${isLoading ? 'opacity-50 cursor-not-allowed' : 'hover:scale-[1.02] active:scale-[0.98]'}`}
      whileHover={{ scale: isLoading ? 1 : 1.02 }}
      whileTap={{ scale: isLoading ? 1 : 0.98 }}
    >
      {isLoading ? (
        <motion.div
          className="w-5 h-5 border-2 border-current border-t-transparent rounded-full"
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
        />
      ) : (
        icon
      )}
      <span className="text-sm">{label}</span>
    </motion.button>
  );
}
