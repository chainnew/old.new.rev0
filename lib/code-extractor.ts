/**
 * Extract code blocks from AI response and parse into file creation data
 */

export interface CodeBlock {
  filename: string;
  language: string;
  code: string;
  lineNumber: number;
}

export function extractCodeBlocks(markdown: string): CodeBlock[] {
  const codeBlocks: CodeBlock[] = [];
  
  // Match code blocks with optional filename comments
  // Supports: ```tsx // filename.tsx  OR  ```typescript\n// src/app/page.tsx
  const codeBlockRegex = /```(\w+)\s*(?:\/\/\s*(.+?))?\n([\s\S]*?)```/g;
  
  let match;
  let lineNumber = 0;
  
  while ((match = codeBlockRegex.exec(markdown)) !== null) {
    const language = match[1];
    const filenameComment = match[2]?.trim();
    const code = match[3];
    
    // Try to extract filename from various formats:
    // 1. From comment: // src/app/page.tsx
    // 2. From context before code block: "Create `src/app/page.tsx`:"
    // 3. From inside code: // File: src/components/Button.tsx
    
    let filename = filenameComment || extractFilenameFromContext(markdown, match.index);
    
    if (filename && code.trim()) {
      codeBlocks.push({
        filename: filename.replace(/^\/+/, ''), // Remove leading slashes
        language,
        code: code.trim(),
        lineNumber: lineNumber++
      });
    }
  }
  
  return codeBlocks;
}

function extractFilenameFromContext(markdown: string, blockIndex: number): string | null {
  // Look backwards from code block for filename patterns
  const beforeBlock = markdown.substring(Math.max(0, blockIndex - 500), blockIndex);
  
  // Pattern 1: "Create `filename.tsx`:"
  const pattern1 = /(?:create|update|modify|edit|add)\s+`([^`]+)`/i;
  const match1 = beforeBlock.match(pattern1);
  if (match1) return match1[1];
  
  // Pattern 2: "**filename.tsx**"
  const pattern2 = /\*\*([^\*]+\.(tsx?|jsx?|py|rs|go|java|sql|md|json|yaml|yml|toml|sh))\*\*/i;
  const match2 = beforeBlock.match(pattern2);
  if (match2) return match2[1];
  
  // Pattern 3: File: src/app/page.tsx
  const pattern3 = /(?:file|path):\s*([^\s\n]+\.(tsx?|jsx?|py|rs|go|java|sql|md|json|yaml|yml|toml|sh))/i;
  const match3 = beforeBlock.match(pattern3);
  if (match3) return match3[1];
  
  return null;
}

export function generateFileCreationCommands(codeBlocks: CodeBlock[], baseDir: string = '.'): string {
  if (codeBlocks.length === 0) return '';
  
  let commands = '#!/bin/bash\n# Auto-generated file creation script\n\n';
  
  for (const block of codeBlocks) {
    const filepath = `${baseDir}/${block.filename}`;
    const dir = filepath.substring(0, filepath.lastIndexOf('/'));
    
    commands += `# Create ${block.filename}\n`;
    commands += `mkdir -p "${dir}"\n`;
    commands += `cat > "${filepath}" << 'EOFCODE'\n`;
    commands += block.code;
    commands += `\nEOFCODE\n\n`;
  }
  
  return commands;
}
