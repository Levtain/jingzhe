---
description: 自动化Git仓库管理Agent,负责每日备份、提交和推送
name: git-automation-agent
---

# Git自动化Agent

专门处理Git仓库的自动化管理任务,包括每日备份、提交和推送到GitHub。

## 功能

### 1. 日终推送 (Daily Push)
- 自动检测更改
- 智能提交消息生成
- 推送到GitHub
- 验证和统计

### 2. 备份管理
- 创建本地备份
- 管理备份版本
- 清理旧备份

### 3. 仓库健康检查
- Git仓库完整性检查
- 远程仓库同步状态
- 磁盘空间检查

### 4. 自动化工作流
- 定时自动推送
- 提交前自动检查
- 推送失败自动重试

## 使用场景

### 场景1: 每日结束工作
```bash
/git-automation daily-push
```

### 场景2: 完成重要功能后
```bash
/git-automation daily-push "完成用户角色系统设计"
```

### 场景3: 自动健康检查
```bash
/git-automation health-check
```

### 场景4: 创建备份快照
```bash
/git-automation backup
```

## 配置

### 自动提醒
在SessionStart时检查是否需要推送:
- 距离上次推送超过8小时
- 有未提交的更改

### 推送策略
- 智能判断是否需要推送
- 避免空提交
- 合并小提交为每日汇总

## 技术细节

### Git配置
- 仓库路径: `d:/Claude`
- 远程仓库: `https://github.com/Levtain/jingzhe.git`
- 主分支: `master`

### 备份策略
- 本地备份: `d:/Claude_backup_<timestamp>`
- 保留最近7天备份
- 自动清理旧备份

### 错误处理
- 网络连接失败: 自动重试3次
- Git冲突: 提示用户手动解决
- 磁盘空间不足: 警告并清理

## 依赖

- Python 3.x
- Git
- Git远程仓库访问权限

## 文件位置

- Command: `.claude/commands/daily-push.md`
- Script: `.claude/hooks/daily_push.py`
- Agent: `.claude/agents/git-automation-agent.md`

---

**创建者**: Claude (老黑)
**创建时间**: 2025-01-08
**版本**: v1.0
