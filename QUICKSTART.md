# Quick Start Guide

## 5-Minute Setup

### Step 1: Install Dependencies

**With Poetry (Recommended):**
```bash
poetry install
```

**With pip:**
```bash
pip install -r requirements.txt
```

### Step 2: Configure AI Provider

Copy example environment file:
```bash
# Windows PowerShell
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Edit `.env` and set your AI provider:

**Option A: OpenAI**
```env
AI_PROVIDER=openai
AI_API_KEY=sk-your-openai-key-here
AI_MODEL=gpt-4o-mini
```

**Option B: Anthropic**
```env
AI_PROVIDER=anthropic
AI_API_KEY=sk-ant-your-key-here
AI_MODEL=claude-haiku-4-20250205
```

**Option C: Custom/Proxy**
```env
AI_PROVIDER=openai
AI_API_KEY=your-custom-key
AI_BASE_URL=https://your-proxy.com/v1
AI_MODEL=gpt-4o-mini
```

### Step 3: Initialize Database

```bash
# With Poetry
poetry run pm init

# With pip/python
python -m src.main init
```

### Step 4: Add Your First Records

```bash
# With Poetry
poetry run pm finance add "今天花了50块买午饭"
poetry run pm health add "昨晚睡了8小时，睡得很好"
poetry run pm work add "今天工作8小时，完成了用户认证模块"
poetry run pm leisure add "看了2小时电影"

# With pip/python
python -m src.main finance add "今天花了50块买午饭"
python -m src.main health add "昨晚睡了8小时，睡得很好"
python -m src.main work add "今天工作8小时，完成了用户认证模块"
python -m src.main leisure add "看了2小时电影"
```

### Step 5: View Reports

```bash
pm report daily
pm finance list --days 7
pm work summary
```

## Command Reference

### All Commands

```bash
pm                    # Show help
pm init              # Initialize database
pm version           # Show version

# Finance
pm finance add "<text>"           # Add record
pm finance list [--days N]        # List records
pm finance stats [--days N]       # Show statistics

# Health
pm health add "<text>"            # Add record
pm health list [--days N]         # List records

# Work
pm work add "<text>"              # Add record
pm work list [--days N]           # List records
pm work summary [--days N]        # Show summary

# Leisure
pm leisure add "<text>"           # Add record
pm leisure list [--days N]        # List records

# Reports
pm report daily [YYYY-MM-DD]      # Daily report
pm report weekly                  # Weekly report
pm report monthly                 # Monthly report
```

## Natural Language Examples

### Finance

| Input | Parsed As |
|-------|-----------|
| "今天花了50块买午饭" | 💸 ¥50 餐饮 |
| "地铁8块钱" | 💸 ¥8 交通 |
| "发了10000块工资" | 💰 ¥10000 工资 |
| "超市买菜花了200元" | 💸 ¥200 购物 |

### Health

| Input | Parsed As |
|-------|-----------|
| "昨晚睡了8小时，睡得很好" | 😴 8h, 很好 |
| "11点睡，7点起，睡眠质量一般" | 😴 8h, 一般 |
| "今天心情不错" | 😊 好 |
| "只睡了5个小时，很差" | 😴 5h, 很差 |

### Work

| Input | Parsed As |
|-------|-----------|
| "今天工作8小时，完成了用户认证模块" | 💼 8h, 用户认证模块 |
| "开了2个小时会，讨论了产品方案" | 💼 2h, 会议 |
| "修复了3个bug" | 💼 ~2h, bug修复 |
| "写了文档，大概3小时" | 💼 3h, 文档 |

### Leisure

| Input | Parsed As |
|-------|-----------|
| "看了2小时电影" | 🎮 电影, 2h |
| "和朋友打了3小时桌球，很开心" | 🎮 桌球, 3h, ⭐⭐⭐⭐⭐ |
| "逛了1小时公园" | 🎮 逛公园, 1h |
| "玩了一下午游戏" | 🎮 游戏, ~4h |

## Troubleshooting

### "Module not found" error

Make sure you're in the project directory:
```bash
cd D:\tool\personal-memory
```

### "AI API error"

Check your `.env` file:
- Is `AI_API_KEY` set correctly?
- Is `AI_PROVIDER` valid (openai or anthropic)?
- For OpenAI, can you reach `AI_BASE_URL`?

### Database errors

Re-initialize the database:
```bash
pm init
```

### Can't run `pm` command directly

Use the full command:
```bash
# Instead of: pm finance add "..."
# Use:
poetry run pm finance add "..."
# OR
python -m src.main finance add "..."
```

## Tips

1. **Daily routine**: Set a reminder to log your activities each day
2. **Be specific**: More details = better AI parsing
3. **Use categories**: The AI learns from your input patterns
4. **Check reports**: Review weekly/monthly reports for insights
5. **Backup**: Your data is in `data/database.db` - back it up regularly!

## Getting Help

- Check `README.md` for full documentation
- See `SETUP.md` for detailed installation guide
- Review `IMPLEMENTATION.md` for architecture details
- Open an issue on GitHub if you encounter bugs
