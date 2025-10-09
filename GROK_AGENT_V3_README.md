# Grok Agent v3 - OpenRouter & XAI Support

## 🚀 Features
- **Multi-provider support**: OpenRouter (with grok-2-1212) or XAI Direct
- **Async operations**: Fast parallel GitHub content fetching
- **Smart retry logic**: Handles rate limits with exponential backoff
- **Token tracking**: Logs usage for cost monitoring

## 📦 Setup

### 1. Install Dependencies
```bash
pip install aiohttp python-dotenv
```

### 2. Environment Variables

Create a `.env` file with one of these configurations:

#### Option A: OpenRouter (Recommended - supports many models)
```env
# Provider selection
AI_PROVIDER=openrouter

# OpenRouter credentials
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=x-ai/grok-4-fast
OPENROUTER_REFERER=http://localhost:3000
OPENROUTER_APP_NAME=Grok Agent v3

# GitHub (optional, increases rate limits)
GITHUB_TOKEN=your_github_token_here
```

#### Option B: XAI Direct
```env
# Provider selection
AI_PROVIDER=xai

# XAI credentials
XAI_API_KEY=your_xai_api_key_here
XAI_MODEL=grok-beta

# GitHub (optional)
GITHUB_TOKEN=your_github_token_here
```

## 🎯 Available Models

### OpenRouter Models
- `x-ai/grok-2-1212` - Latest Grok model (recommended)
- `x-ai/grok-beta` - Beta Grok model
- `anthropic/claude-3.5-sonnet` - Claude 3.5 Sonnet
- `openai/gpt-4-turbo` - GPT-4 Turbo
- `openai/gpt-3.5-turbo` - GPT-3.5 Turbo
- Many more at https://openrouter.ai/models

### XAI Direct Models
- `grok-beta` - XAI's Grok Beta

## 🏃 Usage

```bash
python improved_grok_agent_v3_openrouter.py
```

## 📝 Configuration Options

The script accepts these parameters in `main_async()`:

```python
await main_async(
    input_file='ui_raw_scrape.json',  # Your input JSON file
    goal='Extract UI components and stencils for web dev library.'
)
```

In `run_agent_async()`:
- `target_dirs`: Directories to scrape (default: `['components', 'styles', 'css', 'ui', 'diagrams']`)
- `max_files_per_dir`: Files to fetch per directory (default: 5)

## 📊 Output

The script generates:
- `ui_raw_scrape_enriched_v3_openrouter.json` - Enriched results with extracted components
- `grok_agent_log.txt` - Detailed logs with token usage

## 💡 Tips

1. **OpenRouter** is recommended because:
   - Single API key for multiple models
   - Better rate limits
   - Transparent pricing
   - Easy model switching

2. **Rate Limiting**:
   - Built-in exponential backoff
   - Respects 429 responses
   - Adds 2s delay between repos

3. **Cost Control**:
   - Monitor token usage in logs
   - Adjust `max_tokens` parameter
   - Limit `max_files_per_dir`

## 🔧 Troubleshooting

### Permission Denied Error
```bash
chmod +w improved_grok_agent_v3_openrouter.py
```

### API Key Not Found
Make sure your `.env` file is in the same directory and contains the correct key names.

### Rate Limit Errors
- Increase delays between requests
- Use a GitHub token to increase API limits
- Reduce `max_files_per_dir`

## 📚 Example .env

```env
AI_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxx
OPENROUTER_MODEL=x-ai/grok-2-1212
GITHUB_TOKEN=ghp_xxxxxxxxxxxxx
```
