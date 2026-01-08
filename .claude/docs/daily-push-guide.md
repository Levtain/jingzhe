# 日终自动推送系统使用指南

## 快速开始

### 方式1: 使用命令(推荐)
```bash
/daily-push
```

### 方式2: 直接运行Python脚本
```bash
python .claude/hooks/daily_push.py
```

### 方式3: 自定义提交消息
```bash
/daily-push "完成用户角色系统设计"
```

## 功能特性

### 自动化流程
1. **检查Git状态** - 检测是否有未提交的更改
2. **添加所有更改** - 自动执行 `git add .`
3. **创建提交** - 带时间戳的提交消息
4. **推送到GitHub** - 自动推送到 `origin/master`
5. **验证推送** - 确认推送成功
6. **显示统计** - 展示今日提交记录

### 智能判断
- 如果工作目录干净,会跳过提交并提示
- 如果未配置远程仓库,会提示配置命令
- 每个步骤都有详细的状态输出

## 提交消息格式

默认格式: `chore: daily backup [日期] [时间]`

示例:
```
chore: daily backup 2026-01-08 20:09
```

自定义消息示例:
```
chore: daily backup - 完成用户角色系统设计
```

## 文件结构

```
.claude/
├── commands/
│   └── daily-push.md          # 命令定义
├── hooks/
│   └── daily_push.py          # Python自动化脚本
├── agents/
│   └── git-automation-agent.md # Agent定义
└── docs/
    └── daily-push-guide.md    # 本文档
```

## 自动化配置

### 1. SessionStart提醒
可以在 `.claude/settings.local.json` 或 `SessionStart` hook中配置:
- 检查距离上次推送是否超过8小时
- 检查是否有未提交的更改
- 提醒执行日终推送

### 2. 定时任务
可以使用Windows Task Scheduler配置定时任务:
```powershell
# 每天下午6点执行
schtasks /create /tn "Daily Git Push" /tr "python d:\Claude\.claude\hooks\daily_push.py" /sc daily /st 18:00
```

### 3. Git Hook
在 `.git/hooks/post-commit` 中添加自动推送:
```bash
#!/bin/sh
# 只有在提交消息包含 "daily-push" 时才自动推送
case "$COMMIT_MESSAGE" in
  *daily-push*)
    git push origin master
    ;;
esac
```

## 技术细节

### Git配置
- 仓库路径: `d:/Claude`
- 远程仓库: `https://github.com/Levtain/jingzhe.git`
- 主分支: `master`
- 行尾符: LF (通过 `.gitattributes` 强制)

### 错误处理
- **网络连接失败**: 提示检查代理设置
- **认证失败**: 提示更新GitHub token
- **Git冲突**: 提示用户手动解决
- **磁盘空间不足**: 警告并建议清理

### Python依赖
- Python 3.x (标准库,无需额外安装)
- subprocess (执行Git命令)
- pathlib (路径处理)
- datetime (时间戳生成)

## 常见问题

### Q1: 推送失败提示认证错误?
**A**: GitHub token可能过期,需要更新token:
```bash
echo "https://USERNAME:TOKEN@github.com" | git credential approve
```

### Q2: 找不到Python命令?
**A**: 确保Python已安装并在PATH中:
```bash
python --version
where python
```

### Q3: 想要推送到其他分支?
**A**: 修改 `daily_push.py` 中的推送命令:
```python
["git", "push", "origin", "master"]  # 改为你的分支名
```

### Q4: 如何查看推送历史?
**A**: 使用Git log命令:
```bash
git log --oneline --since="yesterday"
```

## 版本历史

- **v1.0** (2025-01-08)
  - 初始版本
  - 支持完整的自动化推送流程
  - 修复Windows控制台编码问题

## 维护者

- **创建者**: Claude (老黑)
- **最后更新**: 2025-01-08

---

**相关文件**:
- [daily-push.md](.claude/commands/daily-push.md) - 命令定义
- [daily_push.py](.claude/hooks/daily_push.py) - 自动化脚本
- [git-automation-agent.md](.claude/agents/git-automation-agent.md) - Agent定义
