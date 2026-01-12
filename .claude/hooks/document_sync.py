#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PostToolUse Hook - 文档修改自动同步和提醒
当检测到重要文档变更时,自动提醒并同步相关文档
"""

import json
import sys
import os
from pathlib import Path

# 设置stdout编码为UTF-8,避免Windows环境下的编码错误
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def read_hook_input():
    """从stdin读取Hook输入数据"""
    try:
        input_data = json.load(sys.stdin)
        return input_data
    except json.JSONDecodeError as e:
        print(f"❌ Hook输入解析错误: {e}", file=sys.stderr)
        sys.exit(1)

def get_file_path(tool_input, tool_response):
    """从工具输入/响应中提取文件路径"""
    # Write工具
    if isinstance(tool_input, dict):
        file_path = tool_input.get("file_path", "")
        if file_path:
            return file_path

    # Edit工具
    if isinstance(tool_input, dict):
        file_path = tool_input.get("file_path", "")
        if file_path:
            return file_path

    # 从响应中获取
    if isinstance(tool_response, dict):
        file_path = tool_response.get("filePath", "")
        if file_path:
            return file_path

    return ""

def is_significant_change(file_path, tool_name):
    """判断是否为重要变更"""
    significant_patterns = [
        "CHANGELOG.md",
        "claude.md",
        "/design/",
        "/issues/",
        ".claude/skills/",
        ".claude/agents/",
        ".claude/commands/",
        ".claude/hooks/",
    ]

    for pattern in significant_patterns:
        if pattern in file_path:
            return True

    return False

def analyze_change_type(file_path):
    """分析变更类型"""
    if "CHANGELOG.md" in file_path:
        return "版本号变更"
    elif "claude.md" in file_path:
        return "项目配置更新"
    elif "/design/" in file_path:
        return "设计文档修改"
    elif "/issues/" in file_path:
        return "问题清单更新"
    elif ".claude/skills/" in file_path:
        return "Skill工具修改"
    elif ".claude/agents/" in file_path:
        return "Agent工具修改"
    elif ".claude/commands/" in file_path:
        return "Command工具修改"
    elif ".claude/hooks/" in file_path:
        return "Hook配置修改"
    else:
        return "其他文档修改"

def get_sync_recommendation(file_path):
    """获取同步建议"""
    if "CHANGELOG.md" in file_path:
        return "立即更新claude.md版本号"
    elif "claude.md" in file_path:
        return "检查CHANGELOG是否需要更新"
    elif "/design/" in file_path:
        return "同步更新问题清单和开发日志"
    elif ".claude/" in file_path:
        return "运行/sync-docs同步文档"
    else:
        return "无"

def main():
    """主函数"""
    # 读取Hook输入
    input_data = read_hook_input()

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})
    tool_response = input_data.get("tool_response", {})

    # 提取文件路径
    file_path = get_file_path(tool_input, tool_response)

    if not file_path:
        # 不是文件操作,静默退出
        output = {
            "continue": True,
            "suppressOutput": True
        }
        print(json.dumps(output))
        sys.exit(0)

    # 检查是否为重要变更
    if not is_significant_change(file_path, tool_name):
        # 小改动,不输出
        output = {
            "continue": True,
            "suppressOutput": True
        }
        print(json.dumps(output))
        sys.exit(0)

    # 分析变更
    change_type = analyze_change_type(file_path)
    sync_recommendation = get_sync_recommendation(file_path)
    filename = os.path.basename(file_path)

    # 构建系统消息
    system_message = f"""📋 文档变更提醒

📁 文件: {filename}
📂 路径: {file_path}
🔧 操作: {tool_name}
📝 类型: {change_type}"""

    if sync_recommendation != "无":
        system_message += f"\n💡 建议: {sync_recommendation}"

    # 输出标准JSON格式
    output = {
        "continue": True,
        "suppressOutput": False,
        "systemMessage": system_message
    }
    print(json.dumps(output))

    sys.exit(0)

if __name__ == "__main__":
    main()
