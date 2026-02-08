# Setup Guide

## Windows Installation

### Option 1: Using Poetry (Recommended)

1. **Install Poetry**
   ```powershell
   (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
   ```

2. **Navigate to project directory**
   ```powershell
   cd D:\tool\personal-memory
   ```

3. **Install dependencies**
   ```powershell
   poetry install
   ```

4. **Configure environment**
   ```powershell
   copy .env.example .env
   notepad .env
   ```
   Edit the .env file and set at least:
   - `AI_PROVIDER=openai` (or `anthropic`)
   - `AI_API_KEY=your-actual-api-key`

5. **Initialize database**
   ```powershell
   poetry run pm init
   ```

6. **Test the CLI**
   ```powershell
   poetry run pm finance add "今天花了50块买午饭"
   ```

### Option 2: Using pip

1. **Navigate to project directory**
   ```powershell
   cd D:\tool\personal-memory
   ```

2. **Create virtual environment**
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```powershell
   copy .env.example .env
   notepad .env
   ```

5. **Initialize database**
   ```powershell
   python -m src.main init
   ```

6. **Test the CLI**
   ```powershell
   python -m src.main finance add "今天花了50块买午饭"
   ```

## Getting an API Key

### OpenAI
1. Go to https://platform.openai.com/api-keys
2. Create an account or sign in
3. Create a new API key
4. Use in .env:
   ```
   AI_PROVIDER=openai
   AI_API_KEY=sk-your-key-here
   AI_MODEL=gpt-4o-mini
   ```

### Anthropic Claude
1. Go to https://console.anthropic.com/
2. Create an account or sign in
3. Get your API key
4. Use in .env:
   ```
   AI_PROVIDER=anthropic
   AI_API_KEY=sk-ant-your-key-here
   AI_MODEL=claude-haiku-4-20250205
   ```

### Using a Proxy/Relay Service

If you're in China or want to use a third-party service:

```
AI_PROVIDER=openai
AI_API_KEY=your-custom-key
AI_BASE_URL=https://your-proxy-service.com/v1
AI_MODEL=gpt-4o-mini
```

## Quick Start Commands

```bash
# Initialize
pm init

# Add records
pm finance add "今天花了50块买午饭"
pm health add "昨晚睡了8小时，睡得很好"
pm work add "今天工作8小时，完成了用户认证模块"
pm leisure add "看了2小时电影"

# View reports
pm report daily
pm finance list --days 7
pm work summary
```

## Troubleshooting

### "No module named 'src'"
Make sure you're running from the project root directory:
```powershell
cd D:\tool\personal-memory
```

### "AI API error"
Check your .env file:
- API_KEY is set correctly
- API_PROVIDER is valid (openai or anthropic)
- For OpenAI, check if BASE_URL is accessible

### Database errors
```powershell
# Re-initialize database
pm init
```

### Import errors
Make sure all dependencies are installed:
```powershell
poetry install
# or
pip install -r requirements.txt
```
