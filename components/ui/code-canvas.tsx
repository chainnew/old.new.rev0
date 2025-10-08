"use client";

import { useState, useEffect } from "react";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";
import { Copy, Check, ChevronDown, ChevronUp } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";

interface CodeCanvasProps {
  code: string;
  language: string;
  filename?: string;
}

export function CodeCanvas({ code, language, filename }: CodeCanvasProps) {
  const [copied, setCopied] = useState(false);
  const [isClient, setIsClient] = useState(false);
  const [isCollapsed, setIsCollapsed] = useState(true);

  useEffect(() => {
    setIsClient(true);
  }, []);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const lineCount = code.split('\n').length;
  const shouldCollapse = lineCount > 10;
  const previewLines = code.split('\n').slice(0, 5).join('\n');

  // DEBUG: Log state changes
  useEffect(() => {
    console.log('[CodeCanvas] State:', {
      language,
      lineCount,
      shouldCollapse,
      isCollapsed,
      isClient
    });
  }, [isCollapsed, language, lineCount, shouldCollapse, isClient]);

  if (!isClient) {
    return (
      <div className="relative group my-4 rounded-xl overflow-hidden border border-white/10 bg-[#0d1117] shadow-2xl min-h-[100px]">
        <div className="flex items-center justify-between px-4 py-2 bg-[#161b22] border-b border-white/5">
          <div className="flex items-center gap-2">
            <div className="flex gap-1.5">
              <div className="w-3 h-3 rounded-full bg-red-500/80" />
              <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
              <div className="w-3 h-3 rounded-full bg-green-500/80" />
            </div>
            {filename && (
              <span className="text-xs text-white/60 ml-2 font-mono">
                {filename}
              </span>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 1 }}
      animate={{ opacity: 1 }}
      className="relative group my-4 rounded-lg overflow-hidden bg-[#0a0a0a]/40 backdrop-blur-sm shadow-xl"
      style={{ 
        willChange: isCollapsed ? 'max-height' : 'auto',
        transform: 'translateZ(0)' // Force GPU acceleration
      }}
    >
      {/* DEBUG indicator */}
      <div className="absolute top-0 right-0 bg-red-500/50 text-white text-[8px] px-1 py-0.5 z-50">
        {isCollapsed ? 'COLLAPSED' : 'EXPANDED'}
      </div>

      {/* Header Bar */}
      <div className="flex items-center justify-between px-4 py-2 bg-white/[0.02]">
        <div className="flex items-center gap-2">
          <div className="flex gap-1.5">
            <div className="w-3 h-3 rounded-full bg-red-500/80" />
            <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
            <div className="w-3 h-3 rounded-full bg-green-500/80" />
          </div>
          {filename && (
            <span className="text-xs text-white/60 ml-2 font-mono">
              {filename}
            </span>
          )}
          {!filename && language && (
            <span className="text-xs text-white/40 ml-2 font-mono">
              {language}
            </span>
          )}
          {shouldCollapse && (
            <span className="text-[10px] text-white/30 ml-2">
              {lineCount} lines
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          {shouldCollapse && (
            <motion.button
              onClick={() => {
                console.log('[CodeCanvas] Toggle button clicked:', {
                  current: isCollapsed,
                  willBe: !isCollapsed,
                  timestamp: Date.now()
                });
                setIsCollapsed(!isCollapsed);
              }}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="flex items-center gap-1 px-2.5 py-1.5 rounded-md text-xs font-medium bg-white/5 text-white/50 hover:bg-white/10 hover:text-white/80 transition-all"
            >
              {isCollapsed ? (
                <>
                  <ChevronDown className="w-3.5 h-3.5" />
                  <span>Expand</span>
                </>
              ) : (
                <>
                  <ChevronUp className="w-3.5 h-3.5" />
                  <span>Collapse</span>
                </>
              )}
            </motion.button>
          )}

          <motion.button
            onClick={handleCopy}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className={cn(
              "flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-xs font-medium transition-all",
              copied
                ? "bg-green-500/20 text-green-300"
                : "bg-white/5 text-white/50 hover:bg-white/10 hover:text-white/80"
            )}
          >
            <AnimatePresence mode="wait">
              {copied ? (
                <motion.div
                  key="check"
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  exit={{ scale: 0 }}
                  className="flex items-center gap-1.5"
                >
                  <Check className="w-3.5 h-3.5" />
                  <span>Copied!</span>
                </motion.div>
              ) : (
                <motion.div
                  key="copy"
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  exit={{ scale: 0 }}
                  className="flex items-center gap-1.5"
                >
                  <Copy className="w-3.5 h-3.5" />
                  <span>Copy</span>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.button>
        </div>
      </div>

      {/* Code Content */}
      <div 
        className={cn(
          "relative overflow-hidden transition-all duration-300 ease-in-out",
          shouldCollapse && isCollapsed ? "max-h-[120px]" : "max-h-none"
        )}
        onTransitionStart={() => console.log('[CodeCanvas] Transition START')}
        onTransitionEnd={() => console.log('[CodeCanvas] Transition END')}
      >
        {/* DEBUG: Height indicator */}
        <div className="absolute top-2 left-2 bg-blue-500/50 text-white text-[8px] px-1 py-0.5 z-50">
          Lines: {isCollapsed ? '5 preview' : lineCount}
        </div>

        <div className="overflow-x-auto">
          <SyntaxHighlighter
            language={language}
            style={oneDark}
            customStyle={{
              margin: 0,
              padding: "1.25rem",
              background: "rgba(0, 0, 0, 0.2)",
              fontSize: "0.875rem",
              lineHeight: "1.6",
              borderRadius: "0 0 0.5rem 0.5rem",
            }}
            showLineNumbers={!isCollapsed && code.split("\n").length > 3}
            wrapLines={true}
            lineNumberStyle={{
              minWidth: "3em",
              paddingRight: "1em",
              color: "rgba(255, 255, 255, 0.2)",
              userSelect: "none",
            }}
          >
            {shouldCollapse && isCollapsed ? previewLines : code}
          </SyntaxHighlighter>
        </div>
        
        {shouldCollapse && isCollapsed && (
          <div className="absolute bottom-0 left-0 right-0 h-12 bg-gradient-to-t from-black/80 to-transparent flex items-end justify-center pb-2 pointer-events-none">
            <button
              onClick={() => setIsCollapsed(false)}
              className="text-xs text-white/40 hover:text-white/60 transition-colors pointer-events-auto"
            >
              ···
            </button>
          </div>
        )}
      </div>
    </motion.div>
  );
}

interface InlineCodeProps {
  children: string;
}

export function InlineCode({ children }: InlineCodeProps) {
  return (
    <code className="px-1.5 py-0.5 rounded-md bg-white/5 text-violet-300 font-mono text-sm">
      {children}
    </code>
  );
}
