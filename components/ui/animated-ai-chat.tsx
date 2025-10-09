"use client";

import { useEffect, useRef, useCallback, useTransition } from "react";
import { useState } from "react";
import { cn } from "@/lib/utils";
import {
    ImageIcon,
    FileUp,
    Figma,
    MonitorIcon,
    CircleUserRound,
    ArrowUpIcon,
    Paperclip,
    PlusIcon,
    SendIcon,
    XIcon,
    LoaderIcon,
    Sparkles,
    Command,
    Copy,
    Check,
    Bug,
    Code2,
    Terminal,
    Maximize2,
    Lock,
    Unlock,
    GripHorizontal,
    GripVertical,
    LayoutList,
    ChevronLeft,
    ChevronRight,
    Smartphone,
    Palette,
    Hash,
    FilePlus,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import * as React from "react"
import { MarkdownRenderer } from "./markdown-renderer";
import { BackgroundPlus } from "./background-plus";
import Plan from "./agent-plan";
import { CodeWindow } from "./code-window";
import { BottomPanel } from "./bottom-panel";
import { IPhoneSimulator } from "./iphone-simulator";
import { AndroidSimulator } from "./android-simulator";
import { themes, saveTheme, loadTheme, getTheme } from "@/lib/themes";
import { ThemePicker } from "./theme-picker";
import { UserSidebar } from "./user-sidebar";
import { AccountSettings } from "./account-settings";
import { MessagingPanel } from "./messaging-panel";
import { AuthModal } from "./auth-modal";
import { GitHubPanel } from "./github-panel";
import { ChatSidebar } from "./chat-sidebar";
import { AdminPanel } from "../admin/admin-panel";
import { CodeActionPanel } from "./code-action-panel";

interface UseAutoResizeTextareaProps {
    minHeight: number;
    maxHeight?: number;
}

function useAutoResizeTextarea({
    minHeight,
    maxHeight,
}: UseAutoResizeTextareaProps) {
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    const adjustHeight = useCallback(
        (reset?: boolean) => {
            const textarea = textareaRef.current;
            if (!textarea) return;

            if (reset) {
                textarea.style.height = `${minHeight}px`;
                return;
            }

            textarea.style.height = `${minHeight}px`;
            const newHeight = Math.max(
                minHeight,
                Math.min(
                    textarea.scrollHeight,
                    maxHeight ?? Number.POSITIVE_INFINITY
                )
            );

            textarea.style.height = `${newHeight}px`;
        },
        [minHeight, maxHeight]
    );

    useEffect(() => {
        const textarea = textareaRef.current;
        if (textarea) {
            textarea.style.height = `${minHeight}px`;
        }
    }, [minHeight]);

    useEffect(() => {
        const handleResize = () => adjustHeight();
        window.addEventListener("resize", handleResize);
        return () => window.removeEventListener("resize", handleResize);
    }, [adjustHeight]);

    return { textareaRef, adjustHeight };
}

interface CommandSuggestion {
    icon: React.ReactNode;
    label: string;
    description: string;
    prefix: string;
}

interface TextareaProps
  extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  containerClassName?: string;
  showRing?: boolean;
}

const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, containerClassName, showRing = true, ...props }, ref) => {
    const [isFocused, setIsFocused] = React.useState(false);
    
    return (
      <div className={cn(
        "relative",
        containerClassName
      )}>
        <textarea
          className={cn(
            "flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm",
            "transition-all duration-200 ease-in-out",
            "placeholder:text-muted-foreground",
            "disabled:cursor-not-allowed disabled:opacity-50",
            showRing ? "focus-visible:outline-none focus-visible:ring-0 focus-visible:ring-offset-0" : "",
            className
          )}
          ref={ref}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          {...props}
        />
        
        {showRing && isFocused && (
          <motion.span 
            className="absolute inset-0 rounded-md pointer-events-none ring-2 ring-offset-0 ring-violet-500/30"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
          />
        )}

        {props.onChange && (
          <div 
            className="absolute bottom-2 right-2 opacity-0 w-2 h-2 bg-violet-500 rounded-full"
            style={{
              animation: 'none',
            }}
            id="textarea-ripple"
          />
        )}
      </div>
    )
  }
)
Textarea.displayName = "Textarea"

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export function AnimatedAIChat() {
    const [value, setValue] = useState("");
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [attachments, setAttachments] = useState<string[]>([]);
    const [isTyping, setIsTyping] = useState(false);
    const [isPending, startTransition] = useTransition();
    const [activeSuggestion, setActiveSuggestion] = useState<number>(-1);
    const [showCommandPalette, setShowCommandPalette] = useState(false);
    const [recentCommand, setRecentCommand] = useState<string | null>(null);
    const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
    const { textareaRef, adjustHeight } = useAutoResizeTextarea({
        minHeight: 100,
        maxHeight: 300,
    });
    const [inputFocused, setInputFocused] = useState(false);
    const commandPaletteRef = useRef<HTMLDivElement>(null);
    const [conversationId, setConversationId] = useState(() => `conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
    const [isMounted, setIsMounted] = useState(false);
    const [plannerNotification, setPlannerNotification] = useState(false);
    const [showCode, setShowCode] = useState(false);
    const [showBottomPanel, setShowBottomPanel] = useState(false);
    const [showPlanningPanel, setShowPlanningPanel] = useState(false);
    const [codeHeight, setCodeHeight] = useState(55); // percentage of vh
    const [isResizeLocked, setIsResizeLocked] = useState(false);
    const [isDragging, setIsDragging] = useState(false);
    const [rightPanelWidth, setRightPanelWidth] = useState(1200); // pixels
    const [isRightPanelLocked, setIsRightPanelLocked] = useState(false);
    const [isResizingRightPanel, setIsResizingRightPanel] = useState(false);
    const [isChatCollapsed, setIsChatCollapsed] = useState(false);
    const [showIPhone, setShowIPhone] = useState(false);
    const [showAndroid, setShowAndroid] = useState(false);
    const [currentTheme, setCurrentTheme] = useState('midnight');
    const [showThemeSelector, setShowThemeSelector] = useState(false);
    const [showAccountSettings, setShowAccountSettings] = useState(false);
    const [showMessaging, setShowMessaging] = useState(false);
    const [showChannel, setShowChannel] = useState(false);
    const [showAuth, setShowAuth] = useState(false);
    const [showGitHub, setShowGitHub] = useState(false);
    const [showChatSidebar, setShowChatSidebar] = useState(false);
    const [showAdminPanel, setShowAdminPanel] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Mount effect - runs once
    useEffect(() => {
        setIsMounted(true);
        const savedTheme = loadTheme();
        setCurrentTheme(savedTheme);
    }, []);

    // Load conversation history when conversationId changes
    useEffect(() => {
        if (!conversationId) return;
        
        const loadConversation = async () => {
            try {
                const response = await fetch(`/api/conversations/${conversationId}`);
                if (response.ok) {
                    const data = await response.json();
                    setMessages(data.messages || []);
                }
            } catch (error) {
                console.error("Failed to load conversation history:", error);
            }
        };
        loadConversation();
    }, [conversationId]);

    // Auto-scroll to latest message
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    const handleThemeChange = (themeId: string) => {
        setCurrentTheme(themeId);
        saveTheme(themeId);
        setShowThemeSelector(false);
    };

    const toggleAll = () => {
        const newState = !(showCode && showBottomPanel && showIPhone && showAndroid);
        setShowCode(newState);
        setShowBottomPanel(newState);
        setShowIPhone(newState);
        setShowAndroid(newState);
    };

    const handleMouseDown = () => {
        if (!isResizeLocked) {
            setIsDragging(true);
        }
    };

    const handleRightPanelMouseDown = () => {
        if (!isRightPanelLocked) {
            setIsResizingRightPanel(true);
        }
    };

    useEffect(() => {
        const handleMouseMove = (e: MouseEvent) => {
            if (isDragging && !isResizeLocked) {
                const windowHeight = window.innerHeight;
                const newHeight = ((windowHeight - e.clientY) / windowHeight) * 100;
                // Constrain between 20vh and 80vh
                const constrainedHeight = Math.max(20, Math.min(80, 100 - newHeight));
                setCodeHeight(constrainedHeight);
            }
        };

        const handleMouseUp = () => {
            setIsDragging(false);
        };

        if (isDragging) {
            document.addEventListener('mousemove', handleMouseMove);
            document.addEventListener('mouseup', handleMouseUp);
        }

        return () => {
            document.removeEventListener('mousemove', handleMouseMove);
            document.removeEventListener('mouseup', handleMouseUp);
        };
    }, [isDragging, isResizeLocked]);

    // Right panel width resize
    useEffect(() => {
        const handleMouseMove = (e: MouseEvent) => {
            if (isResizingRightPanel && !isRightPanelLocked) {
                e.preventDefault();
                const windowWidth = window.innerWidth;
                const newWidth = windowWidth - e.clientX;
                // Constrain between 800px and 1600px
                const constrainedWidth = Math.max(800, Math.min(1600, newWidth));
                setRightPanelWidth(constrainedWidth);
            }
        };

        const handleMouseUp = () => {
            setIsResizingRightPanel(false);
            document.body.style.cursor = '';
            document.body.style.userSelect = '';
        };

        if (isResizingRightPanel) {
            document.body.style.cursor = 'ew-resize';
            document.body.style.userSelect = 'none';
            document.addEventListener('mousemove', handleMouseMove);
            document.addEventListener('mouseup', handleMouseUp);
        }

        return () => {
            document.removeEventListener('mousemove', handleMouseMove);
            document.removeEventListener('mouseup', handleMouseUp);
            document.body.style.cursor = '';
            document.body.style.userSelect = '';
        };
    }, [isResizingRightPanel, isRightPanelLocked]);

    const commandSuggestions: CommandSuggestion[] = [
        { 
            icon: <ImageIcon className="w-4 h-4" />, 
            label: "Clone UI", 
            description: "Generate a UI from a screenshot", 
            prefix: "/clone" 
        },
        { 
            icon: <Figma className="w-4 h-4" />, 
            label: "Import Figma", 
            description: "Import a design from Figma", 
            prefix: "/figma" 
        },
        { 
            icon: <MonitorIcon className="w-4 h-4" />, 
            label: "Create Page", 
            description: "Generate a new web page", 
            prefix: "/page" 
        },
        { 
            icon: <Sparkles className="w-4 h-4" />, 
            label: "Improve", 
            description: "Improve existing UI design", 
            prefix: "/improve" 
        },
    ];

    useEffect(() => {
        if (value.startsWith('/') && !value.includes(' ')) {
            setShowCommandPalette(true);
            
            const matchingSuggestionIndex = commandSuggestions.findIndex(
                (cmd) => cmd.prefix.startsWith(value)
            );
            
            if (matchingSuggestionIndex >= 0) {
                setActiveSuggestion(matchingSuggestionIndex);
            } else {
                setActiveSuggestion(-1);
            }
        } else {
            setShowCommandPalette(false);
        }
    }, [value]);

    useEffect(() => {
        const handleMouseMove = (e: MouseEvent) => {
            setMousePosition({ x: e.clientX, y: e.clientY });
        };

        window.addEventListener('mousemove', handleMouseMove);
        return () => {
            window.removeEventListener('mousemove', handleMouseMove);
        };
    }, []);

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            const target = event.target as Node;
            const commandButton = document.querySelector('[data-command-button]');
            
            if (commandPaletteRef.current && 
                !commandPaletteRef.current.contains(target) && 
                !commandButton?.contains(target)) {
                setShowCommandPalette(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, []);

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (showCommandPalette) {
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                setActiveSuggestion(prev => 
                    prev < commandSuggestions.length - 1 ? prev + 1 : 0
                );
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                setActiveSuggestion(prev => 
                    prev > 0 ? prev - 1 : commandSuggestions.length - 1
                );
            } else if (e.key === 'Tab' || e.key === 'Enter') {
                e.preventDefault();
                if (activeSuggestion >= 0) {
                    const selectedCommand = commandSuggestions[activeSuggestion];
                    setValue(selectedCommand.prefix + ' ');
                    setShowCommandPalette(false);
                    
                    setRecentCommand(selectedCommand.label);
                    setTimeout(() => setRecentCommand(null), 3500);
                }
            } else if (e.key === 'Escape') {
                e.preventDefault();
                setShowCommandPalette(false);
            }
        } else if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            if (value.trim()) {
                handleSendMessage();
            }
        }
    };

    const handleSendMessage = async () => {
        if (!value.trim() || isTyping) return;

        const userMessage = value.trim();
        setValue("");
        adjustHeight(true);

        // Check if this is a big/complex task - trigger notification instead of auto-opening
        const complexityKeywords = [
            'build', 'create app', 'implement', 'develop', 'architecture',
            'system', 'project', 'multiple', 'integrate', 'full stack',
            'backend', 'frontend', 'database', 'api', '/plan', 'scope'
        ];
        
        const isComplexTask = complexityKeywords.some(keyword => 
            userMessage.toLowerCase().includes(keyword)
        ) || userMessage.length > 200; // Long messages = complex tasks
        
        if (isComplexTask) {
            setPlannerNotification(true);
            // Auto-clear notification after 10 seconds
            setTimeout(() => setPlannerNotification(false), 10000);
        }

        // Add user message
        const newMessages = [...messages, { role: "user" as const, content: userMessage }];
        setMessages(newMessages);
        setIsTyping(true);

        try {
            const response = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ 
                    message: userMessage,
                    conversationId: conversationId,
                    history: messages // Pass full conversation history for 1M context
                }),
            });

            if (!response.ok) {
                throw new Error("Failed to get response");
            }

            const data = await response.json();
            setMessages((prev) => [
                ...prev,
                { role: "assistant", content: data.response },
            ]);
        } catch (error) {
            console.error("Error:", error);
            setMessages((prev) => [
                ...prev,
                {
                    role: "assistant",
                    content: "Sorry, I encountered an error. Please try again.",
                },
            ]);
        } finally {
            setIsTyping(false);
        }
    };

    const handleAttachFile = () => {
        const mockFileName = `file-${Math.floor(Math.random() * 1000)}.pdf`;
        setAttachments(prev => [...prev, mockFileName]);
    };

    const removeAttachment = (index: number) => {
        setAttachments(prev => prev.filter((_, i) => i !== index));
    };
    
    const selectCommandSuggestion = (index: number) => {
        const selectedCommand = commandSuggestions[index];
        setValue(selectedCommand.prefix + ' ');
        setShowCommandPalette(false);
        
        setRecentCommand(selectedCommand.label);
        setTimeout(() => setRecentCommand(null), 2000);
    };

    return (
        <div className="h-screen flex w-full text-white relative overflow-hidden">
            <BackgroundPlus themeId={currentTheme} />

            {/* User Sidebar - Always visible */}
            <UserSidebar
                onOpenSettings={() => setShowAccountSettings(true)}
                onOpenMessages={() => setShowMessaging(true)}
                onOpenChannel={() => setShowChannel(true)}
                onOpenGitHub={() => setShowGitHub(true)}
                onOpenAuth={() => setShowAuth(true)}
                onOpenAIChat={() => setShowChatSidebar(true)}
                onOpenAdmin={() => setShowAdminPanel(true)}
            />

            {/* Chat Sidebar - Slides in next to user sidebar */}
            <AnimatePresence>
                {showChatSidebar && (
                    <ChatSidebar onClose={() => setShowChatSidebar(false)} />
                )}
            </AnimatePresence>
            {/* Collapsed Chat Tab - Shows when chat is hidden */}
            <AnimatePresence>
                {isChatCollapsed && (
                    <motion.div
                        initial={{ opacity: 0, x: -100 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -100 }}
                        className="fixed left-0 bottom-4 z-[55]"
                    >
                        <button
                            onClick={() => setIsChatCollapsed(false)}
                            className="bg-black/80 backdrop-blur-sm border border-white/10 rounded-r-lg p-3 hover:bg-white/5 transition-all shadow-lg"
                            title="Show chat"
                        >
                            <ChevronRight className="w-5 h-5 text-white/70" />
                        </button>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Top Toolbar - Fixed above chat */}
            <motion.div
                className="fixed top-4 z-50"
                style={{ left: 'calc(3% + 1rem)' }}
                animate={{
                    x: isChatCollapsed ? -800 : 0,
                    opacity: isChatCollapsed ? 0 : 1
                }}
                transition={{
                    type: "spring",
                    stiffness: 300,
                    damping: 30
                }}
            >
                <div className="flex items-center gap-2">
                    <motion.button
                        onClick={() => {
                            setMessages([]);
                            setConversationId(`conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
                        }}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        className="flex items-center gap-2 px-4 py-2 rounded-lg bg-violet-600/90 hover:bg-violet-500 backdrop-blur-sm border border-violet-400/30 text-white text-sm font-medium transition-colors shadow-lg"
                        title="Start a new chat session"
                    >
                        <FilePlus className="w-4 h-4" />
                        New Session
                    </motion.button>
                </div>
            </motion.div>

            {/* Left: Chat Area - Full height, scrollable past top bar */}
            <motion.div 
                className="fixed top-0 bottom-4 z-10 w-[900px] flex flex-col rounded-2xl overflow-hidden shadow-2xl"
                style={{ left: '3%' }}
                animate={{
                    x: isChatCollapsed ? -800 : 0,
                    opacity: isChatCollapsed ? 0 : 1
                }}
                transition={{
                    type: "spring",
                    stiffness: 300,
                    damping: 30
                }}
            >

                {/* Chat Messages Area - Scrollable with sleek scrollbar */}
                <div 
                    className="flex-1 w-full overflow-y-auto overflow-x-hidden pb-2 pt-24 min-h-0 custom-scrollbar"
                    style={{
                        scrollbarWidth: 'thin',
                        scrollbarColor: 'rgba(139, 92, 246, 0.3) transparent'
                    }}
                >
                    <div className="space-y-4 flex flex-col w-full px-4 min-h-full justify-end">
                        {messages.length === 0 ? (
                            <div className="flex-1" />
                        ) : (
                            <div className="space-y-4">
                                {messages.map((msg, idx) => (
                                    <MessageBubble 
                                        key={`msg-${idx}-${msg.role}-${msg.content.substring(0, 50)}`} 
                                        message={msg} 
                                    />
                                ))}
                                <div ref={messagesEndRef} />
                            </div>
                        )}
                    </div>
                </div>

                {/* Input Area - Fixed at bottom */}
                <div className="w-full relative z-20 space-y-4 px-4 pb-6 flex-shrink-0">
                <motion.div 
                    className="relative backdrop-blur-2xl bg-white/[0.02] rounded-2xl border border-white/[0.05] shadow-2xl"
                    initial={{ scale: 0.98 }}
                    animate={{ scale: 1 }}
                    transition={{ delay: 0.1 }}
                >
                    <AnimatePresence>
                        {showCommandPalette && (
                            <motion.div 
                                ref={commandPaletteRef}
                                className="absolute left-4 right-4 bottom-full mb-2 backdrop-blur-xl bg-black/90 rounded-lg z-50 shadow-lg border border-white/10 overflow-hidden"
                                initial={{ opacity: 0, y: 5 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: 5 }}
                                transition={{ duration: 0.15 }}
                            >
                                <div className="py-1 bg-black/95">
                                    {commandSuggestions.map((suggestion, index) => (
                                        <motion.div
                                            key={suggestion.prefix}
                                            className={cn(
                                                "flex items-center gap-2 px-3 py-2 text-xs transition-colors cursor-pointer",
                                                activeSuggestion === index 
                                                    ? "bg-white/10 text-white" 
                                                    : "text-white/70 hover:bg-white/5"
                                            )}
                                            onClick={() => selectCommandSuggestion(index)}
                                            initial={{ opacity: 0 }}
                                            animate={{ opacity: 1 }}
                                            transition={{ delay: index * 0.03 }}
                                        >
                                            <div className="w-5 h-5 flex items-center justify-center text-white/60">
                                                {suggestion.icon}
                                            </div>
                                            <div className="font-medium">{suggestion.label}</div>
                                            <div className="text-white/40 text-xs ml-1">
                                                {suggestion.prefix}
                                            </div>
                                        </motion.div>
                                    ))}
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>

                    <div className="p-4">
                        <Textarea
                            ref={textareaRef}
                            value={value}
                            onChange={(e) => {
                                setValue(e.target.value);
                                adjustHeight();
                            }}
                            onKeyDown={handleKeyDown}
                            onFocus={() => setInputFocused(true)}
                            onBlur={() => setInputFocused(false)}
                            placeholder="Ask a question..."
                            disabled={isTyping}
                            containerClassName="w-full"
                            className={cn(
                                "w-full px-4 py-3",
                                "resize-none",
                                "bg-transparent",
                                "border-none",
                                "text-white/90 text-sm",
                                "focus:outline-none",
                                "placeholder:text-white/20",
                                "min-h-[100px]"
                            )}
                            style={{
                                overflow: "hidden",
                            }}
                            showRing={false}
                        />
                    </div>

                    <AnimatePresence>
                        {attachments.length > 0 && (
                            <motion.div 
                                className="px-4 pb-3 flex gap-2 flex-wrap"
                                initial={{ opacity: 0, height: 0 }}
                                animate={{ opacity: 1, height: "auto" }}
                                exit={{ opacity: 0, height: 0 }}
                            >
                                {attachments.map((file, index) => (
                                    <motion.div
                                        key={index}
                                        className="flex items-center gap-2 text-xs bg-white/[0.03] py-1.5 px-3 rounded-lg text-white/70"
                                        initial={{ opacity: 0, scale: 0.9 }}
                                        animate={{ opacity: 1, scale: 1 }}
                                        exit={{ opacity: 0, scale: 0.9 }}
                                    >
                                        <span>{file}</span>
                                        <button 
                                            onClick={() => removeAttachment(index)}
                                            className="text-white/40 hover:text-white transition-colors"
                                        >
                                            <XIcon className="w-3 h-3" />
                                        </button>
                                    </motion.div>
                                ))}
                            </motion.div>
                        )}
                    </AnimatePresence>

                    <div className="p-3 border-t border-white/[0.05] flex items-center justify-between gap-2 flex-shrink-0">
                        <div className="flex items-center gap-2">
                            <motion.button
                                type="button"
                                onClick={handleAttachFile}
                                whileTap={{ scale: 0.94 }}
                                className="p-2 text-white/40 hover:text-white/90 rounded-lg transition-colors"
                            >
                                <Paperclip className="w-4 h-4" />
                            </motion.button>
                            
                            <motion.button
                                type="button"
                                data-command-button
                                onClick={(e) => {
                                    e.stopPropagation();
                                    setShowCommandPalette(prev => !prev);
                                }}
                                whileTap={{ scale: 0.94 }}
                                className={cn(
                                    "p-2 text-white/40 hover:text-white/90 rounded-lg transition-colors",
                                    showCommandPalette && "bg-white/10 text-white/90"
                                )}
                            >
                                <Command className="w-4 h-4" />
                            </motion.button>
                        </div>

                        <div className="flex items-center gap-1.5 flex-wrap">
                            {/* AI Thinking Indicator */}
                            {isTyping && (
                                <motion.div
                                    initial={{ opacity: 0, scale: 0.8 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    exit={{ opacity: 0, scale: 0.8 }}
                                    className="flex items-center gap-2 px-3 py-2 rounded-lg bg-violet-500/10 border border-violet-500/20"
                                >
                                    <Sparkles className="w-3.5 h-3.5 text-violet-400 animate-pulse" />
                                    <span className="text-xs text-violet-300">AI Thinking...</span>
                                </motion.div>
                            )}

                            <motion.button
                                type="button"
                                onClick={() => setIsChatCollapsed(true)}
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                className="p-2 rounded-lg text-sm font-medium transition-all bg-white/[0.05] text-white/40 hover:bg-white/10 hover:text-white/60"
                                title="Hide Chat"
                            >
                                <ChevronLeft className="w-4 h-4" />
                            </motion.button>

                            <motion.button
                                type="button"
                                onClick={() => setShowThemeSelector(true)}
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                className="p-2 rounded-lg text-sm font-medium transition-all bg-white/[0.05] text-white/40 hover:bg-white/10 hover:text-white/60"
                                title="Change Theme"
                            >
                                <Palette className="w-4 h-4" />
                            </motion.button>

                            <motion.button
                                type="button"
                                onClick={() => {
                                    setShowPlanningPanel(!showPlanningPanel);
                                    setPlannerNotification(false);
                                }}
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                className={cn(
                                    "p-2 rounded-lg text-sm font-medium transition-all relative",
                                    showPlanningPanel
                                        ? "bg-violet-500/20 text-violet-300"
                                        : "bg-white/[0.05] text-white/40 hover:bg-white/10 hover:text-white/60"
                                )}
                                title="Toggle AI Planner"
                            >
                                <LayoutList className="w-4 h-4" />
                                {/* Notification pulse when scope detected */}
                                <AnimatePresence>
                                    {plannerNotification && !showPlanningPanel && (
                                        <motion.div
                                            initial={{ scale: 0 }}
                                            animate={{ scale: 1 }}
                                            exit={{ scale: 0 }}
                                            className="absolute -top-1 -right-1 w-3 h-3 bg-violet-500 rounded-full"
                                        >
                                            <div className="absolute inset-0 rounded-full bg-violet-500 animate-ping opacity-75" />
                                        </motion.div>
                                    )}
                                </AnimatePresence>
                            </motion.button>

                            <motion.button
                                type="button"
                                onClick={() => setShowCode(!showCode)}
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                className={cn(
                                    "p-2 rounded-lg text-sm font-medium transition-all",
                                    showCode
                                        ? "bg-violet-500/20 text-violet-300"
                                        : "bg-white/[0.05] text-white/40 hover:bg-white/10 hover:text-white/60"
                                )}
                                title="Toggle Code Viewer"
                            >
                                <Code2 className="w-4 h-4" />
                            </motion.button>

                            <motion.button
                                type="button"
                                onClick={() => setShowBottomPanel(!showBottomPanel)}
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                className={cn(
                                    "p-2 rounded-lg text-sm font-medium transition-all",
                                    showBottomPanel
                                        ? "bg-violet-500/20 text-violet-300"
                                        : "bg-white/[0.05] text-white/40 hover:bg-white/10 hover:text-white/60"
                                )}
                                title="Toggle Terminal/Debug"
                            >
                                <Terminal className="w-4 h-4" />
                            </motion.button>

                            <motion.button
                                type="button"
                                onClick={() => setShowIPhone(!showIPhone)}
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                className={cn(
                                    "p-2 rounded-lg text-sm font-medium transition-all",
                                    showIPhone
                                        ? "bg-blue-500/20 text-blue-300"
                                        : "bg-white/[0.05] text-white/40 hover:bg-white/10 hover:text-white/60"
                                )}
                                title="Toggle iPhone Simulator"
                            >
                                <Smartphone className="w-4 h-4" />
                            </motion.button>

                            <motion.button
                                type="button"
                                onClick={() => setShowAndroid(!showAndroid)}
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                className={cn(
                                    "p-2 rounded-lg text-sm font-medium transition-all",
                                    showAndroid
                                        ? "bg-green-500/20 text-green-300"
                                        : "bg-white/[0.05] text-white/40 hover:bg-white/10 hover:text-white/60"
                                )}
                                title="Toggle Android Simulator"
                            >
                                <Smartphone className="w-4 h-4" />
                            </motion.button>

                            <motion.button
                                type="button"
                                onClick={toggleAll}
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                className={cn(
                                    "p-2 rounded-lg text-sm font-medium transition-all",
                                    showCode && showBottomPanel && showIPhone && showAndroid
                                        ? "bg-violet-500/20 text-violet-300"
                                        : "bg-white/[0.05] text-white/40 hover:bg-white/10 hover:text-white/60"
                                )}
                                title="Toggle All Panels"
                            >
                                <Maximize2 className="w-4 h-4" />
                            </motion.button>

                            <div className="w-px h-6 bg-white/10" />

                            <motion.button
                                type="button"
                                onClick={() => setShowChannel(true)}
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                className="p-2 rounded-lg text-sm font-medium transition-all bg-violet-500/10 text-violet-300 hover:bg-violet-500/20"
                                title="Open Channels"
                            >
                                <Hash className="w-4 h-4" />
                            </motion.button>
                        </div>

                        <motion.button
                            type="button"
                            onClick={handleSendMessage}
                            whileHover={{ scale: 1.01 }}
                            whileTap={{ scale: 0.98 }}
                            disabled={isTyping || !value.trim()}
                            className={cn(
                                "px-4 py-2 rounded-lg text-sm font-medium transition-all",
                                "flex items-center gap-2",
                                value.trim() && !isTyping
                                    ? "bg-white text-[#0A0A0B] shadow-lg shadow-white/10"
                                    : "bg-white/[0.05] text-white/40"
                            )}
                        >
                            {isTyping ? (
                                <LoaderIcon className="w-4 h-4 animate-[spin_2s_linear_infinite]" />
                            ) : (
                                <SendIcon className="w-4 h-4" />
                            )}
                            <span>Send</span>
                        </motion.button>
                    </div>
                </motion.div>
            </div>
            </motion.div>

            {/* Removed auto-showing planner sidebar - use button in chat bar instead */}

            {/* AI Planning Panel - Toggleable, content-wrapped, anchored to top */}
            {isMounted && (
                <AnimatePresence>
                    {showPlanningPanel && (
                        <motion.div 
                            className="fixed left-[52rem] top-6 w-[420px] z-40 pointer-events-auto"
                            initial={{ opacity: 0, y: -50 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -50 }}
                            transition={{ 
                                type: "spring",
                                stiffness: 300,
                                damping: 30
                            }}
                        >
                            <div className="max-h-[calc(100vh-3rem)] overflow-y-auto">
                                <div className="bg-black/60 backdrop-blur-sm border border-white/10 rounded-xl shadow-2xl">
                                    <Plan />
                                </div>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            )}

            {/* Code Window - Top right, slides down */}
            {isMounted && (
                <AnimatePresence>
                    {showCode && (
                        <motion.div 
                            className="fixed right-0 top-0 z-[55] shadow-2xl"
                            style={{ 
                                height: showBottomPanel ? `${codeHeight}vh` : '100vh',
                                width: `${rightPanelWidth}px`
                            }}
                            initial={{ opacity: 0, y: -600 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -600 }}
                            transition={{ 
                                type: "spring",
                                stiffness: 300,
                                damping: 30
                            }}
                        >
                            {/* Right Panel Width Resizer - Left Edge */}
                            <div
                                className={cn(
                                    "absolute left-0 top-0 bottom-0 w-[6px] flex items-center justify-center z-50 transition-all group",
                                    isResizingRightPanel ? "bg-violet-500/50" : "bg-white/5 hover:bg-violet-500/30",
                                    isRightPanelLocked && "opacity-50"
                                )}
                                style={{ cursor: isRightPanelLocked ? 'default' : 'ew-resize' }}
                                onMouseDown={handleRightPanelMouseDown}
                            >
                                <div className="absolute left-1 top-1/2 -translate-y-1/2 flex flex-col items-center gap-1.5 py-2 px-1.5 rounded-md bg-black/80 backdrop-blur-sm border border-white/10 shadow-lg">
                                    <GripVertical className="w-3.5 h-3.5 text-white/60 rotate-90" />
                                    <button
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            setIsRightPanelLocked(!isRightPanelLocked);
                                        }}
                                        className="p-1 rounded hover:bg-white/10 transition-colors"
                                        title={isRightPanelLocked ? "Unlock panel resize" : "Lock panel resize"}
                                    >
                                        {isRightPanelLocked ? (
                                            <Lock className="w-3 h-3 text-violet-400" />
                                        ) : (
                                            <Unlock className="w-3 h-3 text-white/50 hover:text-white/70" />
                                        )}
                                    </button>
                                </div>
                            </div>
                            <CodeWindow />
                        </motion.div>
                    )}
                </AnimatePresence>
            )}

            {/* Resizer Bar - Between Code Window and Bottom Panel */}
            {isMounted && showCode && showBottomPanel && (
                <motion.div
                    className="fixed right-0 z-[60] flex items-center justify-center"
                    style={{ 
                        top: `${codeHeight}vh`,
                        height: '4px',
                        width: `${rightPanelWidth}px`,
                        cursor: isResizeLocked ? 'default' : 'ns-resize'
                    }}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                >
                    <div 
                        className={cn(
                            "w-full h-full flex items-center justify-center transition-all",
                            isDragging ? "bg-violet-500/50" : "bg-white/5 hover:bg-violet-500/30",
                            isResizeLocked && "opacity-50"
                        )}
                        onMouseDown={handleMouseDown}
                    >
                        <div className="flex items-center gap-2 px-3 py-0.5 rounded-full bg-black/60 backdrop-blur-sm">
                            <GripHorizontal className="w-4 h-4 text-white/50" />
                            <button
                                onClick={() => setIsResizeLocked(!isResizeLocked)}
                                className="p-1 rounded hover:bg-white/10 transition-colors"
                                title={isResizeLocked ? "Unlock resize" : "Lock resize"}
                            >
                                {isResizeLocked ? (
                                    <Lock className="w-3 h-3 text-violet-400" />
                                ) : (
                                    <Unlock className="w-3 h-3 text-white/50" />
                                )}
                            </button>
                        </div>
                    </div>
                </motion.div>
            )}

            {/* Bottom Panel - Terminal/Debug/Logs - Fixed at bottom */}
            {isMounted && (
                <AnimatePresence>
                    {showBottomPanel && (
                        <motion.div 
                            className="fixed right-0 z-50 shadow-2xl"
                            style={{ 
                                height: showCode ? `${100 - codeHeight}vh` : '45vh',
                                width: `${rightPanelWidth}px`,
                                bottom: '0px',
                                top: showCode ? `${codeHeight}vh` : 'auto'
                            }}
                            initial={{ opacity: 0, y: 500 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: 500 }}
                            transition={{ 
                                type: "spring",
                                stiffness: 300,
                                damping: 30
                            }}
                        >
                            <BottomPanel onClose={() => setShowBottomPanel(false)} />
                        </motion.div>
                    )}
                </AnimatePresence>
            )}

            {/* iPhone Simulator - Slides in from right */}
            {isMounted && (
                <AnimatePresence>
                    {showIPhone && (
                        <motion.div 
                            className="fixed right-0 top-0 bottom-0 w-[600px] z-[70] shadow-2xl"
                            initial={{ opacity: 0, x: 600 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: 600 }}
                            transition={{ 
                                type: "spring",
                                stiffness: 300,
                                damping: 30
                            }}
                        >
                            <div className="relative h-full">
                                <button
                                    onClick={() => setShowIPhone(false)}
                                    className="absolute top-4 right-4 z-[80] p-2 rounded-lg bg-black/60 backdrop-blur-sm border border-white/10 hover:bg-white/10 transition-colors"
                                    title="Close iPhone Simulator"
                                >
                                    <XIcon className="w-4 h-4 text-white/70" />
                                </button>
                                <IPhoneSimulator />
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            )}

            {/* Android Simulator - Slides in from right */}
            {isMounted && (
                <AnimatePresence>
                    {showAndroid && (
                        <motion.div 
                            className="fixed right-0 top-0 bottom-0 w-[600px] z-[70] shadow-2xl"
                            initial={{ opacity: 0, x: 600 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: 600 }}
                            transition={{ 
                                type: "spring",
                                stiffness: 300,
                                damping: 30
                            }}
                        >
                            <div className="relative h-full">
                                <button
                                    onClick={() => setShowAndroid(false)}
                                    className="absolute top-4 right-4 z-[80] p-2 rounded-lg bg-black/60 backdrop-blur-sm border border-white/10 hover:bg-white/10 transition-colors"
                                    title="Close Android Simulator"
                                >
                                    <XIcon className="w-4 h-4 text-white/70" />
                                </button>
                                <AndroidSimulator />
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            )}

            {/* Theme Picker Modal */}
            <AnimatePresence>
                {showThemeSelector && (
                    <ThemePicker
                        currentTheme={currentTheme}
                        onThemeChange={handleThemeChange}
                        onClose={() => setShowThemeSelector(false)}
                    />
                )}
            </AnimatePresence>

            {/* Account Settings Modal */}
            <AnimatePresence>
                {showAccountSettings && (
                    <AccountSettings
                        currentTheme={currentTheme}
                        onThemeChange={handleThemeChange}
                        onClose={() => setShowAccountSettings(false)}
                    />
                )}
            </AnimatePresence>

            {/* Messaging Panel */}
            <AnimatePresence>
                {showMessaging && (
                    <MessagingPanel
                        mode="messages"
                        onClose={() => setShowMessaging(false)}
                    />
                )}
            </AnimatePresence>

            {/* Channel Panel */}
            <AnimatePresence>
                {showChannel && (
                    <MessagingPanel
                        mode="channel"
                        onClose={() => setShowChannel(false)}
                    />
                )}
            </AnimatePresence>

            {/* Auth Modal */}
            <AnimatePresence>
                {showAuth && (
                    <AuthModal onClose={() => setShowAuth(false)} />
                )}
            </AnimatePresence>

            {/* GitHub Panel */}
            <AnimatePresence>
                {showGitHub && (
                    <GitHubPanel onClose={() => setShowGitHub(false)} />
                )}
            </AnimatePresence>

            {/* Admin Panel */}
            <AnimatePresence>
                {showAdminPanel && (
                    <AdminPanel onClose={() => setShowAdminPanel(false)} />
                )}
            </AnimatePresence>
        </div>
    );
}

const MessageBubble = React.memo(({ message }: { message: ChatMessage }) => {
    const [copied, setCopied] = useState(false);

    const handleCopy = async () => {
        await navigator.clipboard.writeText(message.content);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <motion.div
            initial={false}
            animate={{ opacity: 1 }}
            className={cn(
                "rounded-2xl backdrop-blur-xl relative group will-change-transform",
                message.role === "user"
                    ? "self-start max-w-[85%] p-4 bg-white/10 border border-white/10"
                    : "self-stretch max-w-full p-6 bg-white/[0.02] border border-white/5"
            )}
        >
            {message.role === "user" ? (
                <p className="text-sm text-white/90 whitespace-pre-wrap leading-relaxed">
                    {message.content}
                </p>
            ) : (
                <>
                    <MarkdownRenderer content={message.content} />
                    <CodeActionPanel message={message.content} />
                </>
            )}
            
            {/* Copy button */}
            <motion.button
                onClick={handleCopy}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className={cn(
                    "absolute top-3 right-3 p-1.5 rounded-lg transition-all opacity-0 group-hover:opacity-100",
                    copied
                        ? "bg-green-500/20 text-green-400"
                        : "bg-white/5 text-white/40 hover:bg-white/10 hover:text-white/90"
                )}
            >
                {copied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
            </motion.button>
        </motion.div>
    );
});

MessageBubble.displayName = 'MessageBubble';

function TypingDots() {
    return (
        <div className="flex items-center ml-1">
            {[1, 2, 3].map((dot) => (
                <motion.div
                    key={dot}
                    className="w-1.5 h-1.5 bg-white/90 rounded-full mx-0.5"
                    initial={{ opacity: 0.3 }}
                    animate={{ 
                        opacity: [0.3, 0.9, 0.3],
                        scale: [0.85, 1.1, 0.85]
                    }}
                    transition={{
                        duration: 1.2,
                        repeat: Infinity,
                        delay: dot * 0.15,
                        ease: "easeInOut",
                    }}
                    style={{
                        boxShadow: "0 0 4px rgba(255, 255, 255, 0.3)"
                    }}
                />
            ))}
        </div>
    );
}
