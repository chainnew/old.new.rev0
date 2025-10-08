"use client";

import { motion, AnimatePresence } from "framer-motion";
import { themes, Theme } from "@/lib/themes";
import { Check, X } from "lucide-react";

interface ThemePickerProps {
  currentTheme: string;
  onThemeChange: (themeId: string) => void;
  onClose: () => void;
}

export function ThemePicker({ currentTheme, onThemeChange, onClose }: ThemePickerProps) {
  return (
    <motion.div
      className="fixed inset-0 z-[100] flex items-center justify-end bg-black/60 backdrop-blur-sm"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={onClose}
    >
      <motion.div
        className="h-full w-[400px] bg-black/80 backdrop-blur-xl border-l border-white/10 shadow-2xl overflow-hidden flex flex-col"
        initial={{ x: 400 }}
        animate={{ x: 0 }}
        exit={{ x: 400 }}
        transition={{ type: "spring", stiffness: 300, damping: 30 }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="px-4 py-3 border-b border-white/10 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-white">Choose Theme</h2>
            <p className="text-xs text-white/50 mt-0.5">10 themes available</p>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg hover:bg-white/10 transition-colors"
          >
            <X className="w-4 h-4 text-white/70" />
          </button>
        </div>

        {/* Theme Grid */}
        <div className="flex-1 p-4 overflow-y-auto">
          <div className="grid grid-cols-1 gap-3">
          {themes.map((theme) => (
            <motion.button
              key={theme.id}
              onClick={() => onThemeChange(theme.id)}
              className="relative group"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              {/* Preview Card */}
              <div className="relative rounded-xl overflow-hidden border-2 transition-all"
                style={{
                  borderColor: currentTheme === theme.id ? theme.accentColor : 'rgba(255, 255, 255, 0.1)'
                }}
              >
                {/* Background Preview */}
                <div 
                  className={`h-32 bg-gradient-to-br ${theme.background} relative overflow-hidden`}
                >
                  {/* Animated Dots Preview */}
                  <div className="absolute inset-0 flex items-center justify-center">
                    {[...Array(12)].map((_, i) => (
                      <motion.div
                        key={i}
                        className="absolute"
                        style={{
                          width: 3,
                          height: 3,
                          background: theme.dotColor,
                          borderRadius: '50%',
                          left: `${(i % 4) * 25 + 12}%`,
                          top: `${Math.floor(i / 4) * 33 + 16}%`,
                        }}
                        animate={{
                          opacity: [0.3, 0.8, 0.3],
                          scale: [1, 1.5, 1],
                        }}
                        transition={{
                          duration: 2,
                          repeat: Infinity,
                          delay: i * 0.1,
                        }}
                      />
                    ))}
                  </div>

                  {/* Selected Indicator */}
                  {currentTheme === theme.id && (
                    <motion.div
                      className="absolute top-2 right-2 w-8 h-8 rounded-full flex items-center justify-center"
                      style={{ background: theme.accentColor }}
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                    >
                      <Check className="w-5 h-5 text-white" />
                    </motion.div>
                  )}
                </div>

                {/* Theme Info */}
                <div 
                  className="p-4"
                  style={{ 
                    background: theme.panelBg,
                    borderTop: `1px solid ${theme.borderColor}`
                  }}
                >
                  <h3 className="font-semibold mb-1" style={{ color: theme.textColor }}>
                    {theme.name}
                  </h3>
                  <p className="text-xs opacity-60" style={{ color: theme.textColor }}>
                    {theme.description}
                  </p>
                  
                  {/* Color Indicators */}
                  <div className="flex gap-1 mt-2">
                    <div 
                      className="w-4 h-4 rounded-full border border-white/20"
                      style={{ background: theme.accentColor }}
                      title="Accent color"
                    />
                    <div 
                      className="w-4 h-4 rounded-full border border-white/20"
                      style={{ background: theme.dotColor }}
                      title="Dot color"
                    />
                  </div>
                </div>
              </div>

              {/* Hover Overlay */}
              <div className="absolute inset-0 rounded-xl bg-white/0 group-hover:bg-white/5 transition-all pointer-events-none" />
            </motion.button>
          ))}
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
}
