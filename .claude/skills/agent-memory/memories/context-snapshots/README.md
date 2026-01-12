# 上下文快照存储目录

## 说明

此目录用于存储系统级上下文快照,供Claude读取和恢复。

## 文件命名规则

```
{YYYY-MM-DD}-{触发方式}-{序号}.md
```

## 触发方式

- `session`: 手动触发 (/save-context)
- `pre-compact`: PreCompact Hook触发
- `auto`: PostToolUse Hook自动触发

## 示例

```
2025-01-12-session-1.md
2025-01-12-pre-compact-1.md
2025-01-12-auto-1.md
```

## 注意事项

- 此目录中的文件由memory-agent自动管理
- 每日最多保留5个快照,超出会自动归档
- 30天以上的快照会自动归档到archive/
