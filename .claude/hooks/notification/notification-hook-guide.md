# Notification Hook 集成指南

**创建时间**: 2025-01-12
**版本**: v1.0
**状态**: ✅ 已配置

---

## 功能概述

Notification Hook 会在 Claude Code 发送通知时触发，提供以下功能：

### 1. Windows 桌面通知
- 使用 `win10toast` 库显示系统通知
- 支持不同类型的通知（info, warning, error, success）
- 可配置显示时长

### 2. 音效提示
- 使用 Windows API 播放系统音效
- 根据通知类型播放不同音效：
  - **error**: 手形图标音效
  - **warning**: 感叹号音效
  - **success**: 星号音效
  - **info**: 普通音效

### 3. 通知日志
- 记录所有通知到日志文件
- JSON Lines 格式，便于分析
- 按日期自动分割日志

---

## 配置文件

### settings.json

```json
"Notification": [
  {
    "matcher": "*",
    "hooks": [
      {
        "type": "command",
        "command": "python d:/Claude/.claude/hooks/notification/notification-handler.py",
        "timeout": 30
      }
    ]
  }
]
```

**配置说明**:
- `matcher: "*"` - 匹配所有通知
- `type: "command"` - 执行 Python 脚本
- `timeout: 30` - 超时时间 30 秒

---

## 脚本位置

```
.claude/hooks/notification/
├── notification-handler.py       # 主处理脚本
└── notification-hook-guide.md    # 本文档
```

---

## 输入格式

Hook 会接收 JSON 输入（通过 stdin）：

```json
{
  "notification": {
    "type": "info|warning|error|success",
    "title": "通知标题",
    "message": "通知内容"
  },
  "metadata": {
    "source": "optional metadata"
  }
}
```

**字段说明**:
- `type`: 通知类型，影响音效和显示时长
- `title`: 通知标题
- `message`: 通知正文
- `metadata`: 可选的元数据

---

## 输出格式

Hook 返回 JSON 输出：

```json
{
  "hookSpecificOutput": {
    "notificationHandled": true,
    "timestamp": "2025-01-12T14:30:22",
    "type": "info"
  }
}
```

---

## 日志文件

### 控制台日志

```
development/logs/notification-hook/
└── notification-2025-01-12.log
```

**格式**:
```
2025-01-12 14:30:22 - NotificationHook - INFO - Received notification: Task Completed
2025-01-12 14:30:22 - NotificationHook - INFO - Windows notification shown: Task Completed - All tasks completed successfully
2025-01-12 14:30:22 - NotificationHook - INFO - Sound played for notification type: success
```

### 通知记录

```
development/logs/notification-hook/
└── notifications.jsonl
```

**格式** (JSON Lines):
```json
{"timestamp": "2025-01-12T14:30:22", "type": "success", "title": "Task Completed", "message": "All tasks completed successfully"}
{"timestamp": "2025-01-12T14:35:08", "type": "warning", "title": "Warning", "message": "Token usage is high"}
{"timestamp": "2025-01-12T14:40:15", "type": "error", "title": "Error", "message": "Failed to connect to server"}
```

---

## 依赖项

### Python 库

```bash
pip install win10toast
```

### 系统要求

- Windows 10/11
- Python 3.7+
- 启用了 Windows 通知功能

---

## 测试方法

### 手动测试

```bash
echo '{"notification":{"type":"success","title":"测试通知","message":"这是一个测试通知"}}' | python .claude/hooks/notification/notification-handler.py
```

**预期输出**:
1. 显示 Windows 桌面通知
2. 播放成功音效
3. 写入日志文件
4. 返回 JSON 结果

### 测试不同类型

```bash
# Info 通知
echo '{"notification":{"type":"info","title":"信息","message":"这是一条信息"}}' | python .claude/hooks/notification/notification-handler.py

# Warning 通知
echo '{"notification":{"type":"warning","title":"警告","message":"这是一条警告"}}' | python .claude/hooks/notification/notification-handler.py

# Error 通知
echo '{"notification":{"type":"error","title":"错误","message":"这是一条错误"}}' | python .claude/hooks/notification/notification-handler.py
```

---

## 功能特性

### 1. 智能音效

根据通知类型自动选择音效：

```python
if notification_type == "error":
    winsound.MessageBeep(winsound.MB_ICONHAND)      # 错误音效
elif notification_type == "warning":
    winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)  # 警告音效
elif notification_type == "success":
    winsound.MessageBeep(winsound.MB_ICONASTERISK)  # 成功音效
else:
    winsound.MessageBeep(winsound.MB_OK)            # 普通音效
```

### 2. 可配置显示时长

```python
duration = 5   # info: 5秒
duration = 7   # warning: 7秒
duration = 10  # error: 10秒
```

### 3. 自动日志归档

- 按日期分割日志文件
- JSON Lines 格式便于分析
- 包含完整的时间戳和元数据

---

## 故障排除

### 问题 1: 通知未显示

**可能原因**:
- `win10toast` 未安装
- Windows 通知功能被禁用
- 通知被系统屏蔽

**解决方法**:
```bash
pip install win10toast
```

检查 Windows 设置 → 系统 → 通知和操作 → 启用通知

### 问题 2: 音效未播放

**可能原因**:
- 系统音量静音
- 音效设备不可用
- `winsound` API 调用失败

**解决方法**:
- 检查系统音量
- 检查音频设备
- 查看日志文件中的错误信息

### 问题 3: 日志未写入

**可能原因**:
- 日志目录权限不足
- 磁盘空间不足

**解决方法**:
- 检查 `development/logs/notification-hook/` 目录权限
- 检查磁盘空间
- 手动创建日志目录

---

## 与其他 Hook 的配合

### 与 PostToolUse Hook 配合

```yaml
PostToolUse:
  - 执行操作后检查结果
  - 如果发现错误 → 发送 error 通知
  - 如果完成任务 → 发送 success 通知
```

### 与 SessionEnd Hook 配合

```yaml
SessionEnd:
  - 会话结束时自动提交
  - 发送 success 通知: "代码已提交到 GitHub"
```

### 与 PreToolUse Hook 配合

```yaml
PreToolUse:
  - 检查危险操作
  - 如果被阻止 → 发送 warning 通知
```

---

## 扩展功能

### 1. 自定义图标

修改 `show_windows_notification()` 函数：

```python
icon_path = "path/to/your/icon.ico"
toaster.show_toast(
    title=title,
    msg=message,
    icon_path=icon_path,
    duration=duration
)
```

### 2. 集成第三方通知服务

例如集成 Telegram、Slack、企业微信等：

```python
def send_telegram_notification(title, message):
    """发送 Telegram 通知"""
    import requests

    bot_token = "YOUR_BOT_TOKEN"
    chat_id = "YOUR_CHAT_ID"

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": f"{title}\n\n{message}"
    }

    requests.post(url, json=data)
```

### 3. 通知历史记录

创建一个简单的 HTML 页面查看通知历史：

```python
def generate_notification_history():
    """生成通知历史 HTML"""
    with open("development/logs/notification-hook/notifications.jsonl") as f:
        notifications = [json.loads(line) for line in f]

    # 按时间倒序
    notifications.reverse()

    # 生成 HTML
    html = "<html><head><title>Notification History</title></head><body>"
    html += "<h1>Notification History</h1>"
    html += "<table border='1'><tr><th>Time</th><th>Type</th><th>Title</th><th>Message</th></tr>"

    for notif in notifications:
        html += f"<tr><td>{notif['timestamp']}</td>"
        html += f"<td>{notif['type']}</td>"
        html += f"<td>{notif['title']}</td>"
        html += f"<td>{notif['message']}</td></tr>"

    html += "</table></body></html>"

    return html
```

---

## 性能优化

### 1. 异步通知

使用 `threaded=True` 参数，避免阻塞主线程：

```python
toaster.show_toast(
    title=title,
    msg=message,
    duration=duration,
    threaded=True  # 异步显示
)
```

### 2. 音效缓存

如果频繁播放音效，可以预先加载音效文件：

```python
import pygame

pygame.mixer.init()
sound_cache = {
    "error": pygame.mixer.Sound("error.wav"),
    "warning": pygame.mixer.Sound("warning.wav"),
    "success": pygame.mixer.Sound("success.wav"),
    "info": pygame.mixer.Sound("info.wav")
}

def play_notification_sound(notification_type):
    sound_cache[notification_type].play()
```

### 3. 日志批量写入

如果通知非常频繁，可以批量写入日志：

```python
log_buffer = []
BUFFER_SIZE = 10

def log_notification(notification_data):
    log_buffer.append(notification_data)

    if len(log_buffer) >= BUFFER_SIZE:
        flush_log_buffer()

def flush_log_buffer():
    with open(log_file, "a", encoding="utf-8") as f:
        for entry in log_buffer:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    log_buffer.clear()
```

---

## 安全考虑

### 1. 输入验证

```python
def validate_notification(notification_data):
    """验证通知数据"""
    required_fields = ["type", "title", "message"]

    for field in required_fields:
        if field not in notification_data:
            raise ValueError(f"Missing required field: {field}")

    # 验证类型
    valid_types = ["info", "warning", "error", "success"]
    if notification_data["type"] not in valid_types:
        raise ValueError(f"Invalid notification type: {notification_data['type']}")

    # 限制长度
    if len(notification_data["title"]) > 200:
        raise ValueError("Title too long")

    if len(notification_data["message"]) > 1000:
        raise ValueError("Message too long")
```

### 2. 路径安全

确保日志目录在项目范围内：

```python
PROJECT_ROOT = Path("d:/Claude")
LOG_DIR = PROJECT_ROOT / "development/logs/notification-hook"

# 防止路径遍历攻击
if not str(LOG_DIR).startswith(str(PROJECT_ROOT)):
    raise ValueError("Invalid log directory path")
```

---

## 总结

Notification Hook 提供了一个完整的通知系统，包括：

✅ **桌面通知**: Windows 系统通知
✅ **音效提示**: 根据类型播放不同音效
✅ **日志记录**: 完整的通知历史
✅ **易于扩展**: 支持自定义图标、第三方服务
✅ **性能优化**: 异步显示、批量写入
✅ **安全考虑**: 输入验证、路径安全

**下一步建议**:
1. 安装 `win10toast` 库
2. 测试通知功能
3. 根据需求自定义音效和图标
4. 考虑集成第三方通知服务（如 Telegram）

---

**创建时间**: 2025-01-12
**版本**: v1.0
**作者**: 老黑 (Claude)
**状态**: ✅ 已配置并测试
