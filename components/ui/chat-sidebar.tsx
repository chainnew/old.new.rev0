"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { getTheme, loadTheme } from "@/lib/themes";
import { 
  X, 
  Send, 
  Paperclip, 
  Sparkles,
  MessageSquare,
  History,
  Trash2,
  Plus,
  Search,
  Users,
  Circle
} from "lucide-react";
import { MarkdownRenderer } from "./markdown-renderer";

interface ChatSidebarProps {
  onClose: () => void;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

interface Conversation {
  id: string;
  title: string;
  preview: string;
  timestamp: string;
  messages: Message[];
}

export function ChatSidebar({ onClose }: ChatSidebarProps) {
  const [activeTab, setActiveTab] = useState<'chat' | 'friends' | 'history'>('chat');
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversation, setActiveConversation] = useState<string | null>(null);
  const [currentTheme, setCurrentTheme] = useState('midnight');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

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

  const handleSend = async () => {
    if (!input.trim() || isTyping) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: 'Just now'
    };

    setMessages(prev => [...prev, userMessage]);
    const currentInput = input;
    setInput('');
    setIsTyping(true);

    try {
      // Call your Grok API endpoint
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: [...messages, userMessage].map(m => ({
            role: m.role,
            content: m.content
          }))
        })
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data = await response.json();
      
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.message || data.content || 'No response received',
        timestamp: 'Just now'
      };
      
      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: 'Just now'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const loadConversation = (convId: string) => {
    const conv = conversations.find(c => c.id === convId);
    if (conv) {
      setMessages(conv.messages);
      setActiveConversation(convId);
      setActiveTab('chat');
    }
  };

  const newChat = () => {
    setMessages([]);
    setActiveConversation(null);
    setActiveTab('chat');
  };

  const theme = getTheme(currentTheme);

  return (
    <motion.div
      className="fixed left-0 top-[60px] h-[calc(100vh-60px)] w-[420px] z-[60] backdrop-blur-xl border-r flex flex-col"
      style={{
        backgroundColor: theme.panelBg,
        borderColor: theme.borderColor
      }}
      initial={{ x: -420 }}
      animate={{ x: 0 }}
      exit={{ x: -420 }}
      transition={{ type: "spring", stiffness: 300, damping: 30 }}
    >
      {/* Header */}
      <div className="p-4 border-b border-white/10 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-white">AI Chat</h2>
            <p className="text-xs text-white/50">Powered by Grok</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={newChat}
            className="p-2 rounded-lg hover:bg-white/5 transition-colors"
            title="New Chat"
          >
            <Plus className="w-4 h-4 text-white/70" />
          </button>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-white/10 transition-colors"
          >
            <X className="w-5 h-5 text-white/70" />
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="px-4 py-2 border-b border-white/10 flex gap-2">
        <button
          onClick={() => setActiveTab('chat')}
          className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
            activeTab === 'chat'
              ? 'bg-violet-500/20 text-violet-300'
              : 'text-white/60 hover:bg-white/5 hover:text-white'
          }`}
        >
          <Sparkles className="w-4 h-4" />
          AI Chat
        </button>
        <button
          onClick={() => setActiveTab('friends')}
          className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
            activeTab === 'friends'
              ? 'bg-violet-500/20 text-violet-300'
              : 'text-white/60 hover:bg-white/5 hover:text-white'
          }`}
        >
          <Users className="w-4 h-4" />
          Friends
          <span className="px-1.5 py-0.5 text-[10px] bg-green-500/20 text-green-300 rounded-full">3</span>
        </button>
        <button
          onClick={() => setActiveTab('history')}
          className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
            activeTab === 'history'
              ? 'bg-violet-500/20 text-violet-300'
              : 'text-white/60 hover:bg-white/5 hover:text-white'
          }`}
        >
          <History className="w-4 h-4" />
          History
        </button>
      </div>

      {/* Content */}
      {activeTab === 'chat' ? (
        <>
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.length === 0 ? (
              <div className="h-full flex items-center justify-center text-center">
                <div>
                  <Sparkles className="w-12 h-12 mx-auto mb-4 text-violet-400 opacity-50" />
                  <p className="text-white/40 text-sm">Start a conversation with Grok</p>
                  <p className="text-white/20 text-xs mt-2">Ask anything, code, debug, or chat</p>
                </div>
              </div>
            ) : (
              <>
                {messages.map((msg) => (
                  <div
                    key={msg.id}
                    className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[85%] rounded-2xl px-4 py-3 ${
                        msg.role === 'user'
                          ? 'bg-gradient-to-br from-violet-500 to-purple-600 text-white'
                          : 'bg-white/5 text-white/90'
                      }`}
                    >
                      {msg.role === 'assistant' ? (
                        <MarkdownRenderer content={msg.content} />
                      ) : (
                        <p className="text-sm">{msg.content}</p>
                      )}
                    </div>
                  </div>
                ))}
                {isTyping && (
                  <div className="flex justify-start">
                    <div className="bg-white/5 rounded-2xl px-4 py-3">
                      <div className="flex gap-1">
                        <motion.div
                          className="w-2 h-2 bg-violet-400 rounded-full"
                          animate={{ opacity: [0.3, 1, 0.3] }}
                          transition={{ duration: 1, repeat: Infinity, delay: 0 }}
                        />
                        <motion.div
                          className="w-2 h-2 bg-violet-400 rounded-full"
                          animate={{ opacity: [0.3, 1, 0.3] }}
                          transition={{ duration: 1, repeat: Infinity, delay: 0.2 }}
                        />
                        <motion.div
                          className="w-2 h-2 bg-violet-400 rounded-full"
                          animate={{ opacity: [0.3, 1, 0.3] }}
                          transition={{ duration: 1, repeat: Infinity, delay: 0.4 }}
                        />
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </>
            )}
          </div>

          {/* Input */}
          <div className="p-4 border-t border-white/10">
            <div className="flex items-end gap-2">
              <div className="flex-1 bg-white/5 rounded-lg border border-white/10 focus-within:border-violet-500/50 transition-colors">
                <textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handleSend();
                    }
                  }}
                  placeholder="Ask Grok anything..."
                  rows={3}
                  className="w-full px-4 py-3 bg-transparent text-sm text-white placeholder-white/30 focus:outline-none resize-none"
                />
              </div>
              <button
                onClick={handleSend}
                disabled={!input.trim() || isTyping}
                className="p-3 rounded-lg bg-gradient-to-br from-violet-500 to-purple-600 hover:from-violet-600 hover:to-purple-700 text-white transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Send className="w-5 h-5" />
              </button>
            </div>
          </div>
        </>
      ) : (
        // History Tab
        <div className="flex-1 overflow-y-auto p-4">
          <div className="mb-4 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/40" />
            <input
              type="text"
              placeholder="Search conversations..."
              className="w-full pl-10 pr-4 py-2 bg-white/5 border border-white/10 rounded-lg text-sm text-white placeholder-white/30 focus:outline-none focus:border-violet-500/50"
            />
          </div>

          <div className="space-y-2">
            {conversations.map((conv) => (
              <motion.button
                key={conv.id}
                onClick={() => loadConversation(conv.id)}
                className={`w-full text-left p-3 rounded-lg transition-all ${
                  activeConversation === conv.id
                    ? 'bg-violet-500/20 border border-violet-500/30'
                    : 'bg-white/5 hover:bg-white/10 border border-white/10'
                }`}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <div className="flex items-start justify-between mb-1">
                  <h3 className="text-sm font-medium text-white truncate">{conv.title}</h3>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setConversations(conversations.filter(c => c.id !== conv.id));
                    }}
                    className="p-1 rounded hover:bg-red-500/20 transition-colors"
                  >
                    <Trash2 className="w-3 h-3 text-white/40 hover:text-red-400" />
                  </button>
                </div>
                <p className="text-xs text-white/50 truncate mb-1">{conv.preview}</p>
                <span className="text-xs text-white/30">{conv.timestamp}</span>
              </motion.button>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  );
}
