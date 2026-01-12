#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart Permission Guard - 智能权限控制Hook

功能:
- 自动允许安全操作（减少打扰）
- 拦截真正的危险操作
- 使用 exit code 2 阻止操作
"""

import sys
import os
import json
import logging
from pathlib import Path

# 设置stdout编码为UTF-8 (Windows环境)
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def get_log_date():
    """获取日志日期"""
    from datetime import datetime
    return datetime.now().strftime('%Y-%m-%d')


# 配置日志
LOG_DIR = Path("development/logs/permission-guard")
LOG_DIR.mkdir(parents=True, exist_ok=True)

file_handler = logging.FileHandler(LOG_DIR / f"permission-guard-{get_log_date()}.log", encoding='utf-8')
file_handler.setLevel(logging.INFO)

console_handler = logging.StreamHandler(sys.stderr)
console_handler.setLevel(logging.INFO)

logger = logging.getLogger("PermissionGuard")
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)


def is_safe_operation(tool_name, tool_input):
    """
    判断操作是否安全

    返回: (is_safe, reason)
    """

    # ========== 1. 只读工具 - 自动允许 ==========
    if tool_name in ['Read', 'Glob', 'Grep', 'WebFetch', 'WebSearch']:
        return True, f"{tool_name} 是只读操作"

    # ========== 2. AskUserQuestion - 自动允许 ==========
    if tool_name == 'AskUserQuestion':
        return True, "AskUserQuestion 是交互工具"

    # ========== 3. Bash 命令检查 ==========
    if tool_name == 'Bash':
        command = tool_input.get('command', '')

        # 安全命令列表
        safe_commands = [
            'git ', 'npm ', 'pip ', 'python ', 'node ', 'pytest ',
            'ls ', 'dir ', 'cd ', 'pwd ', 'echo ',
            'cat ', 'head ', 'tail ', 'grep ', 'find ',
            'mkdir ', 'touch ', 'cp ', 'mv ',
            'eslint ', 'prettier ', 'tsc ',
            'yarn ', 'pnpm ', 'bun '
        ]

        # 危险命令列表
        dangerous_patterns = [
            'rm -rf', 'rmdir /s', 'del /s',  # 删除命令
            'drop ', 'delete ', 'truncate ',  # 数据库危险操作
            'git push --force', 'git push -f',  # 强制推送
            '> /dev/', 'sudo ', 'su ',  # 系统危险操作
            'format ', 'diskpart ', 'fdisk '  # 磁盘操作
        ]

        # 检查是否匹配危险模式
        for pattern in dangerous_patterns:
            if pattern in command.lower():
                return False, f"检测到危险命令: {pattern}"

        # 检查是否匹配安全命令
        for safe_cmd in safe_commands:
            if command.startswith(safe_cmd):
                return True, f"安全命令: {safe_cmd.strip()}"

        # 默认：Bash 命令需要确认（除非明确安全）
        logger.warning(f"Bash 命令需要确认: {command}")
        return False, f"Bash 命令需要确认: {command[:50]}"

    # ========== 4. Write/Edit 操作检查 ==========
    if tool_name in ['Write', 'Edit']:
        file_path = tool_input.get('file_path', '')

        # 危险文件扩展名
        dangerous_extensions = [
            '.env', '.env.local', '.env.production',
            '.key', '.pem', '.cert', '.p12',
            '.exe', '.dll', '.so', '.dylib',
            '.bat', '.sh', '.ps1'
        ]

        # 检查扩展名
        for ext in dangerous_extensions:
            if file_path.endswith(ext):
                return False, f"危险文件类型: {ext}"

        # 检查路径
        dangerous_paths = [
            '/etc/', 'C:\\Windows\\', 'C:\\Program Files\\',
            '/usr/bin/', '/usr/sbin/', '/System/',
            '.ssh/', '.gnupg/'
        ]

        for path in dangerous_paths:
            if path in file_path:
                return False, f"危险路径: {path}"

        # ========== 5. 文档文件 - 自动允许 ==========
        if file_path.endswith('.md'):
            return True, "Markdown 文档编辑"

        # ========== 6. 代码文件 - 自动允许 ==========
        safe_code_extensions = [
            '.py', '.js', '.ts', '.tsx', '.jsx',
            '.json', '.yaml', '.yml', '.toml',
            '.html', '.css', '.scss', '.less',
            '.vue', '.svelte'
        ]

        for ext in safe_code_extensions:
            if file_path.endswith(ext):
                return True, f"代码文件编辑: {ext}"

        # 其他文件类型需要确认
        logger.warning(f"Write/Edit 操作需要确认: {file_path}")
        return False, f"Write/Edit 操作需要确认: {file_path}"

    # ========== 7. Task 工具 - 自动允许 ==========
    if tool_name == 'Task':
        return True, "Task 工具（子Agent）"

    # ========== 8. TodoWrite - 自动允许 ==========
    if tool_name == 'TodoWrite':
        return True, "TodoWrite 工具"

    # ========== 9. Skill 工具 - 自动允许 ==========
    if tool_name == 'Skill':
        return True, "Skill 工具"

    # ========== 默认：需要确认 ==========
    return False, f"未知工具类型: {tool_name}"


def log_permission_decision(tool_name, tool_input, is_safe, reason):
    """记录权限决策"""
    log_entry = {
        "timestamp": get_log_date(),
        "tool": tool_name,
        "safe": is_safe,
        "reason": reason
    }

    # 写入 JSON 日志
    log_file = LOG_DIR / "decisions.jsonl"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")


def main():
    """主函数"""
    try:
        # 读取环境变量
        tool_name = os.environ.get('TOOL_NAME', '')
        tool_input_str = os.environ.get('TOOL_INPUT', '{}')

        # 解析工具输入
        try:
            tool_input = json.loads(tool_input_str)
        except json.JSONDecodeError:
            tool_input = {}

        # 判断是否安全
        is_safe, reason = is_safe_operation(tool_name, tool_input)

        # 记录决策
        log_permission_decision(tool_name, tool_input, is_safe, reason)

        # 输出决策
        if is_safe:
            logger.info(f"✅ 允许: {tool_name} - {reason}")
            print(f"✅ 自动允许: {reason}")
            return 0  # 允许操作
        else:
            logger.warning(f"❌ 阻止: {tool_name} - {reason}")
            print(f"❌ 阻止操作: {reason}")
            print(f"\n工具: {tool_name}")
            if 'file_path' in tool_input:
                print(f"文件: {tool_input['file_path']}")
            if 'command' in tool_input:
                print(f"命令: {tool_input['command']}")
            return 2  # 阻止操作

    except Exception as e:
        logger.error(f"权限检查错误: {e}")
        print(f"❌ 权限检查错误: {e}")
        return 2  # 出错时默认阻止


if __name__ == "__main__":
    sys.exit(main())
