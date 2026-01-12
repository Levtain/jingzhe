---
description: 手动触发上下文快照保存,用于在重要节点主动保存当前状态
argument-hint: [--decisions | --force | --message "备注"]
allowed-tools: Read, Write, Grep
---

# /save-context 命令

手动触发上下文快照保存命令。

## 功能

在重要节点主动保存当前上下文状态到 `development/memories/context-snapshots/` 和 `.claude/skills/agent-memory/memories/context-snapshots/`。

## 使用方法

### 基本用法

```bash
/save-context                    # 保存完整上下文快照
/save-context --decisions        # 仅保存决策
/save-context --force            # 强制保存(忽略上下文使用率)
/save-context --message "备注"   # 添加说明信息
```

### 参数选项

```bash
--mode, -m
    模式选择:
    - full: 完整快照(默认)
    - decisions: 仅保存决策

--message, -m
    添加说明信息
    示例: --message "完成反作弊系统讨论"

--force, -f
    强制保存,忽略上下文使用率限制

--help, -h
    显示帮助信息
```

---

## 执行流程

### 1. 检查当前状态

```bash
# 调用 /context 命令检查使用率
current_usage=$(/context)
usage_rate=$(parseUsageRate "$current_usage")
```

### 2. 根据模式执行

**full mode** (默认):
```bash
# 读取必要信息
- 最近3个daily-summary
- development/active/issues/questions.md
- docs/product/claude.md (进度概览部分)
- 当前会话历史

# 生成完整快照
# 保存到:
#   - .claude/skills/agent-memory/memories/context-snapshots/
#   - development/memories/context-snapshots/
```

**decisions mode**:
```bash
# 仅提取决策
- 扫描当前会话中的决策关键词
- 提取确认的内容
- 保存到:
#   - .claude/skills/agent-memory/memories/decisions/
#   - development/memories/design-decisions/
```

### 3. 保存成功反馈

```markdown
✅ 上下文快照已保存

📄 文件位置:
- 系统记忆: .claude/skills/agent-memory/memories/context-snapshots/2025-01-12-session-1.md
- 项目记忆: development/memories/context-snapshots/2025-01-12-session-1.md

📊 快照内容:
- 进度: 96/149 (64%)
- 当前讨论: 反作弊系统
- 保存时间: 2025-01-12 14:30

💡 提示: 下次会话开始时可选择恢复此快照
```

---

## 使用场景

### 场景1: 完成重要讨论后

```bash
你: 刚完成反作弊系统所有问题的讨论
我: 太好了!建议保存上下文快照
    输入: /save-context --message "反作弊系统8个问题全部确认"
```

### 场景2: 长时间工作后

```bash
你: 今天先到这里
我: 好的,自动保存上下文
    (session-end Hook自动触发)
```

### 场景3: 即将进行重要工作前

```bash
你: 准备开始讨论排名系统了
我: 建议先保存当前上下文,以便随时恢复
    输入: /save-context --message "准备开始排名系统讨论"
```

---

## 文件命名规则

**自动生成命名**:
```
{YYYY-MM-DD}-session-{序号}.md

示例:
2025-01-12-session-1.md
2025-01-12-session-2.md
2025-01-13-session-1.md
```

**带自定义消息**:
```
{YYYY-MM-DD}-{简短描述}-session-{序号}.md

示例:
2025-01-12-anti-cheat-completed-session-1.md
2025-01-12-ranking-start-session-2.md
```

---

## 快照内容格式

### full mode 内容

```markdown
---
summary: "上下文快照 - {日期时间}"
created: 2025-01-12
usage_rate: 85
mode: full
message: "用户自定义备注"
tags: [context-snapshot, {date}]
---

# 上下文快照 - 2025-01-12 14:30

## 📊 进度概览

**问题确认**: 96/149 (64%)
**当前阶段**: 设计讨论
**最近更新**: 2025-01-12

## 💬 最近工作总结

### 最近3日工作

**2025-01-12**:
- ✅ 反作弊系统: 8个问题全部确认
- ✅ 成就系统: 5个问题确认

**2025-01-11**:
- ✅ 排名系统: 3个问题确认
- ✅ 文档更新

**2025-01-10**:
- ✅ 经济系统: 2个问题确认

## 🎯 当前状态

**正在讨论**: 反作弊系统

**已确认决策**:
- 善意度初始值: 100分
- 检测算法: 基于评分模式
- 处理策略: 分阶段处理

**待确认问题**:
- 排名系统: 15个问题
- 推荐位机制: 5个问题

## 📝 下一步建议

1. 继续讨论排名系统细节
2. 生成排名系统PRD
3. 确认推荐位机制

---
**保存时间**: 2025-01-12 14:30:22
**上下文使用率**: 85%
**触发方式**: 手动 (/save-context)
```

### decisions mode 内容

```markdown
---
summary: "决策记录 - {日期时间}"
created: 2025-01-12
mode: decisions
tags: [decisions, {date}]
---

# 设计决策记录 - 2025-01-12

## 反作弊系统决策

### 决策1: 善意度初始值
- **时间**: 2025-01-12 10:15
- **决策**: 100分,新用户默认信任
- **理由**: 降低新用户门槛,提升参与度

### 决策2: 作弊检测算法
- **时间**: 2025-01-12 11:30
- **决策**: 基于评分模式分析
- **细节**:
  - 突然大量评分
  - 评分过于一致
  - 异常时间段评分

### 决策3: 处理策略
- **时间**: 2025-01-12 14:20
- **决策**: 分阶段处理
- **流程**:
  1. 降低善意度
  2. 取消评分权重
  3. 极端情况封禁

---
**记录时间**: 2025-01-12 14:30
**相关问题**: 反作弊系统 8个问题
```

---

## 注意事项

1. **自动保存优先**:
   - session-end Hook会自动保存
   - 关键操作后会自动保存
   - 手动保存是补充,不是必需

2. **避免过度保存**:
   - 不要每次小操作都保存
   - 建议在重要节点保存
   - 系统会自动管理旧快照

3. **快照清理**:
   - 每个会话日最多保留5个快照
   - 超过30天的快照自动归档
   - 可手动删除不需要的快照

---

## 配合自动触发

**自动触发场景** (无需手动):
- ✅ 讨论完一个问题 (标记✅后)
- ✅ 执行 `/sync-docs` 后
- ✅ 执行 `/daily-summary` 后
- ✅ 上下文使用率达到85%

**手动触发场景** (建议使用):
- 📝 完成重要功能讨论后
- 📝 即将切换工作重点前
- 📝 想要手动创建检查点
- 📝 不确定下次何时继续

---

## 错误处理

### 错误1: 无法读取questions.md

```markdown
⚠️ 警告: 无法读取问题清单

文件: development/active/issues/questions.md

建议:
- 检查文件是否存在
- 继续保存其他内容

已保存部分快照...
```

### 错误2: agent-memory不可写

```markdown
⚠️ 警告: 系统记忆写入失败

已保存到项目记忆:
- development/memories/context-snapshots/2025-01-12-session-1.md

建议:
- 检查文件权限
- 检查磁盘空间
```

---

## 相关命令

- `/sync-docs` - 同步文档(会自动触发快照)
- `/daily-summary` - 生成每日总结(会自动触发快照)
- `/check-progress` - 检查项目进度

---

## 版本历史

- **v1.0** (2025-01-12): 初始版本
  - 基本保存功能
  - full/decisions两种模式
  - 自动命名规则

---

**创建时间**: 2025-01-12
**维护者**: AI (Claude)
**状态**: ✅ 设计完成,待实现
