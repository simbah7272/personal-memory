# Personal Memory System

A lightweight personal data recording and management platform powered by AI natural language processing.

## Features

- 📝 **Natural Language Input**: Just describe what happened in plain language
- 🤖 **AI-Powered Parsing**: Automatically structures your data using AI
- 💰 **Finance Tracking**: Track income and expenses with automatic categorization
- 😴 **Health Monitoring**: Record sleep, mood, and wellness metrics
- 💼 **Work Logging**: Track tasks, hours, and achievements
- 🎮 **Leisure Activities**: Log free time activities and enjoyment levels
- 📊 **Reports**: Generate daily, weekly, and monthly summaries

## Installation

### Using Poetry (Recommended)

```bash
# Install dependencies
poetry install

# Create .env file from example
cp .env.example .env

# Edit .env with your configuration
# Important: Set AI_PROVIDER and AI_API_KEY
```

### Using pip

```bash
pip install -e .
```

## Configuration

Edit the `.env` file with your settings:

```bash
# AI Provider Configuration (choose one)
AI_PROVIDER=openai                    # Options: openai, anthropic
AI_API_KEY=your-api-key-here
AI_BASE_URL=https://api.openai.com/v1  # Optional: For proxy/relay services
AI_MODEL=gpt-4o-mini

# Or use Anthropic
# AI_PROVIDER=anthropic
# AI_API_KEY=sk-ant-your-key
# AI_MODEL=claude-haiku-4-20250205

# Database (default is fine for most users)
DATABASE_URL=sqlite:///data/database.db
```

## Quick Start

### 1. Initialize the database

```bash
pm init
```

### 2. Add your first records

```bash
# Finance
pm finance add "今天花了50块买午饭"

# Health
pm health add "昨晚睡了8小时，睡得很好"

# Work
pm work add "今天工作8小时，完成了用户认证模块"

# Leisure
pm leisure add "看了2小时电影"
```

### 3. View reports

```bash
pm report daily
pm report weekly
pm report monthly
```

## Commands

### Finance Commands

```bash
# Add a finance record
pm finance add "今天花了50块买午饭"

# List recent records
pm finance list --days 7

# Show statistics by category
pm finance stats
```

### Health Commands

```bash
# Add a health record
pm health add "昨晚睡了8小时，睡得很好"

# List recent records
pm health list --days 7
```

### Work Commands

```bash
# Add a work record
pm work add "今天工作8小时，完成了用户认证模块"

# List recent records
pm work list --days 7

# Show summary
pm work summary --days 30
```

### Leisure Commands

```bash
# Add a leisure record
pm leisure add "看了2小时电影"

# List recent records
pm leisure list --days 7
```

### Report Commands

```bash
# Daily report
pm report daily

# Weekly report
pm report weekly

# Monthly report
pm report monthly

# Report for a specific date
pm report daily 2025-01-15
```

## Natural Language Examples

### Finance

- "今天花了50块买午饭"
- "地铁8块钱"
- "发了10000块工资"
- "超市买菜花了200元"

### Health

- "昨晚睡了8小时，睡得很好"
- "11点睡，7点起，睡眠质量一般"
- "今天心情不错"
- "睡了6个小时，很差"

### Work

- "今天工作8小时，完成了用户认证模块"
- "开了2个小时会，讨论了产品方案"
- "修复了3个bug"
- "写了文档，大概3小时"

### Leisure

- "看了2小时电影"
- "和朋友打了3小时桌球，很开心"
- "逛了1小时公园"
- "玩了一下午游戏"

## AI Provider Support

The system supports multiple AI providers:

### OpenAI (Default)

```bash
AI_PROVIDER=openai
AI_API_KEY=sk-your-key
AI_MODEL=gpt-4o-mini
```

### Anthropic Claude

```bash
AI_PROVIDER=anthropic
AI_API_KEY=sk-ant-your-key
AI_MODEL=claude-haiku-4-20250205
```

### Custom/Proxy Services

You can use custom base URLs for proxy or relay services:

```bash
AI_PROVIDER=openai
AI_API_KEY=your-custom-key
AI_BASE_URL=https://your-proxy.com/v1
AI_MODEL=gpt-4o-mini
```

## Project Structure

```
personal-memory/
├── src/
│   ├── main.py              # CLI entry point
│   ├── config.py            # Configuration management
│   ├── core/
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── schemas.py       # Pydantic schemas
│   │   ├── database.py      # Database connection
│   │   └── exceptions.py    # Custom exceptions
│   ├── services/
│   │   └── record_service.py # Business logic
│   ├── repositories/        # Data access layer
│   ├── cli/                 # CLI commands
│   ├── ai/
│   │   ├── parser.py        # Text parser
│   │   └── providers.py     # AI provider abstraction
│   └── utils/               # Utilities
├── prompts/                 # AI prompt templates
├── data/                    # Database storage
└── tests/                   # Tests
```

## Development

### Running Tests

```bash
poetry run pytest
```

### Code Formatting

```bash
poetry run black src/
poetry run ruff check src/
```

## License

MIT License - feel free to use this project for personal use.
