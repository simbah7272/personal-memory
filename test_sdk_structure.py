"""测试 SDK 事件对象结构"""
import lark_oapi as lark
import json

APP_ID = "cli_a90b197f26b95cd4"
APP_SECRET = "0tfpk8749kMPTAIIV9WWKhRNBK2XVmZH"

def on_message_received(data):
    """检查事件对象的所有属性"""
    print("=" * 50, flush=True)
    print("[DEBUG] Event object structure:", flush=True)
    print(f"Type: {type(data)}", flush=True)
    print(f"Dir: {[attr for attr in dir(data) if not attr.startswith('_')]}", flush=True)

    # Try different access patterns
    print("\n--- Trying different access patterns ---", flush=True)

    # Pattern 1: data.sender
    try:
        print(f"data.sender exists: {hasattr(data, 'sender')}", flush=True)
        if hasattr(data, 'sender'):
            print(f"data.sender: {data.sender}", flush=True)
    except Exception as e:
        print(f"Error accessing data.sender: {e}", flush=True)

    # Pattern 2: data.event
    try:
        print(f"data.event exists: {hasattr(data, 'event')}", flush=True)
        if hasattr(data, 'event'):
            print(f"data.event: {data.event}", flush=True)
            if hasattr(data.event, 'sender'):
                print(f"data.event.sender: {data.event.sender}", flush=True)
    except Exception as e:
        print(f"Error accessing data.event: {e}", flush=True)

    # Pattern 3: Check for event_sender
    try:
        if hasattr(data, 'event_sender'):
            print(f"data.event_sender: {data.event_sender}", flush=True)
    except Exception as e:
        pass

    # Try to get message content
    try:
        if hasattr(data, 'message'):
            print(f"data.message: {data.message}", flush=True)
            print(f"data.message.content: {data.message.content}", flush=True)
        elif hasattr(data, 'event') and hasattr(data.event, 'message'):
            print(f"data.event.message: {data.event.message}", flush=True)
            print(f"data.event.message.content: {data.event.message.content}", flush=True)
    except Exception as e:
        print(f"Error accessing message: {e}", flush=True)

    print("=" * 50, flush=True)

# 创建事件处理器
event_handler = lark.EventDispatcherHandler.builder(
    APP_ID,
    APP_SECRET
).register_p2_im_message_receive_v1(on_message_received).build()

print("Starting...", flush=True)

client = lark.ws.Client(
    APP_ID,
    APP_SECRET,
    event_handler=event_handler,
    log_level=lark.LogLevel.INFO
)

try:
    client.start()
except KeyboardInterrupt:
    print("\nStopped")
