# 飞书机器人配置检查清单

## 🔍 问题诊断

症状：长连接已建立，但收不到消息

## ✅ 必须检查的配置

### 1. 事件订阅配置

访问：https://open.feishu.cn/app/cli_a90b197f26b95cd4/event

**必须确认**：

#### 1.1 启用事件订阅
- [ ] 已开启"事件订阅"开关

#### 1.2 订阅方式（重要！）
- [ ] **必须选择**："使用长连接接收事件"
- [ ] ❌ 不要选择："通过 HTTP 推送接收事件"

#### 1.3 订阅事件
- [ ] 已勾选：`im.message.receive_v1`（接收消息）
- [ ] 点击了"保存"或"更新"按钮

### 2. 权限配置

访问：https://open.feishu.cn/app/cli_a90b197f26b95cd4/permission

**必须开通的权限**：
- [ ] `im:message` - 发送消息权限
- [ ] `im:message:send_as_bot` - 机器人发送权限
- [ ] 点击了"申请权限"或"开通权限"

### 3. 发布状态

访问：https://open.feishu.cn/app/cli_a90b197f26b95cd4

- [ ] 应用状态为"已启用"或"已发布"
- [ ] 如果是"开发中"状态，需要添加测试用户

### 4. 测试方法

#### 方法1：检查 SDK 日志

启动服务时应该看到：
```
[Lark] [INFO] connected to wss://...
```

**收到消息时应该看到**：
```
📩 收到消息: xxx
```

如果没有"收到消息"日志，说明事件没推送过来。

#### 方法2：手动触发测试

在飞书中给机器人发消息后，观察服务端是否有新日志输出。

## 🛠️ 调试步骤

### 步骤1：添加调试日志

在 `src/feishu/event_handler.py` 中的 `on_message_received` 函数开头添加：

```python
def on_message_received(data: lark.im.v1.P2ImMessageReceiveV1):
    """Handle received message event."""
    print(f"🔍 [DEBUG] Event received: {data}")  # 添加这行
    try:
        # ... 原有代码
```

### 步骤2：重新启动服务

```bash
pm serve
```

### 步骤3：发送测试消息

在飞书中发送任意消息给机器人。

### 步骤4：检查日志

- **如果看到** `🔍 [DEBUG] Event received: ...` 说明事件已到达，是处理逻辑问题
- **如果没有看到** 说明事件没有推送到客户端，是飞书配置问题

## 📋 常见配置错误

### 错误1：订阅方式选错了

❌ 错误：选择了"通过 HTTP 推送接收事件"
✅ 正确：选择"使用长连接接收事件"

### 错误2：事件未订阅

❌ 错误：只勾选了其他事件，没勾选 `im.message.receive_v1`
✅ 正确：必须勾选 `im.message.receive_v1`

### 错误3：权限未开通

❌ 错误：只添加了权限但没点击"申请权限"
✅ 正确：点击"申请权限"并等待审批（自建应用自动通过）

### 错误4：应用未发布

❌ 错误：应用处于"开发中"状态，且没有添加测试用户
✅ 正确：将应用改为"已发布"状态，或添加测试用户

### 错误5：机器人未在会话中

❌ 错误：在群聊中但机器人不在群里
✅ 正确：在飞书中找到机器人应用，直接发消息

## 🎯 快速验证方法

### 最简单的测试

1. 访问飞书开放平台事件订阅页面
2. 确认看到：**"使用长连接接收事件"**
3. 确认已勾选：`im.message.receive_v1`
4. 确认看到：**"已启用"**状态
5. 点击"保存"或"更新"
6. 重启 `pm serve`
7. 在飞书给机器人发消息

## 📞 如果还不行

检查飞书开放平台的"事件订阅"页面，确认：
- 页面顶部是否显示"已启用"
- 是否有错误提示（红色感叹号等）
- 是否选择了"使用长连接接收事件"

参考文档：
- https://open.feishu.cn/document/server-side-sdk/python--sdk/handle-events
- https://open.feishu.cn/document/common-capabilities/message-card/message-card-content
