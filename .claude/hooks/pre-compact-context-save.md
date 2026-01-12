---
name: pre-compact-context-save
description: 在系统即将压缩上下文前,自动保存完整上下文快照
phase: pre_compact
version: 1.0
---

# PreCompact Hook - 上下文压缩前自动保存

在系统即将执行上下文压缩操作前,自动保存完整的上下文快照。

---

## 🎯 核心功能

**触发时机**: PreCompact Hook (系统级)
**触发条件**: 系统即将压缩上下文
**执行动作**: 保存完整上下文快照

---

## 📋 执行流程

### 步骤1: 触发检测

```javascript
// PreCompact Hook自动触发
系统: "准备压缩上下文"
  ↓
PreCompact Hook触发
```

### 步骤2: 收集信息

**读取进度数据**:
```javascript
// 1. 当前进度
const questions = read('development/active/issues/questions.md');
const confirmed = countConfirmed(questions);
const total = questions.length;
const percentage = (confirmed / total) * 100;

// 2. 最近工作总结
const summaries = getRecentDailySummaries(3); // 最近3个

// 3. 当前会话信息
const currentSession = extractCurrentSessionInfo();

// 4. 项目概览
const projectOverview = read('docs/product/claude.md');
```

### 步骤3: 生成快照

**快照内容结构**:
```markdown
---
summary: "上下文快照 - 压缩前自动保存"
created: 2025-01-12
trigger: pre-compact
usage_rate: 92
mode: full
tags: [context-snapshot, auto-save, pre-compact]
---

# 上下文快照 - 2025-01-12 16:45

> ⚠️ 系统即将压缩上下文,已自动保存当前状态

## 📊 进度概览

**问题确认**: 96/149 (64%)
**当前阶段**: 设计讨论
**上下文使用率**: 92%

## 💬 最近工作总结

### 最近3日工作

**2025-01-12**:
- ✅ 反作弊系统: 8个问题全部确认
- ✅ 成就系统: 5个问题确认
- 📝 完成文档更新

**2025-01-11**:
- ✅ 排名系统: 3个问题确认
- ✅ 文档同步

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
- 社区功能: 6个问题

## 💡 下一步建议

1. 继续讨论排名系统细节
2. 生成排名系统PRD
3. 确认推荐位机制

## 📁 相关文件

- 问题清单: development/active/issues/questions.md
- 项目文档: docs/product/claude.md
- 变更日志: docs/product/CHANGELOG.md

---
**保存时间**: 2025-01-12 16:45:32
**触发方式**: PreCompact Hook (系统自动)
**上下文使用率**: 92%
```

### 步骤4: 保存快照

**保存位置** (双重保存):
```javascript
// 系统级记忆 (Claude读取)
saveTo('.claude/skills/agent-memory/memories/context-snapshots/2025-01-12-pre-compact.md');

// 项目级记忆 (人类查阅)
saveTo('development/memories/context-snapshots/2025-01-12-pre-compact.md');
```

### 步骤5: 记录日志

```javascript
logTo('development/logs/context-monitor/pre-compact-triggers.log', {
  timestamp: '2025-01-12 16:45:32',
  usage_rate: 92,
  confirmed: 96,
  total: 149,
  snapshot_file: '2025-01-12-pre-compact.md',
  status: 'success'
});
```

---

## ✅ 优势

### 1. 系统级触发,100%可靠

**不会错过任何压缩**:
- ✅ 系统主动通知
- ✅ 无需定期轮询
- ✅ 无需依赖/context命令

### 2. 压缩前自动保存

**完美时机**:
- ✅ 压缩前最后一刻
- ✅ 保存最完整状态
- ✅ 不会遗漏信息

### 3. 双重保存机制

**系统级 + 项目级**:
- ✅ Claude可读取 (agent-memory)
- ✅ 人类可查阅 (development/memories)
- ✅ 各司其职

---

## 🔄 与其他触发方式的配合

### 配合PostToolUse Hook

**PostToolUse Hook** (辅助触发器):
- 70-84%: 显示提醒
- ≥85%: 记录决策
- 作为PreCompact的补充

### 配合手动触发

**手动触发** (/save-context):
- 用户随时可手动保存
- 完全可控
- 作为补充和兜底

---

## 📝 配置示例

### Hook配置

```json
{
  "name": "pre-compact-context-save",
  "description": "上下文压缩前自动保存",
  "phase": "pre_compact",
  "enabled": true,
  "config": {
    "saveLocation": [
      ".claude/skills/agent-memory/memories/context-snapshots/",
      "development/memories/context-snapshots/"
    ],
    "readCount": 3,
    "format": "markdown",
    "includeMetadata": true
  }
}
```

---

## ⚠️ 注意事项

### 1. 快照大小

**限制**: 单个快照建议<100KB

**原因**:
- 避免占用过多空间
- 加快读取速度
- 便于后续管理

**策略**:
- 只保存关键信息
- 不包含完整会话历史
- 引用而非复制

### 2. 保存频率

**限制**: 同一天最多5个PreCompact快照

**策略**:
```javascript
if (countTodayPreCompacts() >= 5) {
  // 只保存增量
  saveIncrementalSnapshot();
} else {
  // 保存完整快照
  saveFullSnapshot();
}
```

### 3. 错误处理

**失败不影响压缩**:
```javascript
try {
  saveContextSnapshot();
} catch (error) {
  logError(error);
  // 不抛出异常,让系统继续压缩
}
```

---

## 🔗 相关文件

- **Hook文件**: `.claude/hooks/pre-compact/`
- **日志文件**: `development/logs/context-monitor/pre-compact-triggers.log`
- **快照位置**:
  - `.claude/skills/agent-memory/memories/context-snapshots/`
  - `development/memories/context-snapshots/`

---

## 📊 监控指标

```javascript
{
  "preCompactSaves": {
    "total": 50,
    "thisWeek": 12,
    "successRate": 0.98,
    "averageSize": "45KB",
    "averageTime": "350ms"
  }
}
```

---

## 🎯 版本历史

- **v1.0** (2025-01-12): 初始版本
  - PreCompact Hook集成
  - 双重保存机制
  - 完整快照生成

---

**创建时间**: 2025-01-12
**维护者**: AI (Claude)
**状态**: ✅ 设计完成,待实现
