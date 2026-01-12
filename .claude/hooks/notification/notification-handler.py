#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Notification Handler - 通知处理Hook

功能:
- 接收 Claude Code 发送的通知
- 显示 Windows 桌面通知
- 播放提示音效
- 记录通知日志
"""

import sys
import os
import json
import logging
from datetime import datetime
from pathlib import Path

# 设置stdout编码为UTF-8 (Windows环境)
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 配置日志
LOG_DIR = Path("development/logs/notification-hook")
LOG_DIR.mkdir(parents=True, exist_ok=True)

# 创建日志文件处理器
file_handler = logging.FileHandler(LOG_DIR / f"notification-{datetime.now().strftime('%Y-%m-%d')}.log", encoding='utf-8')
file_handler.setLevel(logging.INFO)

# 创建控制台处理器，并确保使用UTF-8编码
console_handler = logging.StreamHandler(sys.stderr)
console_handler.setLevel(logging.INFO)

# 配置日志
logger = logging.getLogger("NotificationHook")
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)


def show_windows_notification(title, message, notification_type="info"):
    """显示 Windows 桌面通知"""
    try:
        from win10toast import ToastNotifier

        toaster = ToastNotifier()

        # 根据类型设置图标
        icon_path = None
        duration = 5

        if notification_type == "error":
            duration = 10
        elif notification_type == "warning":
            duration = 7

        # 显示通知
        toaster.show_toast(
            title=title,
            msg=message,
            icon_path=icon_path,
            duration=duration,
            threaded=True
        )

        logger.info(f"Windows notification shown: {title} - {message}")

    except ImportError:
        logger.warning("win10toast not installed, skipping desktop notification")
        logger.info(f"Notification: {title} - {message}")
    except Exception as e:
        logger.error(f"Failed to show Windows notification: {e}")


def play_notification_sound(notification_type="info"):
    """播放通知音效"""
    try:
        import winsound

        # 根据类型选择音效
        if notification_type == "error":
            # 错误: 手形图标
            winsound.MessageBeep(winsound.MB_ICONHAND)
        elif notification_type == "warning":
            # 警告: 感叹号
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        elif notification_type == "success":
            # 成功: 星号
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
        else:
            # 信息: 普通
            winsound.MessageBeep(winsound.MB_OK)

        logger.info(f"Sound played for notification type: {notification_type}")

    except Exception as e:
        logger.error(f"Failed to play notification sound: {e}")


def log_notification(notification_data):
    """记录通知到日志文件"""
    try:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": notification_data.get("type", "info"),
            "title": notification_data.get("title", ""),
            "message": notification_data.get("message", "")
        }

        # 写入JSON日志
        log_file = LOG_DIR / "notifications.jsonl"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

        logger.info(f"Notification logged: {log_entry}")

    except Exception as e:
        logger.error(f"Failed to log notification: {e}")


def parse_notification_input():
    """解析输入的通知数据"""
    try:
        # 从 stdin 读取 JSON 输入
        input_data = json.loads(sys.stdin.read())

        # 提取通知内容
        notification = input_data.get("notification", {})

        return {
            "type": notification.get("type", "info"),
            "title": notification.get("title", "Claude Code Notification"),
            "message": notification.get("message", ""),
            "metadata": input_data.get("metadata", {})
        }

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON input: {e}")
        return None
    except Exception as e:
        logger.error(f"Failed to parse notification input: {e}")
        return None


def main():
    """主函数"""
    try:
        # 解析输入
        notification_data = parse_notification_input()

        if not notification_data:
            return 1

        logger.info(f"Received notification: {notification_data['title']}")

        # 记录通知
        log_notification(notification_data)

        # 显示桌面通知
        show_windows_notification(
            title=notification_data["title"],
            message=notification_data["message"],
            notification_type=notification_data["type"]
        )

        # 播放音效
        play_notification_sound(notification_data["type"])

        # 返回成功结果
        output = {
            "hookSpecificOutput": {
                "notificationHandled": True,
                "timestamp": datetime.now().isoformat(),
                "type": notification_data["type"]
            }
        }

        print(json.dumps(output, ensure_ascii=False))
        return 0

    except Exception as e:
        logger.error(f"Notification handler error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
