"use client";

import ReactMarkdown from "react-markdown";
import { CodeCanvas, InlineCode } from "./code-canvas";
import { motion } from "framer-motion";

interface MarkdownRendererProps {
  content: string;
}

export function MarkdownRenderer({ content }: MarkdownRendererProps) {
  return (
    <div className="prose prose-invert max-w-none">
      <ReactMarkdown
        components={{
          // Code blocks with canvas
          code({ node, className, children, ...props }: any) {
            const match = /language-(\w+)/.exec(className || "");
            const codeString = String(children).replace(/\n$/, "");
            const inline = !className;
            
            if (!inline && match) {
              const language = match[1];
              
              // Special handling for diff blocks
              if (language === 'diff') {
                return (
                  <div className="my-4 rounded-lg overflow-hidden bg-black/20 backdrop-blur-sm">
                    <div className="flex items-center justify-between px-4 py-2 bg-white/[0.02]">
                      <span className="text-xs text-white/50 font-mono">Code Changes</span>
                    </div>
                    <pre className="p-4 overflow-x-auto text-sm">
                      <code className="font-mono">
                        {codeString.split('\n').map((line, i) => {
                          if (line.startsWith('+')) {
                            return (
                              <div key={i} className="text-green-400 bg-green-500/10 -mx-4 px-4">
                                {line}
                              </div>
                            );
                          } else if (line.startsWith('-')) {
                            return (
                              <div key={i} className="text-red-400 bg-red-500/10 -mx-4 px-4">
                                {line}
                              </div>
                            );
                          } else if (line.startsWith('//') || line.startsWith('#')) {
                            return (
                              <div key={i} className="text-white/40 italic">
                                {line}
                              </div>
                            );
                          }
                          return (
                            <div key={i} className="text-white/60">
                              {line}
                            </div>
                          );
                        })}
                      </code>
                    </pre>
                  </div>
                );
              }
              
              return (
                <CodeCanvas
                  code={codeString}
                  language={language}
                />
              );
            }
            
            return <InlineCode>{codeString}</InlineCode>;
          },
          
          // Headings
          h1({ children }) {
            return (
              <motion.h1
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                className="text-2xl font-bold text-white/90 mt-6 mb-4 border-b border-white/10 pb-2"
              >
                {children}
              </motion.h1>
            );
          },
          h2({ children }) {
            return (
              <motion.h2
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                className="text-xl font-semibold text-white/90 mt-5 mb-3"
              >
                {children}
              </motion.h2>
            );
          },
          h3({ children }) {
            return (
              <motion.h3
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                className="text-lg font-semibold text-white/85 mt-4 mb-2"
              >
                {children}
              </motion.h3>
            );
          },
          
          // Paragraphs
          p({ children }) {
            return (
              <p className="text-white/80 leading-relaxed mb-4">
                {children}
              </p>
            );
          },
          
          // Lists
          ul({ children }) {
            return (
              <ul className="list-disc list-inside space-y-2 text-white/80 mb-4 ml-2">
                {children}
              </ul>
            );
          },
          ol({ children }) {
            return (
              <ol className="list-decimal list-inside space-y-2 text-white/80 mb-4 ml-2">
                {children}
              </ol>
            );
          },
          li({ children }) {
            return (
              <li className="text-white/80 leading-relaxed">
                {children}
              </li>
            );
          },
          
          // Blockquotes
          blockquote({ children }) {
            return (
              <blockquote className="border-l-4 border-violet-500/50 pl-4 py-2 my-4 bg-white/5 rounded-r">
                <div className="text-white/70 italic">{children}</div>
              </blockquote>
            );
          },
          
          // Links
          a({ href, children }) {
            // Special styling for planner links (swarm links)
            if (href?.startsWith('/planner/')) {
              return (
                <a
                  href={href}
                  className="inline-flex items-center gap-2 px-4 py-2 my-2 bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-700 hover:to-purple-700 text-white rounded-lg font-medium transition-all shadow-lg shadow-violet-500/25 hover:shadow-violet-500/40 hover:scale-105"
                >
                  <span className="text-lg">🚀</span>
                  {children}
                </a>
              );
            }
            
            return (
              <a
                href={href}
                target="_blank"
                rel="noopener noreferrer"
                className="text-violet-400 hover:text-violet-300 underline underline-offset-2 transition-colors"
              >
                {children}
              </a>
            );
          },
          
          // Horizontal rule
          hr() {
            return <hr className="border-white/10 my-6" />;
          },
          
          // Tables
          table({ children }) {
            return (
              <div className="overflow-x-auto my-4">
                <table className="min-w-full border-collapse border border-white/10">
                  {children}
                </table>
              </div>
            );
          },
          th({ children }) {
            return (
              <th className="border border-white/10 bg-white/5 px-4 py-2 text-left text-white/90 font-semibold">
                {children}
              </th>
            );
          },
          td({ children }) {
            return (
              <td className="border border-white/10 px-4 py-2 text-white/80">
                {children}
              </td>
            );
          },
          
          // Strong/Bold
          strong({ children }) {
            return <strong className="font-semibold text-white/95">{children}</strong>;
          },
          
          // Emphasis/Italic
          em({ children }) {
            return <em className="italic text-white/85">{children}</em>;
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
