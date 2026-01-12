#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SessionStart Hook - 上下文恢复功能
检查最近的上下文快照并询问用户是否恢复
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

# 设置stdout编码为UTF-8
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def format_time_ago(timestamp):
    """格式化时间为"多久之前""""
    now = datetime.now()
    diff = now - timestamp

    minutes = int(diff.total_seconds() / 60)
    hours = minutes // 60
    days = hours // 24

    if days > 0:
        return f"{days}天前"
    elif hours > 0:
        return f"{hours}小时前"
    elif minutes > 0:
        return f"{minutes}分钟前"
    else:
        return "刚刚"

def format_bytes(size):
    """格式化字节大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f}{unit}"
        size /= 1024.0
    return f"{size:.1f}TB"

def parse_frontmatter(content):
    """解析Markdown文件的frontmatter"""
    lines = content.split('\n')
    if not lines or not lines[0].startswith('---'):
        return {}

    frontmatter = {}
    for line in lines[1:]:
        if line.startswith('---'):
            break
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip().strip('"').strip("'")

    return frontmatter

def find_recent_snapshots(max_age_hours=24, max_size_kb=100):
    """查找最近的上下文快照"""
    # 检查系统级和项目级两个位置
    snapshot_dirs = [
        Path('.claude/skills/agent-memory/memories/context-snapshots'),
        Path('development/memories/context-snapshots')
    ]

    snapshots = []

    for snapshot_dir in snapshot_dirs:
        if not snapshot_dir.exists():
            continue

        for file in snapshot_dir.glob('*.md'):
            if file.name.startswith('.'):
                continue

            stat = file.stat()
            mtime = datetime.fromtimestamp(stat.st_mtime)
            size = stat.st_size

            # 过滤条件
            age = datetime.now() - mtime
            if age.total_seconds() > max_age_hours * 3600:
                continue

            if size > max_size_kb * 1024:
                continue

            snapshots.append({
                'path': str(file),
                'filename': file.name,
                'timestamp': mtime,
                'size': size
            })

    # 按时间倒序排序
    snapshots.sort(key=lambda x: x['timestamp'], reverse=True)

    return snapshots

def extract_snapshot_summary(snapshot):
    """提取快照摘要信息"""
    try:
        with open(snapshot['path'], 'r', encoding='utf-8') as f:
            content = f.read()

        frontmatter = parse_frontmatter(content)

        confirmed = int(frontmatter.get('confirmed_questions', 0))
        total = int(frontmatter.get('total_questions', 0))
        percentage = int(confirmed / total * 100) if total > 0 else 0

        return {
            'timeAgo': format_time_ago(snapshot['timestamp']),
            'exactTime': snapshot['timestamp'].strftime('%Y-%m-%d %H:%M'),
            'confirmed': confirmed,
            'total': total,
            'percentage': percentage,
            'currentTopic': frontmatter.get('current_topic', '未知'),
            'trigger': frontmatter.get('trigger', 'unknown'),
            'size': format_bytes(snapshot['size']),
            'filename': snapshot['filename'],
            'path': snapshot['path']
        }
    except Exception as e:
        print(f"❌ 解析快照失败: {e}", file=sys.stderr)
        return None

def display_snapshot_summary(summary):
    """显示快照摘要"""
    print("\n" + "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("💡 发现最近的上下文快照")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"\n📅 时间: {summary['timeAgo']} ({summary['exactTime']})")
    print(f"📊 进度: {summary['confirmed']}/{summary['total']} ({summary['percentage']}%)")
    print(f"🎯 当前讨论: {summary['currentTopic']}")
    print(f"📦 大小: {summary['size']}")
    print(f"\n是否恢复完整上下文? [Y/n]")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

def load_full_snapshot(snapshot_path):
    """加载并显示完整快照"""
    try:
        with open(snapshot_path, 'r', encoding='utf-8') as f:
            content = f.read()

        divider = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

        print("\n正在加载上下文快照...\n")
        print(divider)
        print(content)
        print(divider)
        print("\n✅ 上下文已恢复,可以继续工作\n")

        return True
    except Exception as e:
        print(f"❌ 加载快照失败: {e}", file=sys.stderr)
        return False

def main():
    """主函数"""
    try:
        # 查找最近快照
        snapshots = find_recent_snapshots(max_age_hours=24, max_size_kb=100)

        if not snapshots:
            # 无快照,静默退出
            sys.exit(0)

        # 只处理最新的一个
        latest_snapshot = snapshots[0]
        summary = extract_snapshot_summary(latest_snapshot)

        if not summary:
            sys.exit(0)

        # 显示摘要
        display_snapshot_summary(summary)

        # 注意: 由于这是Hook,不能交互式等待用户输入
        # 我们只显示提示,用户可以手动运行 /save-context --list 查看所有快照
        print("ℹ️  提示: 查看完整快照内容请手动运行: /save-context --list\n")

    except Exception as e:
        # 错误不应该中断会话启动
        print(f"❌ SessionStart load-context错误: {e}", file=sys.stderr)
        sys.exit(0)

    sys.exit(0)

if __name__ == "__main__":
    main()
