#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PermissionRequest Hook - 智能权限控制器
自动批准安全的工具调用,减少用户确认次数
"""

import json
import sys
import re
from pathlib import Path

# 设置stdout编码为UTF-8
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def is_safe_file_operation(file_path, tool_name):
    """判断文件操作是否安全"""

    # 只读操作通常是安全的
    if tool_name in ['Read', 'Glob', 'Grep']:
        return True, "只读操作,安全"

    # 写入操作需要检查文件路径
    if tool_name in ['Write', 'Edit']:
        # 危险文件列表
        dangerous_patterns = [
            '.env',
            '.git',
            'node_modules/',
            '__pycache__/',
            '.pyc',
            'package-lock.json',
            'yarn.lock',
            '.claude/settings',  # 保护Hook配置
            'settings.json',
        ]

        for pattern in dangerous_patterns:
            if pattern in file_path:
                return False, f"包含保护路径: {pattern}"

        # 项目内的文件通常是安全的
        # 检查是否在项目目录下
        if any(safe_dir in file_path for safe_dir in [
            'development/',
            'docs/',
            '.claude/agents/',
            '.claude/commands/',
            '.claude/guide/',
            '.claude/skills/',
            '.claude/hooks/',
            '.claude/templates/',
            '.claude/prompts/',
            '.claude/workflows/',
        ]):
            return True, "项目文件,安全"

        return False, "需要确认的路径"

    return False, "未知操作类型"

def is_safe_bash_command(command):
    """判断Bash命令是否安全"""

    # 安全的只读命令
    safe_read_commands = [
        r'^\s*ls\s+',           # 列出文件
        r'^\s*cat\s+',          # 查看文件
        r'^\s*head\s+',         # 查看文件开头
        r'^\s*tail\s+',         # 查看文件结尾
        r'^\s*grep\s+',         # 搜索内容
        r'^\s*find\s+.+-name\s+',  # 查找文件
        r'^\s*wc\s+-l\s+',      # 统计行数
        r'^\s*pwd\s+',          # 显示当前目录
        r'^\s*echo\s+',         # 输出文本
        r'^\s*python\s+-c\s+"', # Python单行代码
        r'^\s*git\s+(status|log|diff|branch|show)',  # Git只读命令
    ]

    for pattern in safe_read_commands:
        if re.match(pattern, command):
            return True, "安全只读命令"

    # 危险命令
    dangerous_commands = [
        r'\brm\s+-rf\s+',       # 强制删除
        r'\bdd\s+',             # 删除磁盘
        r'\bmkfs\.',            # 格式化
        r'\bchmod\s+777',       # 过度开放权限
        r'>\s*/dev/',           # 直接写设备
        r':\(\)\{\s*:\|:\s*&\}\s*:',  # Fork炸弹
    ]

    for pattern in dangerous_commands:
        if re.search(pattern, command):
            return False, f"危险命令: {pattern}"

    # Git写命令 - 需要确认但通常可以允许
    if re.match(r'^\s*git\s+(commit|push|pull|add)', command):
        return True, "Git操作(可允许)"

    # NPM/Python包操作 - 需要确认
    if re.match(r'^\s*(npm|pip|python)\s+(install|uninstall)', command):
        return True, "包管理操作(可允许)"

    # 文件编辑 - 检查路径
    if re.match(r'^\s*(sed|awk|python)', command):
        return None, "需要检查路径"

    return None, "需要人工判断"

def get_permission_decision(tool_name, tool_input):
    """获取权限决策"""

    # 1. 只读工具 - 自动批准
    if tool_name in ['Read', 'Glob', 'Grep', 'WebFetch', 'WebSearch']:
        return {
            "decision": {
                "behavior": "allow",
                "reason": f"{tool_name}是只读操作,自动批准"
            }
        }

    # 2. 文件写入操作 - 检查路径
    if tool_name in ['Write', 'Edit']:
        file_path = tool_input.get('file_path', '')

        safe, reason = is_safe_file_operation(file_path, tool_name)

        if safe:
            return {
                "decision": {
                    "behavior": "allow",
                    "reason": reason
                }
            }
        elif safe is False:
            return {
                "decision": {
                    "behavior": "deny",
                    "message": f"危险操作被阻止: {reason}"
                }
            }
        else:
            return None  # 需要询问用户

    # 3. Bash命令 - 智能判断
    if tool_name == 'Bash':
        command = tool_input.get('command', '')

        safe, reason = is_safe_bash_command(command)

        if safe:
            return {
                "decision": {
                    "behavior": "allow",
                    "reason": reason
                }
            }
        elif safe is False:
            return {
                "decision": {
                    "behavior": "deny",
                    "message": f"危险命令被阻止: {reason}"
                }
            }
        else:
            return None  # 需要询问用户

    # 4. Task工具 - 检查子agent类型
    if tool_name == 'Task':
        # Task工具用于启动子agent,通常可以允许
        return {
            "decision": {
                "behavior": "allow",
                "reason": "Task工具用于子agent,自动批准"
            }
        }

    # 5. 其他工具 - 默认询问
    return None

def main():
    """主函数"""

    try:
        # 读取stdin
        input_data = json.load(sys.stdin)

        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})

        # 调试日志
        print(f"[PermissionRequest Hook] Called with tool_name={tool_name}, input={tool_input}", file=sys.stderr)

        if not tool_name:
            sys.exit(0)

        # 获取权限决策
        decision = get_permission_decision(tool_name, tool_input)

        if decision is None:
            # 没有自动决策,让用户确认
            sys.exit(0)

        # 输出决策
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PermissionRequest",
                "decision": decision["decision"]
            }
        }

        print(json.dumps(output, ensure_ascii=False, indent=2))

        # 记录到stderr (调试用)
        decision_type = decision["decision"]["behavior"]
        reason = decision["decision"].get("reason", decision["decision"].get("message", ""))
        print(f"🤖 PermissionRequest: {tool_name} → {decision_type} ({reason})", file=sys.stderr)

        sys.exit(0)

    except Exception as e:
        # 出错时不影响正常流程
        print(f"❌ Smart permission controller error: {e}", file=sys.stderr)
        sys.exit(0)

if __name__ == "__main__":
    main()
