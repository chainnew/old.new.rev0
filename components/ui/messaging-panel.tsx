"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, Search, Send, Users, Hash, UserPlus } from "lucide-react";

interface MessagingPanelProps {
  onClose: () => void;
  mode: 'messages' | 'channel';
}

interface Message {
  id: string;
  user: string;
  avatar: string;
  content: string;
  timestamp: string;
  isOnline?: boolean;
}

interface Conversation {
  id: string;
  name: string;
  avatar: string;
  lastMessage: string;
  unread: number;
  isOnline: boolean;
  timestamp: string;
}

// Empty arrays - will be populated from backend/database
const mockConversations: Conversation[] = [];
const mockChannelMessages: Message[] = [];

export function MessagingPanel({ onClose, mode }: MessagingPanelProps) {
  const [activeConversation, setActiveConversation] = useState<string | null>(mode === 'channel' ? 'channel' : null);
  const [messageInput, setMessageInput] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  return (
    <motion.div
      className="fixed inset-0 z-[90] flex items-end justify-center bg-black/60 backdrop-blur-sm"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={onClose}
    >
      <motion.div
        className="w-full max-w-[1200px] h-[600px] bg-black/90 backdrop-blur-xl border-t border-white/10 rounded-t-2xl shadow-2xl overflow-hidden flex mb-0"
        initial={{ y: 600 }}
        animate={{ y: 0 }}
        exit={{ y: 600 }}
        transition={{ type: "spring", stiffness: 300, damping: 30 }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Conversations List */}
        <div className="w-80 border-r border-white/10 flex flex-col">
          {/* Header */}
          <div className="p-4 border-b border-white/10">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-white">
                {mode === 'channel' ? 'Channels' : 'Messages'}
              </h2>
              <button
                onClick={onClose}
                className="p-1 rounded-lg hover:bg-white/10 transition-colors"
              >
                <X className="w-5 h-5 text-white/70" />
              </button>
            </div>

            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/40" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search..."
                className="w-full pl-10 pr-4 py-2 bg-white/5 border border-white/10 rounded-lg text-sm text-white placeholder-white/30 focus:outline-none focus:border-violet-500/50"
              />
            </div>
          </div>

          {/* Public Channel */}
          {mode === 'channel' && (
            <button
              onClick={() => setActiveConversation('channel')}
              className={`flex items-center gap-3 p-4 border-b border-white/10 transition-all ${
                activeConversation === 'channel' ? 'bg-violet-500/10' : 'hover:bg-white/5'
              }`}
            >
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center flex-shrink-0">
                <Hash className="w-5 h-5 text-white" />
              </div>
              <div className="flex-1 text-left overflow-hidden">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-white">old.new</span>
                  <span className="text-xs text-white/50">Now</span>
                </div>
                <p className="text-xs text-white/50 truncate">125 online members</p>
              </div>
            </button>
          )}

          {/* Conversation List */}
          <div className="flex-1 overflow-y-auto">
            {mockConversations.map((conv) => (
              <button
                key={conv.id}
                onClick={() => setActiveConversation(conv.id)}
                className={`w-full flex items-center gap-3 p-4 border-b border-white/10 transition-all ${
                  activeConversation === conv.id ? 'bg-violet-500/10' : 'hover:bg-white/5'
                }`}
              >
                <div className="relative flex-shrink-0">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
                    <span className="text-white text-xs font-semibold">{conv.avatar}</span>
                  </div>
                  {conv.isOnline && (
                    <div className="absolute bottom-0 right-0 w-3 h-3 bg-green-500 border-2 border-black rounded-full" />
                  )}
                </div>
                <div className="flex-1 text-left overflow-hidden">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-white truncate">{conv.name}</span>
                    <span className="text-xs text-white/50">{conv.timestamp}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <p className="text-xs text-white/50 truncate">{conv.lastMessage}</p>
                    {conv.unread > 0 && (
                      <div className="w-5 h-5 bg-violet-500 rounded-full flex items-center justify-center flex-shrink-0 ml-2">
                        <span className="text-[10px] font-bold text-white">{conv.unread}</span>
                      </div>
                    )}
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Chat Area */}
        <div className="flex-1 flex flex-col">
          {activeConversation ? (
            <>
              {/* Chat Header */}
              <div className="p-4 border-b border-white/10 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 rounded-${activeConversation === 'channel' ? 'lg' : 'full'} bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center`}>
                    {activeConversation === 'channel' ? (
                      <Hash className="w-5 h-5 text-white" />
                    ) : (
                      <span className="text-white text-xs font-semibold">SC</span>
                    )}
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-white">
                      {activeConversation === 'channel' ? 'old.new' : 'Sarah Chen'}
                    </h3>
                    <p className="text-xs text-white/50">
                      {activeConversation === 'channel' ? '125 members online' : 'Active now'}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button className="p-2 rounded-lg hover:bg-white/5 transition-colors">
                    <Users className="w-4 h-4 text-white/70" />
                  </button>
                  <button className="p-2 rounded-lg hover:bg-white/5 transition-colors">
                    <UserPlus className="w-4 h-4 text-white/70" />
                  </button>
                </div>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {mockChannelMessages.map((msg) => (
                  <div key={msg.id} className="flex gap-3">
                    <div className="relative flex-shrink-0">
                      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
                        <span className="text-white text-[10px] font-semibold">{msg.avatar}</span>
                      </div>
                      {msg.isOnline && (
                        <div className="absolute bottom-0 right-0 w-2 h-2 bg-green-500 border border-black rounded-full" />
                      )}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-sm font-medium text-white">{msg.user}</span>
                        <span className="text-xs text-white/40">{msg.timestamp}</span>
                      </div>
                      <p className="text-sm text-white/80">{msg.content}</p>
                    </div>
                  </div>
                ))}
              </div>

              {/* Input */}
              <div className="p-4 border-t border-white/10">
                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    value={messageInput}
                    onChange={(e) => setMessageInput(e.target.value)}
                    placeholder={activeConversation === 'channel' ? 'Message #old.new' : 'Send a message...'}
                    className="flex-1 px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-sm text-white placeholder-white/30 focus:outline-none focus:border-violet-500/50"
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && messageInput.trim()) {
                        setMessageInput('');
                      }
                    }}
                  />
                  <button
                    className="p-2 rounded-lg bg-violet-500 hover:bg-violet-600 transition-colors"
                    disabled={!messageInput.trim()}
                  >
                    <Send className="w-5 h-5 text-white" />
                  </button>
                </div>
              </div>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center text-white/40">
              <div className="text-center">
                <Users className="w-16 h-16 mx-auto mb-4 opacity-30" />
                <p className="text-lg font-medium">Select a conversation</p>
                <p className="text-sm mt-2">Choose from your existing conversations or start a new one</p>
              </div>
            </div>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
}
