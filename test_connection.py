"""测试飞书长连接和事件接收"""
import lark_oapi as lark
import json
import sys

# 配置
APP_ID = "cli_a90b197f26b95cd4"
APP_SECRET = "0tfpk8749kMPTAIIV9WWKhRNBK2XVmZH"

def on_message_received(data):
    """处理接收到的消息"""
    # Force flush output
    sys.stdout.flush()

    print("=" * 50, flush=True)
    print("[OK] Event received!", flush=True)
    print(f"Event type: {type(data)}", flush=True)

    try:
        if hasattr(data, 'sender'):
            user_id = data.sender.sender_id.user_id
            open_id = data.sender.sender_id.open_id
            print(f"User ID: {user_id}", flush=True)
            print(f"Open ID: {open_id}", flush=True)

            # Use open_id if user_id is null
            sender_id = user_id or open_id
            print(f"Using sender_id: {sender_id}", flush=True)

        if hasattr(data, 'message'):
            content_str = data.message.content
            print(f"Message content: {content_str}", flush=True)

            content = json.loads(content_str)
            text = content.get("text", "")
            print(f"Text: {text}", flush=True)

            print("=" * 50, flush=True)
            print("[SUCCESS] Message processing complete!", flush=True)
            print(f"Extracted text: {text}", flush=True)
    except Exception as e:
        print(f"Error: {e}", flush=True)
        import traceback
        traceback.print_exc()

# 创建事件处理器
event_handler = lark.EventDispatcherHandler.builder(
    APP_ID,
    APP_SECRET
).register_p2_im_message_receive_v1(on_message_received).build()

print("[OK] Event handler created", flush=True)
print(f"APP_ID: {APP_ID}", flush=True)
print("Connecting to Feishu server...", flush=True)
print("Send a message to the bot now!", flush=True)
print("=" * 50, flush=True)
sys.stdout.flush()

# 创建 WebSocket 客户端
client = lark.ws.Client(
    APP_ID,
    APP_SECRET,
    event_handler=event_handler,
    log_level=lark.LogLevel.INFO  # Use INFO to reduce noise
)

# 启动连接
try:
    client.start()
except KeyboardInterrupt:
    print("\nDisconnected by user", flush=True)
