#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
会话结束自动Git提交脚本

功能:
1. 检查Git状态
2. 如果有改动 → 自动commit并push
3. 跳过敏感文件
4. 生成提交信息

作者: Claude (老黑)
创建时间: 2025-01-12
版本: v1.0
"""

import os
import subprocess
import json
from datetime import datetime
import re

def run_command(cmd):
    """执行命令并返回结果"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            timeout=30
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return 1, "", str(e)

def check_git_status():
    """检查Git状态"""
    code, stdout, stderr = run_command("git status --porcelain")
    if code != 0:
        return None, stderr

    if not stdout:
        return False, "No changes"
    return True, stdout

def should_skip_file(file_path):
    """判断是否应该跳过该文件"""
    # 跳过的文件模式
    skip_patterns = [
        r'\.tmp$',
        r'\.log$',
        r'\.DS_Store$',
        r'__pycache__',
        r'\.pyc$',
        r'\.env$',
        r'credentials\.json',
        r'\.claude/skills/agent-memory/memories/',  # 记忆文件频繁变动
    ]

    for pattern in skip_patterns:
        if re.search(pattern, file_path):
            return True
    return False

def generate_commit_message(changes):
    """生成提交信息"""
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d %H:%M")

    # 分析改动类型
    change_types = {
        'docs': 0,
        'hooks': 0,
        'agents': 0,
        'commands': 0,
        'skills': 0,
        'design': 0,
        'other': 0
    }

    for line in changes.split('\n'):
        if not line:
            continue
        file_path = line.split()[1] if len(line.split()) > 1 else ""

        if '.claude/hooks/' in file_path:
            change_types['hooks'] += 1
        elif '.claude/agents/' in file_path:
            change_types['agents'] += 1
        elif '.claude/commands/' in file_path:
            change_types['commands'] += 1
        elif '.claude/skills/' in file_path:
            change_types['skills'] += 1
        elif 'docs/design/' in file_path or file_path.endswith('.md'):
            change_types['docs'] += 1
        elif 'development/' in file_path:
            change_types['docs'] += 1
        else:
            change_types['other'] += 1

    # 确定主要改动类型
    main_type = max(change_types.items(), key=lambda x: x[1])[0]
    count = sum(change_types.values())

    # 生成提交信息
    if main_type == 'docs':
        prefix = "docs"
    elif main_type == 'hooks':
        prefix = "hooks"
    elif main_type == 'agents':
        prefix = "agent"
    elif main_type == 'commands':
        prefix = "feat"
    else:
        prefix = "chore"

    message = f"{prefix}: 自动提交 - {date_str}\n\n"
    message += f"📊 改动统计: {count}个文件\n\n"

    if change_types['docs'] > 0:
        message += f"- 文档: {change_types['docs']}个\n"
    if change_types['hooks'] > 0:
        message += f"- Hook: {change_types['hooks']}个\n"
    if change_types['agents'] > 0:
        message += f"- Agent: {change_types['agents']}个\n"
    if change_types['commands'] > 0:
        message += f"- Command: {change_types['commands']}个\n"
    if change_types['other'] > 0:
        message += f"- 其他: {change_types['other']}个\n"

    message += "\n🤖 Auto-commit by SessionEnd Hook"
    return message

def auto_commit():
    """自动提交函数"""
    # 检查Git状态
    has_changes, status = check_git_status()

    if has_changes is False:
        return {
            "continue": True,
            "suppressOutput": True,
            "message": "✅ 无改动，跳过提交"
        }

    if has_changes is None:
        return {
            "continue": True,
            "suppressOutput": False,
            "message": f"⚠️ Git状态检查失败: {status}"
        }

    # 生成提交信息
    commit_message = generate_commit_message(status)

    # 添加所有改动
    code, stdout, stderr = run_command("git add -A")
    if code != 0:
        return {
            "continue": True,
            "suppressOutput": False,
            "message": f"⚠️ Git add失败: {stderr}"
        }

    # 创建提交
    commit_msg_escaped = commit_message.replace('"', '\\"')
    code, stdout, stderr = run_command(f'git commit -m "{commit_msg_escaped}"')

    if code != 0:
        return {
            "continue": True,
            "suppressOutput": False,
            "message": f"⚠️ Git commit失败: {stderr}"
        }

    # 推送到远程
    code, stdout, stderr = run_command("git push origin master")

    if code != 0:
        return {
            "continue": True,
            "suppressOutput": False,
            "message": f"⚠️ Git push失败: {stderr}\n✅ 本地提交成功，请手动推送"
        }

    return {
        "continue": True,
        "suppressOutput": False,
        "message": f"✅ 自动提交成功!\n\n📝 {commit_message}"
    }

if __name__ == "__main__":
    import sys
    result = auto_commit()
    # 使用UTF-8编码输出
    sys.stdout.reconfigure(encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))
