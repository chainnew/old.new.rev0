"use client";

import React, { createContext, useContext, useState, useCallback } from 'react';

interface CodeFile {
  id: string;
  filename: string;
  path: string;
  language: string;
  code: string;
  createdAt: number;
}

interface CodeSyncContextType {
  generatedFiles: CodeFile[];
  addGeneratedFile: (file: Omit<CodeFile, 'id' | 'createdAt'>) => void;
  clearGeneratedFiles: () => void;
  syncToCodeWindow: (files: CodeFile[]) => void;
}

const CodeSyncContext = createContext<CodeSyncContextType | undefined>(undefined);

export function CodeSyncProvider({ children }: { children: React.ReactNode }) {
  const [generatedFiles, setGeneratedFiles] = useState<CodeFile[]>([]);

  const addGeneratedFile = useCallback((file: Omit<CodeFile, 'id' | 'createdAt'>) => {
    const newFile: CodeFile = {
      ...file,
      id: `gen_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      createdAt: Date.now(),
    };
    console.log('🔥 CodeSyncContext: Adding file to state:', newFile.filename);
    setGeneratedFiles(prev => {
      const updated = [...prev, newFile];
      console.log('  📊 Total files in state:', updated.length);
      return updated;
    });
    return newFile;
  }, []);

  const clearGeneratedFiles = useCallback(() => {
    setGeneratedFiles([]);
  }, []);

  const syncToCodeWindow = useCallback((files: CodeFile[]) => {
    setGeneratedFiles(files);
  }, []);

  return (
    <CodeSyncContext.Provider value={{
      generatedFiles,
      addGeneratedFile,
      clearGeneratedFiles,
      syncToCodeWindow
    }}>
      {children}
    </CodeSyncContext.Provider>
  );
}

export function useCodeSync() {
  const context = useContext(CodeSyncContext);
  if (!context) {
    throw new Error('useCodeSync must be used within CodeSyncProvider');
  }
  return context;
}
