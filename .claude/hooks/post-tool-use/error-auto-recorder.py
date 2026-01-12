#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Error Auto Recorder - 自动错误检测和记录Hook
"""
import json
import sys
import os
import re
from datetime import datetime

def read_json_input():
    """读取Hook的JSON输入"""
    try:
        input_data = sys.stdin.read().strip()
        if not input_data:
            return {}
        return json.loads(input_data)
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON input: {e}", file=sys.stderr)
        return {}

def detect_error_patterns(context):
    """检测错误模式"""
    tool_name = context.get('tool_name', '')
    tool_input = context.get('tool_input', {})
    result = context.get('result', '')

    errors = []

    # 检测技能相关错误
    if tool_name == 'Skill':
        if 'Unknown skill' in str(result):
            errors.append({
                'type': 'skill_not_found',
                'severity': 'high',
                'description': '尝试使用未安装的skill',
                'skill_name': tool_input.get('skill', 'unknown')
            })

    # 检测文档路径错误
    if tool_name in ['Write', 'Edit']:
        file_path = tool_input.get('file_path', '')
        # 应该写入.active/但写到了development/根目录
        if 'development/' in file_path and '.active/' not in file_path:
            if file_path.endswith('.md'):
                errors.append({
                    'type': 'wrong_document_path',
                    'severity': 'medium',
                    'description': f'文档路径错误：应该使用.active/目录，实际使用了{file_path}',
                    'file_path': file_path
                })

    # 检测用户负面反馈（需要从上下文分析）
    conversation_history = context.get('conversation_history', [])
    recent_messages = conversation_history[-5:] if conversation_history else []

    negative_keywords = [
        '又犯错误', '又错了', '你没理解', '这不是我要求的',
        '应该先', '你没做', '还是不行', '没生效'
    ]

    for msg in recent_messages:
        if any(keyword in msg for keyword in negative_keywords):
            errors.append({
                'type': 'user_negative_feedback',
                'severity': 'high',
                'description': f'用户负面反馈: {msg[:100]}...'
            })
            break

    return errors

def generate_error_id():
    """生成错误ID"""
    now = datetime.now()
    date_str = now.strftime('%Y%m%d')

    # 读取现有error-log.md，找到今日最大编号
    error_log_path = 'development/active/tracking/error-log.md'
    max_num = 0

    try:
        if os.path.exists(error_log_path):
            with open(error_log_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 查找今日所有错误编号
                pattern = f'ERR-{date_str}-(\\d+)'
                matches = re.findall(pattern, content)
                if matches:
                    max_num = max(int(m) for m in matches)
    except Exception as e:
        print(f"⚠️ Warning: Could not read error log for ID generation: {e}", file=sys.stderr)

    # 递增编号
    new_num = max_num + 1
    return f'ERR-{date_str}-{new_num:02d}'

def format_error_entry(error, context):
    """格式化错误条目"""
    error_id = generate_error_id()
    now = datetime.now().strftime('%Y-%m-%d %H:%M')

    # 根据错误类型生成标题
    title_map = {
        'skill_not_found': '使用未安装的skill',
        'wrong_document_path': '文档路径错误',
        'user_negative_feedback': '用户负面反馈',
    }
    title = title_map.get(error['type'], '未分类错误')

    # 严重程度映射
    severity_map = {
        'high': '🔴严重',
        'medium': '🟡中等',
        'low': '🟢轻微'
    }
    severity = severity_map.get(error['severity'], '🟡中等')

    entry = f"""
#### [{error_id}] - {title}

**发现时间**: {now}
**发现方式**: 自动检测
**错误类型**: {error['type']}
**严重程度**: {severity}

**问题描述**:
- {error['description']}
"""

    # 添加上下文信息
    if 'file_path' in error:
        entry += f"""
**相关文件**:
- {error['file_path']}
"""

    if 'skill_name' in error:
        entry += f"""
**相关skill**:
- {error['skill_name']}
"""

    entry += """
**根本原因分析**:
- 需要进一步分析

**解决方案**:
- 待分析

**预防措施**:
- 待确定

**状态**: ⏳待检测和分析
"""

    return entry

def append_to_error_log(entry):
    """追加错误到日志文件"""
    error_log_path = 'development/active/tracking/error-log.md'

    try:
        # 读取现有内容
        if os.path.exists(error_log_path):
            with open(error_log_path, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = '# Claude 错误日志\n\n初始化错误日志\n'

        # 找到插入位置（在"今日错误"部分之后）
        if '## 🔴 今日错误' in content:
            # 在今日错误部分最后追加
            lines = content.split('\n')
            insert_index = len(lines)
            for i, line in enumerate(reversed(lines)):
                if line.startswith('## 🔴 历史错误') or line.startswith('---'):
                    insert_index = len(lines) - i
                    break

            lines.insert(insert_index, entry)
            content = '\n'.join(lines)
        else:
            # 如果没有"今日错误"部分，添加一个
            today_section = f"""

## 🔴 今日错误 ({datetime.now().strftime('%Y-%m-%d')})

{entry}

---
## 🔴 历史错误

"""
            content = content.replace('\n## 📚 相关资源', today_section)

        # 写回文件
        with open(error_log_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return True
    except Exception as e:
        print(f"❌ Failed to write error log: {e}", file=sys.stderr)
        return False

def main():
    # 读取Hook输入
    context = read_json_input()

    if not context:
        print(json.dumps({"trigger": "none"}))
        return

    # 检测错误
    errors = detect_error_patterns(context)

    if not errors:
        print(json.dumps({"trigger": "none"}))
        return

    # 发现错误，记录第一个
    error = errors[0]
    entry = format_error_entry(error, context)

    if append_to_error_log(entry):
        print(json.dumps({
            "trigger": "error_detected",
            "error_type": error['type'],
            "message": "错误已自动记录到error-log.md"
        }))
    else:
        print(json.dumps({
            "trigger": "error",
            "error_type": error['type'],
            "message": "记录错误失败"
        }))

if __name__ == '__main__':
    main()
