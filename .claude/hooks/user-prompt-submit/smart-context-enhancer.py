#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UserPromptSubmit Hook - 智能上下文增强器
当检测到自然语言指令时,自动追加对应的命令作为上下文
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

# 自然语言命令映射
NL_COMMANDS = {
    # 进度查看类
    r'看看?进度?|check progress|查看状态': '/check-progress',

    # 文档同步类
    r'同步一下|sync docs|同步文档': '/sync-docs',

    # 总结类
    r'今天先这样|daily.*summary|生成总结|今天总结': '/daily-summary',

    # 讨论类
    r'开始讨论|discuss|讨论问题': '/discuss',

    # 上下文保存类
    r'保存上下文|save.*context|保存状态': '/save-context',

    # 问题列表类
    r'(查看)?问题(列表)?|questions|看看问题': '/check-progress',

    # Token检查类
    r'检查token|token.*check|看看token': '/token-check',

    # 文档审核类
    r'审核文档|review.*doc|检查文档': '/review-docs',
}

def match_natural_command(user_input):
    """匹配自然语言到命令"""

    # 去除首尾空格
    text = user_input.strip()

    # 如果已经是斜杠命令,直接返回
    if text.startswith('/'):
        return None

    # 遍历所有模式
    for pattern, command in NL_COMMANDS.items():
        if re.search(pattern, text, re.IGNORECASE):
            return command

    return None

def main():
    """主函数"""

    try:
        # 读取stdin (Claude传递的JSON数据)
        input_data = json.load(sys.stdin)

        # 获取用户输入
        user_prompt = input_data.get('prompt', '')

        if not user_prompt:
            sys.exit(0)

        # 匹配自然语言命令
        matched_command = match_natural_command(user_prompt)

        if matched_command:
            # 关键:使用additionalContext追加命令
            # 这样Claude会看到用户的原始输入 + 我们追加的命令

            output = {
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": f"\n\n[系统提示: 检测到自然语言指令,自动执行对应命令]\n{matched_command}\n"
                }
            }

            print(json.dumps(output, ensure_ascii=False, indent=2))

            # 显示提示信息到stderr (用户可见)
            print(f"\n💡 检测到自然语言指令,已自动触发: {matched_command}\n", file=sys.stderr)

            sys.exit(0)
        else:
            # 没有匹配的命令,保持原样
            sys.exit(0)

    except Exception as e:
        # 出错时不影响正常使用
        print(f"❌ Smart context enhancer error: {e}", file=sys.stderr)
        sys.exit(0)

if __name__ == "__main__":
    main()
