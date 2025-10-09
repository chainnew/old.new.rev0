# 🗄️ PostgreSQL 2M Context Setup Guide

## **What's Configured:**
- ✅ 2M token context window (2,000,000 tokens!)
- ✅ Full conversation history saved to PostgreSQL
- ✅ Persistent chat across sessions
- ✅ Vector embeddings ready for RAG (future)
- ✅ Auto-scroll to latest messages
- ✅ Sleek custom scrollbar

---

## **Quick Setup (5 minutes)**

### **1. Install PostgreSQL**

**Mac (Homebrew):**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**Docker (easiest):**
```bash
docker run -d \
  --name postgres-chat \
  -e POSTGRES_PASSWORD=yourpassword \
  -e POSTGRES_DB=ai_chat_db \
  -p 5432:5432 \
  postgres:15-alpine
```

### **2. Create Database**

```bash
# Connect to PostgreSQL
psql postgres

# Create database and user
CREATE DATABASE ai_chat_db;
CREATE USER ai_chat_user WITH ENCRYPTED PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE ai_chat_db TO ai_chat_user;
\q
```

### **3. Set Environment Variable**

Add to your `.env` file:
```bash
DATABASE_URL="postgresql://ai_chat_user:your_secure_password@localhost:5432/ai_chat_db?schema=public"
```

### **4. Run Migrations**

```bash
# Generate Prisma Client
npx prisma generate

# Apply schema to database
psql -U ai_chat_user -d ai_chat_db -f database/schema.sql

# Or use Prisma (simpler)
npx prisma db push
```

### **5. Start Your App**

```bash
npm run dev
```

---

## **Verification**

Test the setup:
```bash
# Check if tables were created
psql -U ai_chat_user -d ai_chat_db -c "\dt"

# Should show:
# - users
# - conversations  
# - messages
# - tasks
# - subtasks
```

---

## **Features Now Active:**

### **🎨 Frontend**
- Full-height scrollable chat window
- Larger text input (100px min)
- Auto-scroll to latest messages
- Sleek violet scrollbar (6px wide)
- Loads conversation history on mount

### **🔌 Backend**
- 2M token context window
- PostgreSQL persistence
- Conversation history API
- Auto-title generation
- Token usage tracking

### **📊 Database Schema**
- `conversations` table with 2M context window
- `messages` table for full chat history
- `tasks` & `subtasks` for planner
- Vector embeddings ready (for future RAG)
- Full-text search indexes

---

## **Usage**

```typescript
// Chat automatically:
// 1. Loads conversation history on page load
// 2. Saves every message to PostgreSQL
// 3. Maintains 2M token context window
// 4. Auto-generates conversation titles

// Access conversation:
fetch(`/api/conversations/${conversationId}`)
```

---

## **Troubleshooting**

### **"Cannot find module '@prisma/client'"**
```bash
npx prisma generate
```

### **"Connection refused to database"**
```bash
# Check if PostgreSQL is running
brew services list | grep postgresql
# or
sudo systemctl status postgresql
```

### **"relation does not exist"**
```bash
# Apply schema
psql -U ai_chat_user -d ai_chat_db -f database/schema.sql
```

---

## **Next Steps**

1. **Vector Embeddings**: Add OpenAI embeddings for semantic search
2. **RAG Integration**: Query past conversations intelligently  
3. **Multi-user**: Add user authentication (Clerk/NextAuth)
4. **Export**: Download conversation history as JSON/MD

---

**Your chat now has INFINITE memory powered by PostgreSQL! 🚀**
