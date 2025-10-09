"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Copy, Check, Trash2, Download, Code2, FileCode, 
  Folder, FolderOpen, File, Plus, Edit3, X, 
  ChevronRight, ChevronDown, Search, MoreVertical,
  GripVertical, Lock, Unlock, Monitor, RefreshCw, FileUp,
  Scissors, Info, Edit, FolderEdit
} from "lucide-react";
import { sanitizeUrl } from "@/lib/sanitize-url";
import { cn } from "@/lib/utils";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";

interface FileNode {
  id: string;
  name: string;
  type: 'file' | 'folder';
  path: string;
  children?: FileNode[];
  language?: string;
  code?: string;
}

interface CodeTab {
  id: string;
  filename: string;
  language: string;
  code: string;
  path: string;
  isDirty: boolean;
}

// Mock file tree structure
const mockFileTree: FileNode[] = [
  {
    id: '1',
    name: 'components',
    type: 'folder',
    path: '/components',
    children: [
      {
        id: '1-1',
        name: 'Button.tsx',
        type: 'file',
        path: '/components/Button.tsx',
        language: 'typescript',
        code: `export function Button({ children, ...props }) {
  return (
    <button className="btn" {...props}>
      {children}
    </button>
  );
}`
      },
      {
        id: '1-2',
        name: 'ui',
        type: 'folder',
        path: '/components/ui',
        children: [
          {
            id: '1-2-1',
            name: 'code-canvas.tsx',
            type: 'file',
            path: '/components/ui/code-canvas.tsx',
            language: 'typescript',
            code: '// Code canvas component\nexport function CodeCanvas() {}'
          }
        ]
      }
    ]
  },
  {
    id: '2',
    name: 'app',
    type: 'folder',
    path: '/app',
    children: [
      {
        id: '2-1',
        name: 'page.tsx',
        type: 'file',
        path: '/app/page.tsx',
        language: 'typescript',
        code: '// Main page\nexport default function Page() {\n  return <div>Home</div>;\n}'
      }
    ]
  },
  {
    id: '3',
    name: 'README.md',
    type: 'file',
    path: '/README.md',
    language: 'markdown',
    code: '# My Project\n\nWelcome to the project!'
  }
];

export function CodeWindow() {
  const [fileTree] = useState<FileNode[]>(mockFileTree);
  const [openTabs, setOpenTabs] = useState<CodeTab[]>([]);
  const [activeTab, setActiveTab] = useState<string | null>(null);
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set(['1', '2']));
  const [copied, setCopied] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [explorerWidth, setExplorerWidth] = useState(264); // pixels
  const [isExplorerLocked, setIsExplorerLocked] = useState(false);
  const [isResizingExplorer, setIsResizingExplorer] = useState(false);
  const [activeView, setActiveView] = useState<'code' | 'preview'>('code');
  const [previewUrl, setPreviewUrl] = useState('http://localhost:3000');
  const [contextMenu, setContextMenu] = useState<{ x: number; y: number; node: FileNode } | null>(null);
  const [clipboard, setClipboard] = useState<{ node: FileNode; action: 'cut' | 'copy' } | null>(null);
  const [renamingNode, setRenamingNode] = useState<string | null>(null);
  const [renameValue, setRenameValue] = useState('');

  const handleCopy = async (code: string) => {
    await navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const openFile = (file: FileNode) => {
    if (file.type !== 'file' || !file.code) return;
    
    // Check if tab already exists
    const existingTab = openTabs.find(tab => tab.path === file.path);
    if (existingTab) {
      setActiveTab(existingTab.id);
      return;
    }

    // Create new tab
    const newTab: CodeTab = {
      id: file.id,
      filename: file.name,
      language: file.language || 'text',
      code: file.code,
      path: file.path,
      isDirty: false
    };

    setOpenTabs([...openTabs, newTab]);
    setActiveTab(newTab.id);
  };

  const closeTab = (tabId: string, e?: React.MouseEvent) => {
    e?.stopPropagation();
    const newTabs = openTabs.filter(tab => tab.id !== tabId);
    setOpenTabs(newTabs);
    
    if (activeTab === tabId) {
      setActiveTab(newTabs.length > 0 ? newTabs[newTabs.length - 1].id : null);
    }
  };

  const toggleFolder = (folderId: string) => {
    const newExpanded = new Set(expandedFolders);
    if (newExpanded.has(folderId)) {
      newExpanded.delete(folderId);
    } else {
      newExpanded.add(folderId);
    }
    setExpandedFolders(newExpanded);
  };

  const handleExplorerMouseDown = () => {
    if (!isExplorerLocked) {
      setIsResizingExplorer(true);
    }
  };

  // Handle explorer resize
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (isResizingExplorer && !isExplorerLocked) {
        e.preventDefault();
        const codeWindow = document.querySelector('[data-code-window]');
        if (codeWindow) {
          const rect = codeWindow.getBoundingClientRect();
          const newWidth = e.clientX - rect.left;
          // Constrain between 200px and 500px
          const constrainedWidth = Math.max(200, Math.min(500, newWidth));
          setExplorerWidth(constrainedWidth);
        }
      }
    };

    const handleMouseUp = () => {
      setIsResizingExplorer(false);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };

    if (isResizingExplorer) {
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
  }, [isResizingExplorer, isExplorerLocked]);

  const activeTabData = openTabs.find(tab => tab.id === activeTab);

  // Render file tree recursively
  const handleContextMenu = (e: React.MouseEvent, node: FileNode) => {
    e.preventDefault();
    
    // Get click position and adjust to prevent menu from going off-screen
    const menuWidth = 180;
    const menuHeight = 220;
    const x = e.clientX + menuWidth > window.innerWidth 
      ? e.clientX - menuWidth 
      : e.clientX;
    const y = e.clientY + menuHeight > window.innerHeight
      ? e.clientY - menuHeight
      : e.clientY;
    
    setContextMenu({ x, y, node });
  };

  const handleRename = (node: FileNode) => {
    setRenamingNode(node.id);
    setRenameValue(node.name);
    setContextMenu(null);
  };

  const confirmRename = (nodeId: string) => {
    // TODO: Implement actual rename in file tree
    console.log('Rename', nodeId, 'to', renameValue);
    setRenamingNode(null);
  };

  const handleDelete = (node: FileNode) => {
    // TODO: Implement actual delete from file tree
    console.log('Delete', node.name);
    setContextMenu(null);
  };

  const handleCut = (node: FileNode) => {
    setClipboard({ node, action: 'cut' });
    setContextMenu(null);
  };

  const handleCopyNode = (node: FileNode) => {
    setClipboard({ node, action: 'copy' });
    setContextMenu(null);
  };

  const handleInfo = (node: FileNode) => {
    console.log('File info:', node);
    alert(`File: ${node.name}\nPath: ${node.path || 'N/A'}\nType: ${node.type}`);
    setContextMenu(null);
  };

  useEffect(() => {
    const handleClickOutside = () => setContextMenu(null);
    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, []);

  const renderFileTree = (nodes: FileNode[], depth: number = 0) => {
    return nodes.map(node => (
      <div key={node.id}>
        {renamingNode === node.id ? (
          <div style={{ paddingLeft: `${8 + depth * 16}px` }} className="px-2 py-1">
            <input
              type="text"
              value={renameValue}
              onChange={(e) => setRenameValue(e.target.value)}
              onBlur={() => confirmRename(node.id)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') confirmRename(node.id);
                if (e.key === 'Escape') setRenamingNode(null);
              }}
              autoFocus
              className="w-full px-1 py-0.5 text-xs bg-white/10 border border-violet-500/50 rounded text-white/90 focus:outline-none"
            />
          </div>
        ) : (
          <button
            onClick={() => node.type === 'folder' ? toggleFolder(node.id) : openFile(node)}
            onContextMenu={(e) => handleContextMenu(e, node)}
            className={cn(
              "w-full flex items-center gap-2 px-2 py-1 text-xs hover:bg-white/5 transition-colors group",
              activeTab === node.id && "bg-violet-500/10"
            )}
            style={{ paddingLeft: `${8 + depth * 16}px` }}
          >
            {node.type === 'folder' ? (
              <>
                {expandedFolders.has(node.id) ? (
                  <ChevronDown className="w-3 h-3 text-white/40" />
                ) : (
                  <ChevronRight className="w-3 h-3 text-white/40" />
                )}
                {expandedFolders.has(node.id) ? (
                  <FolderOpen className="w-3.5 h-3.5 text-violet-400" />
                ) : (
                  <Folder className="w-3.5 h-3.5 text-violet-400" />
                )}
              </>
            ) : (
              <File className="w-3.5 h-3.5 text-white/50 ml-5" />
            )}
            <span className="text-white/70 truncate group-hover:text-white/90">
              {node.name}
            </span>
          </button>
        )}
        {node.type === 'folder' && node.children && expandedFolders.has(node.id) && (
          <div>
            {renderFileTree(node.children, depth + 1)}
          </div>
        )}
      </div>
    ));
  };

  return (
    <div className="h-full flex bg-black/60 backdrop-blur-sm border-b border-white/10 relative" data-code-window>
      {/* File Explorer - Left Side */}
      <div className="flex flex-col border-r border-white/10 bg-white/[0.01]" style={{ width: `${explorerWidth}px` }}>
        {/* Explorer Header */}
        <div className="px-3 py-2 border-b border-white/10 bg-white/[0.02]">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-white/80">EXPLORER</span>
            <div className="flex items-center gap-1">
              <button className="p-1 rounded hover:bg-white/10 text-white/40 hover:text-white/70 transition-colors">
                <Plus className="w-3 h-3" />
              </button>
              <button className="p-1 rounded hover:bg-white/10 text-white/40 hover:text-white/70 transition-colors">
                <Search className="w-3 h-3" />
              </button>
            </div>
          </div>
          <input
            type="text"
            placeholder="Search files..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-2 py-1 text-xs bg-white/5 border border-white/10 rounded text-white/80 placeholder-white/30 focus:outline-none focus:border-violet-500/50"
          />
        </div>

        {/* File Tree */}
        <div className="flex-1 overflow-y-auto py-2">
          {renderFileTree(fileTree)}
        </div>

        {/* Explorer Footer */}
        <div className="px-3 py-2 border-t border-white/10 bg-white/[0.02]">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[10px] text-white/40">Files: {fileTree.length} | Tabs: {openTabs.length}</span>
          </div>
          <button 
            onClick={() => {
              const input = document.createElement('input');
              input.type = 'file';
              input.webkitdirectory = true;
              input.multiple = true;
              input.onchange = (e: any) => {
                const files = Array.from(e.target.files);
                console.log('Uploaded project files:', files);
                // TODO: Process uploaded files and add to file tree
              };
              input.click();
            }}
            className="w-full px-3 py-1.5 text-xs font-medium bg-violet-500/20 hover:bg-violet-500/30 text-violet-300 rounded transition-colors flex items-center justify-center gap-2"
          >
            <FileUp className="w-3.5 h-3.5" />
            Upload Project
          </button>
        </div>
      </div>

      {/* Code Editor - Right Side */}
      <div className="flex-1 flex flex-col">
        {/* Header with View Tabs */}
        <div className="flex items-center justify-between border-b border-white/10 bg-white/[0.02]">
          <div className="flex items-center">
            {/* Code Viewer Tab */}
            <button
              onClick={() => setActiveView('code')}
              className={cn(
                "flex items-center gap-2 px-4 py-2 text-xs font-medium transition-all border-b-2",
                activeView === 'code'
                  ? "text-white/90 border-violet-500 bg-white/5"
                  : "text-white/50 border-transparent hover:text-white/70 hover:bg-white/[0.02]"
              )}
            >
              <Code2 className="w-3.5 h-3.5" />
              <span>Code Viewer</span>
            </button>
            
            {/* Browser Preview Tab */}
            <button
              onClick={() => setActiveView('preview')}
              className={cn(
                "flex items-center gap-2 px-4 py-2 text-xs font-medium transition-all border-b-2",
                activeView === 'preview'
                  ? "text-white/90 border-violet-500 bg-white/5"
                  : "text-white/50 border-transparent hover:text-white/70 hover:bg-white/[0.02]"
              )}
            >
              <Monitor className="w-3.5 h-3.5" />
              <span>Preview</span>
            </button>
          </div>
          
          <div className="flex items-center gap-2 px-4">
            {activeView === 'code' && activeTabData && (
              <button
                onClick={() => handleCopy(activeTabData.code)}
                className="p-1 rounded hover:bg-white/10 text-white/50 hover:text-white/80 transition-colors"
                title="Copy code"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-green-400" /> : <Copy className="w-3.5 h-3.5" />}
              </button>
            )}
            {activeView === 'preview' && (
              <button
                onClick={() => {
                  const iframe = document.querySelector('[data-preview-frame]') as HTMLIFrameElement;
                  if (iframe) iframe.src = sanitizeUrl(iframe.src);
                }}
                className="p-1 rounded hover:bg-white/10 text-white/50 hover:text-white/80 transition-colors"
                title="Refresh preview"
              >
                <RefreshCw className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
        </div>

        {/* Tabs Bar */}
        {openTabs.length > 0 && (
          <div className="flex items-center gap-1 px-2 py-1 bg-white/[0.01] border-b border-white/10 overflow-x-auto">
            <AnimatePresence>
              {openTabs.map(tab => (
                <motion.button
                  key={tab.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  onClick={() => setActiveTab(tab.id)}
                  className={cn(
                    "flex items-center gap-2 px-3 py-1.5 rounded-md text-xs transition-all group",
                    activeTab === tab.id
                      ? "bg-white/10 text-white/90"
                      : "text-white/60 hover:bg-white/5"
                  )}
                >
                  <File className="w-3 h-3" />
                  <span className="font-mono">{tab.filename}</span>
                  {tab.isDirty && <span className="w-1.5 h-1.5 rounded-full bg-violet-400" />}
                  <button
                    onClick={(e) => closeTab(tab.id, e)}
                    className="opacity-0 group-hover:opacity-100 hover:bg-white/10 p-0.5 rounded transition-all"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </motion.button>
              ))}
            </AnimatePresence>
          </div>
        )}

        {/* Content Display - Code or Preview */}
        {activeView === 'code' ? (
          // Code View
          activeTabData ? (
            <div className="flex-1 overflow-auto bg-black">
              <SyntaxHighlighter
                language={activeTabData.language}
                style={oneDark}
                customStyle={{
                  margin: 0,
                  padding: "1.5rem",
                  background: "#000000",
                  fontSize: "0.875rem",
                  lineHeight: "1.6",
                  height: "100%",
                }}
                showLineNumbers={true}
                wrapLines={true}
                lineNumberStyle={{
                  minWidth: "3em",
                  paddingRight: "1em",
                  color: "rgba(255, 255, 255, 0.7)",
                  fontSize: "0.7rem",
                  userSelect: "none",
                }}
              >
                {activeTabData.code}
              </SyntaxHighlighter>
            </div>
          ) : (
            <div className="flex-1 flex items-center justify-center text-white/30 text-sm bg-black">
              <div className="text-center">
                <FileCode className="w-16 h-16 mx-auto mb-3 opacity-30" />
                <p>No file selected</p>
                <p className="text-xs mt-1 text-white/20">Click a file to view its content</p>
              </div>
            </div>
          )
        ) : (
          // Browser Preview
          <div className="flex-1 flex flex-col bg-black">
            <div className="px-4 py-2 bg-white/[0.02] border-b border-white/10 flex items-center gap-2">
              <input
                type="text"
                value={previewUrl}
                onChange={(e) => setPreviewUrl(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    const iframe = document.querySelector('[data-preview-frame]') as HTMLIFrameElement;
                    if (iframe) iframe.src = sanitizeUrl(previewUrl);
                  }
                }}
                className="flex-1 px-3 py-1.5 text-xs bg-white/5 border border-white/10 rounded text-white/80 placeholder-white/30 focus:outline-none focus:border-violet-500/50 font-mono"
                placeholder="Enter URL to preview..."
              />
              <button
                onClick={() => {
                  const iframe = document.querySelector('[data-preview-frame]') as HTMLIFrameElement;
                  if (iframe) iframe.src = sanitizeUrl(previewUrl);
                }}
                className="px-3 py-1.5 text-xs bg-violet-500/20 hover:bg-violet-500/30 text-violet-300 rounded transition-colors"
              >
                Go
              </button>
            </div>
            <div className="flex-1 relative">
              <iframe
                data-preview-frame
                src={sanitizeUrl(previewUrl)}
                className="absolute inset-0 w-full h-full bg-white"
                sandbox="allow-same-origin allow-scripts allow-forms allow-modals allow-popups"
                title="Browser Preview"
              />
            </div>
          </div>
        )}

        {/* Footer - Only show in code view */}
        {activeView === 'code' && activeTabData && (
          <div className="px-4 py-1.5 border-t border-white/10 bg-white/[0.02] text-[10px] text-white/40 flex justify-between">
            <span className="font-mono">{activeTabData.path}</span>
            <div className="flex items-center gap-3">
              <span>{activeTabData.code.split('\n').length} lines</span>
              <span className="text-violet-400">
                {(activeTabData.code.length / 1024).toFixed(1)} KB
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Context Menu */}
      <AnimatePresence>
        {contextMenu && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.1 }}
            className="fixed z-[100] bg-black/90 backdrop-blur-sm border border-white/20 rounded-lg shadow-2xl py-1 min-w-[180px]"
            style={{
              left: contextMenu.x,
              top: contextMenu.y,
            }}
          >
            <button
              onClick={() => handleRename(contextMenu.node)}
              className="w-full px-3 py-1.5 text-xs text-white/80 hover:bg-white/10 flex items-center gap-2 transition-colors"
            >
              <Edit className="w-3.5 h-3.5" />
              Rename
            </button>
            <button
              onClick={() => contextMenu.node.type === 'file' && openFile(contextMenu.node)}
              className="w-full px-3 py-1.5 text-xs text-white/80 hover:bg-white/10 flex items-center gap-2 transition-colors"
            >
              <Edit3 className="w-3.5 h-3.5" />
              Edit
            </button>
            <div className="h-px bg-white/10 my-1" />
            <button
              onClick={() => handleCut(contextMenu.node)}
              className="w-full px-3 py-1.5 text-xs text-white/80 hover:bg-white/10 flex items-center gap-2 transition-colors"
            >
              <Scissors className="w-3.5 h-3.5" />
              Cut
            </button>
            <button
              onClick={() => handleCopyNode(contextMenu.node)}
              className="w-full px-3 py-1.5 text-xs text-white/80 hover:bg-white/10 flex items-center gap-2 transition-colors"
            >
              <Copy className="w-3.5 h-3.5" />
              Copy
            </button>
            <div className="h-px bg-white/10 my-1" />
            <button
              onClick={() => handleDelete(contextMenu.node)}
              className="w-full px-3 py-1.5 text-xs text-red-400 hover:bg-red-500/10 flex items-center gap-2 transition-colors"
            >
              <Trash2 className="w-3.5 h-3.5" />
              Delete
            </button>
            <div className="h-px bg-white/10 my-1" />
            <button
              onClick={() => handleInfo(contextMenu.node)}
              className="w-full px-3 py-1.5 text-xs text-white/80 hover:bg-white/10 flex items-center gap-2 transition-colors"
            >
              <Info className="w-3.5 h-3.5" />
              Info
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
