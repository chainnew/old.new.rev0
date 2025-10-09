"use client";

import { useState, useMemo } from "react";
import { FileCode, Download, Copy, Check, Zap, AlertCircle } from "lucide-react";
import { extractCodeBlocks, generateFileCreationCommands, type CodeBlock } from "@/lib/code-extractor";

interface CodeActionPanelProps {
  message: string;
}

export function CodeActionPanel({ message }: CodeActionPanelProps) {
  const [copied, setCopied] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const [creating, setCreating] = useState(false);
  const [created, setCreated] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Extract code blocks from message (memoized to prevent re-extraction)
  const codeBlocks = useMemo(() => extractCodeBlocks(message), [message]);

  if (codeBlocks.length === 0) return null;

  const handleCopyScript = async () => {
    const script = generateFileCreationCommands(codeBlocks);
    await navigator.clipboard.writeText(script);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadScript = () => {
    const script = generateFileCreationCommands(codeBlocks);
    const blob = new Blob([script], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'create-files.sh';
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleCreateFiles = async () => {
    if (!confirm(`Create ${codeBlocks.length} file(s) in your project?\n\n${codeBlocks.map(b => '→ ' + b.filename).join('\n')}`)) {
      return;
    }

    setCreating(true);
    setError(null);

    try {
      const response = await fetch('/api/create-files', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          files: codeBlocks.map(block => ({
            filename: block.filename,
            content: block.code
          }))
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to create files');
      }

      setCreated(true);
      setTimeout(() => setCreated(false), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create files');
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="mt-4 border border-violet-500/30 rounded-lg bg-violet-950/20 p-4">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <FileCode className="w-4 h-4 text-violet-400" />
          <span className="text-sm font-semibold text-violet-300">
            {codeBlocks.length} file{codeBlocks.length > 1 ? 's' : ''} detected
          </span>
        </div>
        <button
          onClick={() => setExpanded(!expanded)}
          className="text-xs text-violet-400 hover:text-violet-300"
        >
          {expanded ? 'Hide' : 'Show'} files
        </button>
      </div>

      {expanded && (
        <div className="mb-3 space-y-1">
          {codeBlocks.map((block, idx) => (
            <div key={idx} className="text-xs text-gray-400 font-mono">
              → {block.filename}
            </div>
          ))}
        </div>
      )}

      <div className="flex flex-wrap gap-2">
        <button
          onClick={handleCreateFiles}
          disabled={creating || created}
          className="flex items-center gap-2 px-4 py-2 text-xs font-semibold bg-violet-600 hover:bg-violet-500 disabled:bg-green-600 disabled:cursor-not-allowed text-white rounded transition-colors"
        >
          {creating ? (
            <>
              <div className="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Creating...
            </>
          ) : created ? (
            <>
              <Check className="w-3 h-3" />
              Created!
            </>
          ) : (
            <>
              <Zap className="w-3 h-3" />
              Create Files Now
            </>
          )}
        </button>
        
        <button
          onClick={handleCopyScript}
          className="flex items-center gap-2 px-3 py-1.5 text-xs bg-violet-600/50 hover:bg-violet-600 text-white rounded transition-colors"
        >
          {copied ? (
            <>
              <Check className="w-3 h-3" />
              Copied!
            </>
          ) : (
            <>
              <Copy className="w-3 h-3" />
              Copy Script
            </>
          )}
        </button>
        
        <button
          onClick={handleDownloadScript}
          className="flex items-center gap-2 px-3 py-1.5 text-xs bg-violet-600/30 hover:bg-violet-600/50 text-white rounded transition-colors"
        >
          <Download className="w-3 h-3" />
          Download .sh
        </button>
      </div>

      {error && (
        <div className="mt-2 flex items-center gap-2 text-xs text-red-400">
          <AlertCircle className="w-3 h-3" />
          {error}
        </div>
      )}

      <p className="mt-2 text-xs text-gray-500">
        Click "Create Files Now" to automatically create all files in your project
      </p>
    </div>
  );
}
