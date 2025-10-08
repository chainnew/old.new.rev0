# Code Canvas Features - Ruixen AI Chat

## ✨ Key Features Implemented

### 1. **1M Token Context Window**
- Full 1 million token context support via OpenRouter
- Maintains up to 20 message pairs (40 messages) in conversation history
- Automatic context management and pruning to stay within limits
- Conversation caching for consistent context across sessions

### 2. **Structured Output System**
- **Markdown Rendering**: All AI responses are rendered with proper markdown formatting
- **Code Canvas**: Beautiful syntax-highlighted code blocks with:
  - macOS-style window controls (red, yellow, green dots)
  - Language badges and filenames
  - Line numbers for multi-line code
  - One-click copy functionality with visual feedback
  - Smooth animations and hover effects
  
### 3. **Context Caching & Management**
- **Server-side caching**: Conversation history cached in memory
- **Unique conversation IDs**: Each session gets a unique identifier
- **Automatic cleanup**: Old conversations pruned to keep system tidy
- **History passing**: Full context sent with each request for continuity

### 4. **Code-Optimized AI System Prompt**
The orchestrator (API Key #1) uses a specialized system prompt:
```
- Always use proper markdown code blocks with language tags
- Structure responses clearly with headings and sections
- Break complex code into logical components
- Provide explanations before and after code blocks
- Keep code clean, well-commented, and production-ready
- Use best practices and modern patterns
```

### 5. **Advanced API Configuration**
```typescript
{
  model: "x-ai/grok-code-fast-1",
  max_tokens: 16000,           // Large output for code generation
  temperature: 0.3,            // Lower for more consistent code
  top_p: 0.9,
  frequency_penalty: 0.0,
  presence_penalty: 0.0,
  transforms: ["middle-out"]   // OpenRouter optimization
}
```

## 📦 Component Architecture

### **CodeCanvas** (`/components/ui/code-canvas.tsx`)
- Syntax highlighting via `react-syntax-highlighter`
- Prism `oneDark` theme for consistency
- Animated copy button with success state
- Hover glow effects
- Responsive overflow handling

### **MarkdownRenderer** (`/components/ui/markdown-renderer.tsx`)
- Processes all markdown elements:
  - Headers (H1, H2, H3) with animations
  - Code blocks (inline and fenced)
  - Lists (ordered & unordered)
  - Blockquotes, tables, links
  - Bold, italic, horizontal rules
- Custom styling for dark theme
- Motion animations for smooth appearance

### **AnimatedAIChat** (`/components/ui/animated-ai-chat.tsx`)
- Main chat interface with Framer Motion animations
- Command palette (`/clone`, `/figma`, `/page`, `/improve`)
- Auto-resizing textarea
- Conversation ID management
- History tracking and API integration

### **API Route** (`/app/api/chat/route.ts`)
- OpenRouter integration with 3 API keys
- Key #1: Orchestrator (handles all responses)
- Keys #2 & #3: Available for validation/parallel processing
- Context caching with Map data structure
- Automatic history management

## 🎨 Visual Features

### Code Display
```
┌─────────────────────────────────┐
│ ● ● ●  filename.tsx             │ ← macOS window bar
├─────────────────────────────────┤
│  1  import { useState } from... │ ← Line numbers
│  2  export function Demo() {    │ ← Syntax highlighting
│  3    return <div>...</div>     │
│  ...                            │
└─────────────────────────────────┘
```

### Message Bubbles
- **User messages**: Compact, right-aligned, blue-tinted
- **AI messages**: Full-width, left-aligned, with markdown rendering
- **Smooth animations**: Fade in from bottom
- **Loading state**: "Thinking..." indicator with animated dots

## 🔧 Configuration

### Environment Variables
```env
OPENROUTER_API_KEY1=sk-or-v1-...  # Orchestrator
OPENROUTER_API_KEY2=sk-or-v1-...  # Secondary
OPENROUTER_API_KEY3=sk-or-v1-...  # Tertiary
```

### Context Management
- **Max context**: 1,000,000 tokens
- **Cached messages**: 40 (20 exchanges)
- **Cache cleanup**: Automatic when limit exceeded
- **Conversation persistence**: In-memory (can be extended to Redis/DB)

## 📊 Token Optimization

1. **System prompt**: ~150 tokens (reused across calls)
2. **User messages**: Variable (depends on input)
3. **AI responses**: Up to 16,000 tokens per response
4. **History**: Last 20 exchanges (~20k-200k tokens depending on complexity)
5. **Total capacity**: Fits well within 1M token window

## 🚀 Usage Example

```typescript
// User asks for code
"Create a React component for a todo list"

// AI responds with:
- Explanation paragraph
- ```tsx code block (rendered in CodeCanvas)
- Additional notes
- Multiple files if needed (each in separate canvas)
```

## 🎯 Benefits

1. **Developer-friendly**: Code is immediately readable and copyable
2. **Professional appearance**: macOS-style canvases look polished
3. **Context-aware**: AI remembers entire conversation (up to 1M tokens)
4. **Efficient**: Caching reduces redundant API calls
5. **Structured**: Markdown ensures clean, organized output
6. **Extensible**: Easy to add more features (file attachments, streaming, etc.)

## 📝 Future Enhancements

- [ ] Streaming responses for real-time output
- [ ] File upload for code analysis
- [ ] Multi-file project scaffolding
- [ ] Export conversation to markdown
- [ ] Persistent storage (Redis/PostgreSQL)
- [ ] API Keys #2 & #3 for code validation
- [ ] Diff viewer for code changes
- [ ] Terminal output rendering
