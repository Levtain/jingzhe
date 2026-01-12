---
name: auto-context-snapshot
description: 关键操作后自动触发上下文快照保存(提醒+决策记录),配合PreCompact Hook使用
version: 1.2
triggers:
  - usage_80_98: 上下文使用率80-98%时显示提醒
  - usage_99_plus: 上下文使用率≥99%时记录决策
  - question_confirmed: 问题标记为✅后
  - sync_docs: 执行/sync-docs后
  - daily_summary: 执行/daily-summary后
---

# 自动上下文监控与提醒机制

在关键节点提供监控和提醒,配合PreCompact Hook使用。

**主要触发器**: PreCompact Hook (系统级,压缩前保存完整快照)
**辅助触发器**: PostToolUse Hook (监控+提醒+决策记录)

**阈值设置** (v1.2):
- **80-98%**: 显示友好提醒 💡
- **≥99%**: 记录决策 📝
- **PreCompact**: 完整快照 💾

---

## 触发场景

### 场景1: 问题确认后触发 ⭐

**触发条件**:
- questions.md中问题状态从❌变为✅
- 通过/discuss命令确认
- 手动标记完成

**触发逻辑**:
```javascript
// 在PostToolUse Hook中检测
onAfterToolUse(function(toolName, result) {
  if (toolName === 'Edit' || toolName === 'Write') {
    // 检查是否修改了questions.md
    if (file === 'development/active/issues/questions.md') {
      // 检查是否有新的✅标记
      if (hasNewConfirmedQuestions(result)) {
        triggerContextSnapshot('decisions', {
          reason: '问题确认',
          question_count: countNewConfirmed(result)
        });
      }
    }
  }
});
```

**保存内容**: decisions mode
- 提取新确认的问题
- 记录决策要点
- 保存到 `decisions/`

---

### 场景2: 文档同步后触发

**触发条件**: 执行 `/sync-docs` 命令后

**触发逻辑**:
```javascript
// 在sync-docs命令执行后
onCommandComplete('/sync-docs', function(result) {
  // 检查同步内容
  if (result.hasChanges) {
    triggerContextSnapshot('full', {
      reason: '文档同步',
      files_synced: result.files.length
    });
  }
});
```

**保存内容**: full mode
- 完整上下文快照
- 包含同步的变更
- 记录到 `context-snapshots/`

---

### 场景3: 每日总结后触发

**触发条件**: 执行 `/daily-summary` 命令后

**触发逻辑**:
```javascript
// 在daily-summary命令执行后
onCommandComplete('/daily-summary', function(result) {
  triggerContextSnapshot('full', {
    reason: '每日总结',
    tasks_completed: result.taskCount
  });
});
```

**保存内容**: full mode
- 保存每日总结到agent-memory
- 同时保存上下文快照
- 记录到 `context-snapshots/`

---

## 自动触发的优势

### 1. 无需记忆

**之前**:
```
用户完成重要讨论
用户: 需要手动保存吗?
AI: 你可以运行 /save-context
用户: 好的 /save-context
```
❌ 容易忘记

**现在**:
```
用户完成重要讨论
标记问题为✅
→ 系统自动保存 ✅
```
✅ 完全自动

### 2. 及时保存

**关键节点自动保存**:
- ✅ 问题确认后立即保存
- ✅ 文档同步后立即保存
- ✅ 每日总结后立即保存

**不会丢失重要信息**

### 3. 减轻负担

**用户不需要**:
- ❌ 记住什么时候保存
- ❌ 手动运行命令
- ❌ 担心忘记保存

**系统自动处理**

---

## 节流策略

### 避免过度保存

**规则1**: 同类操作5分钟内只触发一次
```javascript
const lastSave = getLastSaveTime('question_confirmed');
if (Date.now() - lastSave < 5 * 60 * 1000) {
  return; // 跳过本次保存
}
```

**规则2**: 决策模式保存更频繁
- question_confirmed: decisions mode (轻量)
- sync_docs: full mode (完整)
- daily_summary: full mode (完整)

**规则3**: 内容变化才保存
```javascript
const contentHash = calculateHash(content);
if (contentHash === lastSavedHash) {
  return; // 内容未变化,跳过
}
```

---

## 与手动触发的配合

### 手动触发优先级

**手动 > 自动**

```javascript
// 如果用户刚刚手动保存
if (timeSinceManualSave < 60 * 1000) {
  skipAutoSave(); // 跳过自动保存
}
```

**原因**:
- 避免重复保存
- 尊重用户意图
- 节省资源

### 推荐使用时机

**自动触发** (无需手动):
- ✅ 问题确认后
- ✅ 文档同步后
- ✅ 每日总结后
- ✅ 上下文使用率≥85%

**手动触发** (建议使用):
- 📝 完成重要功能讨论后
- 📝 即将切换工作重点前
- 📝 想要创建检查点
- 📝 不确定下次何时继续

---

## 触发日志记录

所有自动触发都会记录到日志:

```markdown
[2025-01-12 14:30:22] Auto-save triggered
  Reason: question_confirmed
  Mode: decisions
  Questions: 3
  File: context-snapshots/2025-01-12-auto-1.md

[2025-01-12 16:45:10] Auto-save triggered
  Reason: sync_docs
  Mode: full
  Files: 5
  File: context-snapshots/2025-01-12-auto-2.md
```

日志位置: `development/logs/context-monitor/auto-saves.log`

---

## 错误处理

### 失败不影响主流程

```javascript
try {
  triggerContextSnapshot('decisions');
} catch (error) {
  // 静默失败
  logError(error);
  // 不中断用户当前操作
}
```

**原则**:
- 自动保存失败不影响用户工作
- 记录错误日志供后续分析
- 显示友好提醒(可选)

---

## 配置选项

```json
{
  "autoSnapshot": {
    "enabled": true,
    "triggers": {
      "question_confirmed": {
        "enabled": true,
        "mode": "decisions",
        "throttle": 300
      },
      "sync_docs": {
        "enabled": true,
        "mode": "full",
        "throttle": 60
      },
      "daily_summary": {
        "enabled": true,
        "mode": "full",
        "throttle": 3600
      }
    },
    "maxPerDay": 20,
    "cleanupAfterDays": 30
  }
}
```

---

## 监控指标

系统会记录以下指标:

```javascript
{
  "autoSaves": {
    "total": 150,
    "today": 12,
    "byReason": {
      "question_confirmed": 8,
      "sync_docs": 2,
      "daily_summary": 1,
      "context_threshold": 1
    },
    "averageSize": "45KB",
    "successRate": 0.98
  }
}
```

---

## 版本历史

- **v1.0** (2025-01-12): 初始版本
  - 3种自动触发场景
  - 节流策略
  - 错误处理机制

---

**创建时间**: 2025-01-12
**维护者**: AI (Claude)
**状态**: ✅ 设计完成,待实现
