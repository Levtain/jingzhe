#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SessionStart Hook - 会话开始时自动加载项目状态并检查版本一致性
"""

import json
import sys
import os
import re
from pathlib import Path

# 设置stdout编码为UTF-8,避免Windows环境下的编码错误
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def read_file_lines(file_path, max_lines):
    """读取文件的前N行"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = []
            for i, line in enumerate(f):
                if i >= max_lines:
                    break
                lines.append(line.rstrip('\n'))
            return lines
    except Exception as e:
        print(f"❌ 读取文件错误: {e}", file=sys.stderr)
        return None

def extract_version(lines, pattern):
    """从文件行中提取版本号"""
    for line in lines:
        match = re.search(pattern, line)
        if match:
            return match.group(1)
    return None

def find_claude_md():
    """智能查找claude.md文件"""
    # 可能的路径（按优先级）
    possible_paths = [
        "./claude.md",  # 当前目录
        "../claude.md",  # 上级目录
        "../../docs/product/claude.md",  # 从项目根目录
        "docs/product/claude.md",  # 从项目根目录（相对路径）
    ]

    for path_str in possible_paths:
        path = Path(path_str)
        if path.exists() and path.is_file():
            return path.resolve()  # 返回绝对路径

    return None

def get_project_summary():
    """获取项目状态摘要"""
    # 智能查找claude.md
    claude_path = find_claude_md()

    if not claude_path:
        return "未知", "无法找到项目配置文件"

    # 读取前50行
    lines = read_file_lines(str(claude_path), 50)

    if not lines:
        return "未知", "无法读取项目配置"

    # 提取版本号
    version = extract_version(lines, r'版本：v(\d+\.\d+)')

    # 查找当前阶段
    stage = "设计讨论"
    for line in lines:
        if "**当前阶段**" in line or "当前阶段" in line:
            stage = line.strip().strip("*").strip()
            break

    return version, stage

def main():
    """主函数"""
    version, stage = get_project_summary()

    if not version:
        version = "未知"

    # 构建系统消息
    system_message = f"""{'='*60}
🎯 惊蛰计划 v{version}
{'='*60}
📊 当前状态: {stage}
💬 提示: 用自然语言交流即可，无需记住命令
   例如: "看看进度"、"同步一下"、"今天先这样"
{'='*60}
✅ 准备就绪!
{'='*60}"""

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
