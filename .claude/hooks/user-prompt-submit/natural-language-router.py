#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UserPromptSubmit Hook - 自然语言命令路由器
将用户的自然语言输入自动转换为对应的斜杠命令
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
        user_prompt = input_data.get('user_prompt', '')

        if not user_prompt:
            sys.exit(0)

        # 匹配自然语言命令
        matched_command = match_natural_command(user_prompt)

        if matched_command:
            # 找到匹配的命令,修改用户输入
            # 注意: UserPromptSubmit Hook不能直接修改输入,
            # 但可以返回一个新的prompt让Claude处理

            # 构建新的prompt
            original_input = user_prompt
            new_prompt = f"{matched_command}\n\n原始输入: {original_input}"

            # 输出JSON,Claude会使用这个作为新的prompt
            output = {
                "user_prompt": new_prompt,
                "original_input": original_input,
                "detected_command": matched_command
            }

            print(json.dumps(output, ensure_ascii=False))

            # 可选: 显示提示信息
            print(f"\n💡 检测到自然语言命令,自动转换为: {matched_command}\n", file=sys.stderr)

            sys.exit(0)
        else:
            # 没有匹配的命令,保持原样
            sys.exit(0)

    except Exception as e:
        # 出错时不影响正常使用
        print(f"❌ Natural language router error: {e}", file=sys.stderr)
        sys.exit(0)

if __name__ == "__main__":
    main()
