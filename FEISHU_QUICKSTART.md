# Feishu Bot - Quick Start Guide (SDK Long-Connection Mode)

Get started with Personal Memory Feishu bot in **3 minutes**!

**Big News**: No public URL needed! Works locally with SDK long-connection mode.

## Prerequisites

✅ Personal Memory installed (`pip install personal-memory`)
✅ AI API configured (OpenAI or Anthropic)
✅ Feishu account (enterprise/organization)

## Step 1: Create Feishu App (2 min)

1. Visit https://open.feishu.cn/app
2. Click "创建企业自建应用"
3. Name it "Personal Memory"
4. Copy **App ID** and **App Secret**

## Step 2: Configure Permissions (1 min)

In your Feishu app:

1. **Add capability**: "机器人" (Bot)
2. **Add permissions**:
   - `im:message`
   - `im:message:send_as_bot`
3. **Configure event subscription**:
   - Choose **"使用长连接接收事件"** (Use long-connection)
   - Subscribe to: `im.message.receive_v1`

**No URL needed!** That's the beauty of long-connection mode.

## Step 3: Set Environment Variables (30 sec)

Add to your `.env` file:

```bash
# AI Provider (required)
AI_PROVIDER=openai
AI_API_KEY=your_api_key_here

# Feishu Bot (required)
FEISHU_APP_ID=cli_xxxxxxxxxxxxx
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxx
```

## Step 4: Start Service (10 sec)

```bash
# Initialize database (first time only)
pm init

# Start the bot
pm serve
```

You'll see:

```
🚀 启动飞书机器人服务...
  App ID: cli_xxxxxxxxxxxxx
  Database: sqlite:///data/database.db

提示: 服务运行中，按 Ctrl+C 停止

✅ 飞书长连接已建立
📩 等待消息... (按 Ctrl+C 停止)
```

## Step 5: Test! (10 sec)

Find your bot in Feishu and send:

```
hello
```

You should receive a help message! 🎉

## Common Commands

### Add Records

```
今天花了50块买午饭
昨晚睡了8小时
今天工作了4小时
看了2小时电影
```

### Query Data

```
查询本周花费
看看今天的工作记录
上个月在餐饮上花了多少钱
昨天睡了多少小时
```

### Quick Commands

```
/daily   - Today's report
/weekly  - Weekly report
/help    - Help message
```

## Troubleshooting

### Connection fails?

- Check `FEISHU_APP_ID` and `FEISHU_APP_SECRET` in `.env`
- Run `poetry install` to ensure `lark-oapi` is installed
- Check your network connection

### Bot doesn't respond?

- Check AI_API_KEY in `.env`
- Verify permissions are enabled in Feishu app
- Check terminal logs for errors
- Make sure event subscription is enabled

### Need more help?

See [FEISHU_SETUP.md](FEISHU_SETUP.md) for detailed guide

## Why Long-Connection Mode?

| Feature | Webhook Mode | Long-Connection Mode |
|---------|-------------|---------------------|
| Public URL | ❌ Required | ✅ Not needed |
| Local Dev | ❌ Needs ngrok | ✅ Works directly |
| Setup Time | ~10 minutes | ~3 minutes |
| Auto Reconnect | ❌ No | ✅ Yes |

## Tips

💡 **No More ngrok**: Long-connection mode works without public URLs
💡 **Auto Reconnect**: SDK automatically reconnects if network drops
💡 **Production Ready**: Use systemd/supervisor for process management
💡 **Docker Friendly**: Check [FEISHU_SETUP.md](FEISHU_SETUP.md) for Docker setup

## What's Next?

- Customize your AI prompts in `prompts/`
- Add custom commands in `src/feishu/handlers.py`
- Set up automated reminders
- Integrate with other services

Happy tracking! 🎉
