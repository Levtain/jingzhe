---
summary: "上下文监控系统设计 - PreCompact Hook主要触发器+PostToolUse Hook辅助监控(80%提醒/99%决策),三层触发机制,双重保存策略,完整设计方案已完成"
created: 2025-01-12
updated: 2025-01-12
status: completed ✅
version: 1.2
tags: [context-management, memory-agent, hook-design, automation, project-restructure, pre-compact-hook]
related: [.claude/hooks/pre-compact-context-save.md, .claude/hooks/auto-context-snapshot.md, .claude/hooks/session-start/load-context.md, .claude/agents/memory-agent.md, .claude/commands/save-context.md, development/memories/]
---

# 上下文监控系统设计讨论

> **创建时间**: 2025-01-12
> **完成时间**: 2025-01-12
> **状态**: ✅ 设计完成,待实现
> **参与者**: 老黑(Claude) + 蜡烛先生

---

## 🎯 问题背景

**核心问题**: 对话中经常遇到上下文用尽,系统内置的上下文总结器会丢失重要细节。

**目标**: 创建智能的上下文持久化和恢复机制,在上下文用尽前自动保存重要信息。

---

## ✅ 问题1: 触发时机选择 (已解决)

### 最终方案: PostToolUse Hook + /context命令监控

**技术路线**:
```
PostToolUse Hook
  ↓
调用 /context 命令
  ↓
解析输出: "**Tokens:** 55.8k / 200.0k (28%)"
  ↓
提取百分比: 正则表达式 /\((\d+)%\)/
  ↓
判断阈值并触发memory-agent
```

### /context命令返回格式

**实际输出** (Markdown表格,非JSON):
```markdown
## Context Usage

**Model:** claude-sonnet-4-5-20250929
**Tokens:** 55.8k / 200.0k (28%)

### Categories

| Category | Tokens | Percentage |
|----------|--------|------------|
| System prompt | 3.5k | 1.7% |
| System tools | 13.5k | 6.7% |
...
```

**关键数据**: `(28%)` - 通过正则提取

### 三级阈值机制

| 使用率 | 动作 | 说明 |
|--------|------|------|
| <80% | 无操作 | 安全范围 |
| 80-98% | 显示提醒 | 💡 友好提示用户 |
| ≥99% | 记录决策 | 提取并保存重要决策 |
| PreCompact | 完整快照 | 保存完整上下文状态 |

### PostToolUse Hook实现要点

**1. 节流机制** (避免频繁检查):
```javascript
// 最多每60秒检查一次
const lastCheck = localStorage.getItem('lastContextCheck');
const now = Date.now();
if (lastCheck && (now - parseInt(lastCheck)) < 60000) {
  return; // 跳过本次检查
}
localStorage.setItem('lastContextCheck', now.toString());
```

**2. 解析使用率**:
```javascript
function parseUsageRate(output) {
  const match = output.match(/\((\d+)%\)/);
  return match ? parseInt(match[1]) : null;
}
```

**3. 阈值判断与触发**:
```javascript
if (usageRate >= 85) {
  triggerMemoryAgent('full');      // 完整上下文快照
} else if (usageRate >= 70) {
  triggerMemoryAgent('decisions'); // 仅记录决策
} else if (usageRate >= 60) {
  showReminder(usageRate);         // 显示友好提醒
}
```

**4. 错误处理**:
- 解析失败时静默失败,不影响正常工作
- 所有异常捕获并记录日志

### 性能优化

1. **节流**: 最多每分钟检查一次
2. **内容哈希**: 避免重复保存相同内容
3. **异步执行**: 不阻塞主流程
4. **失败静默**: 解析失败不影响用户工作

### 配置选项

```json
{
  "contextMonitor": {
    "checkInterval": 60,      // 检查间隔(秒)
    "warningThreshold": 80,   // 提醒阈值 (v1.2更新)
    "decisionThreshold": 99,  // 决策记录阈值 (v1.2更新)
    "snapshotThreshold": 85,  // 快照阈值
    "enabled": true           // 是否启用
  }
}
```

### 日志记录

文件: `development/logs/context-monitor/2025-01-12-context-checks.log`

格式:
```
[2025-01-12 14:30:22] Usage: 28% - Action: none
[2025-01-12 14:32:15] Usage: 85% - Action: warning_shown
[2025-01-12 14:35:08] Usage: 99% - Action: decisions_saved
[2025-01-12 14:36:00] PreCompact - Action: full_snapshot
```

---

## ⏳ 问题2-5: 待讨论

### 问题2: 每日总结读取范围

**原方案**: "读取最近两天的daily-summary"

**场景问题**:
- 周五工作 → 周末休息 → 周一恢复
- 只读2天会错过周五的工作

**待选方案**:
- 选项A: 读取最近3个summary文件(不论天数)
- 选项B: 读取最近7天内的所有summary
- 选项C: 最近3个summary,但不超过7天 (平衡)

**新思考** (基于/context机制):
- 是否需要读取daily-summary?
- 还是只读取最近的context-snapshot就够了?
- 两者都读: 先读snapshot再读summary补充?

**状态**: 等待用户决策

---

### 问题3: 文件结构和命名 ✅

#### 目录结构设计

**最终方案** (双重保存 + 分类清晰):

```bash
# 系统级记忆 (Claude读取)
.claude/skills/agent-memory/memories/
├── context-snapshots/              # 上下文快照
│   ├── 2025-01-12-session-1.md
│   ├── 2025-01-12-pre-compact-1.md
│   └── 2025-01-12-auto-1.md
├── decisions/                      # 决策记录
│   └── 2025-01-12-anti-cheat-decisions.md
└── daily-summaries/                # 每日总结
    └── 2025-01-12-summary.md

# 项目级记忆 (人类查阅)
development/memories/
├── context-snapshots/              # 上下文快照副本
│   ├── 2025-01-12-session-1.md
│   └── 2025-01-12-pre-compact-1.md
├── design-decisions/               # 设计决策
│   └── 2025-01-12-anti-cheat-system.md
└── project-notes/                  # 项目笔记
    └── ranking-system-notes.md
```

#### 命名规则

**规则1: 触发方式前缀**
```bash
# 手动触发
{YYYY-MM-DD}-session-{序号}.md
示例: 2025-01-12-session-1.md

# PreCompact触发
{YYYY-MM-DD}-pre-compact-{序号}.md
示例: 2025-01-12-pre-compact-1.md

# PostToolUse自动触发
{YYYY-MM-DD}-auto-{序号}.md
示例: 2025-01-12-auto-1.md
```

**规则2: 带描述的命名 (可选)**
```bash
# 用户提供--message参数时
{YYYY-MM-DD}-{简短描述}-session-{序号}.md
示例: 2025-01-12-anti-cheat-completed-session-1.md
```

**规则3: 决策记录命名**
```bash
# 系统级
{YYYY-MM-DD}-{模块名}-decisions.md
示例: 2025-01-12-anti-cheat-decisions.md

# 项目级
{YYYY-MM-DD}-{模块名}-system.md
示例: 2025-01-12-anti-cheat-system.md
```

#### 同一天多次保存处理

**问题**: 同一天可能保存多次,如何区分?

**解决方案**: 序号自动递增
```javascript
function generateSnapshotFileName(type, message) {
  const date = new Date().toISOString().split('T')[0];
  const existing = listSnapshotsByDate(date);
  const nextSeq = existing.length + 1;

  if (message) {
    // 用户自定义描述
    const shortMsg = message.substring(0, 30).replace(/\s+/g, '-');
    return `${date}-${shortMsg}-${type}-${nextSeq}.md`;
  } else {
    // 默认命名
    return `${date}-${type}-${nextSeq}.md`;
  }
}
```

**示例**:
```bash
# 同一天的不同快照
2025-01-12-session-1.md        # 10:30 手动保存
2025-01-12-auto-1.md           # 14:20 问题确认后自动保存
2025-01-12-pre-compact-1.md    # 16:45 压缩前保存
2025-01-12-session-2.md        # 18:00 手动保存
```

#### 重复检测与覆盖策略

**场景**: 连续两次内容几乎相同,是否需要都保存?

**策略**: 内容哈希去重
```javascript
const contentHash = calculateHash(snapshotContent);
const lastSnapshot = getLastSnapshot();

if (lastSnapshot && lastSnapshot.hash === contentHash) {
  const timeDiff = Date.now() - lastSnapshot.timestamp;
  if (timeDiff < 30 * 60 * 1000) { // 30分钟内
    // 跳过保存,避免重复
    log('内容未变化,跳过保存');
    return;
  }
}

// 内容有变化或时间间隔足够长,正常保存
saveSnapshot(snapshotContent);
```

#### 快照生命周期管理

**保留策略**:
```javascript
// 每日最多保留5个快照
const maxPerDay = 5;

// 超过30天的快照归档到archive/
const archiveAfterDays = 30;

// 自动清理: 每天运行一次
function cleanupOldSnapshots() {
  const snapshots = listAllSnapshots();

  // 1. 每日快照数量控制
  const byDate = groupByDate(snapshots);
  for (const [date, snaps] of Object.entries(byDate)) {
    if (snaps.length > maxPerDay) {
      // 保留最重要的,归档其余
      const toArchive = snaps.slice(maxPerDay);
      archiveSnapshots(toArchive);
    }
  }

  // 2. 超期快照归档
  const oldSnapshots = snapshots.filter(s =>
    s.age > archiveAfterDays && !s.isImportant
  );
  archiveSnapshots(oldSnapshots);
}
```

**重要快照标记**:
```markdown
---
tags: [context-snapshot, important]
keep_forever: true
reason: "完成反作弊系统全部8个问题讨论"
---
```

#### 决策记录的组织方式

**决策记录 vs 上下文快照的区别**:

| 维度 | 上下文快照 | 决策记录 |
|------|-----------|---------|
| 触发 | PreCompact / 手动 / 自动 | 问题确认后 |
| 内容 | 完整上下文状态 | 仅提取的决策要点 |
| 大小 | 较大 (~10-50KB) | 较小 (~2-10KB) |
| 频率 | 关键节点保存 | 每次问题确认 |
| 用途 | 恢复上下文 | 快速查阅决策 |

**决策记录的自动提取**:
```javascript
function extractDecisions(context) {
  const decisions = [];

  // 1. 扫描questions.md中的新确认项
  const newConfirmed = scanNewConfirmedItems();

  // 2. 提取会话中的决策关键词
  const decisionKeywords = [
    '决定', '确认', '采用', '选择',
    '方案', '最终', '确定'
  ];
  const sentences = extractSentencesWithKeywords(context, decisionKeywords);

  // 3. 汇总并格式化
  for (const item of newConfirmed) {
    decisions.push({
      question: item.question,
      answer: item.answer,
      timestamp: item.timestamp
    });
  }

  return formatDecisionsDocument(decisions);
}
```

**决策记录文件内容**:
```markdown
---
summary: "反作弊系统设计决策"
created: 2025-01-12
module: "anti-cheat-system"
questions_count: 8
tags: [decisions, anti-cheat]
---

# 反作弊系统设计决策

## 决策1: 善意度初始值
- **时间**: 2025-01-12 10:15
- **决策**: 100分,新用户默认信任
- **理由**: 降低新用户门槛,提升参与度

## 决策2: 作弊检测算法
- **时间**: 2025-01-12 11:30
- **决策**: 基于评分模式分析
- **细节**:
  - 突然大量评分
  - 评分过于一致
  - 异常时间段评分

## 决策3: 处理策略
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

#### 快速检索机制

**场景**: 人类如何快速找到某个决策?

**方案1: 时间线索引**
```markdown
# development/memories/decisions-index.md

## 2025-01-12
- [反作弊系统](decisions/2025-01-12-anti-cheat-system.md) - 8个决策
- [排名系统](decisions/2025-01-12-ranking-system.md) - 3个决策

## 2025-01-11
- [经济系统](decisions/2025-01-11-economy-system.md) - 2个决策
```

**方案2: 标签检索**
```bash
# 查找所有关于"排名"的决策
grep -l "排名" development/memories/design-decisions/*.md

# 查找最近的10个决策
ls -t development/memories/design-decisions/*.md | head -10
```

**状态**: ✅ 已完成设计

---

### 问题4: memory-agent职责边界 ✅

#### 最终职责定义

**✅ 负责的功能**:

1. **上下文快照生成**
   - 读取必要数据(questions.md, claude.md, daily-summary)
   - 生成结构化快照文档
   - 保存到双重位置(agent-memory + development/memories)

2. **决策记录提取**
   - 扫描新确认的问题
   - 提取决策要点
   - 生成决策记录文档

3. **重复检测**
   - 内容哈希计算
   - 30分钟内重复跳过
   - 记录检测日志

4. **数量控制** ⭐ 用户确认
   - 每日快照最多5个
   - **超出时直接归档最旧的快照**
   - 不询问用户,自动执行

**❌ 不负责的功能**:

1. **上下文恢复** → SessionStart Hook负责
2. **定期归档清理** → 清理agent负责 (未来)
3. **数据压缩** → 不需要(纯文本已足够小)
4. **快照搜索索引** → 独立工具或手动处理

#### 协作接口

**输入接口** (被调用):
```javascript
memoryAgent.generateSnapshot({
  mode: 'full' | 'decisions',
  trigger: 'pre-compact' | 'question-confirmed' | 'manual',
  message: '用户自定义备注'
});
```

**输出接口** (返回结果):
```javascript
{
  success: true,
  snapshot_file: '2025-01-12-session-1.md',
  size: '45KB',
  saved_locations: [
    '.claude/skills/agent-memory/memories/context-snapshots/',
    'development/memories/context-snapshots/'
  ],
  timestamp: '2025-01-12 14:30:22'
}
```

**数量控制实现** (用户确认的策略):
```javascript
function controlSnapshotCount(newSnapshot) {
  const todaySnapshots = listSnapshotsByDate(today);
  const maxPerDay = 5;

  if (todaySnapshots.length >= maxPerDay) {
    // 找到最旧的快照
    const oldestSnapshot = todaySnapshots.sort((a, b) =>
      a.timestamp - b.timestamp
    )[0];

    // 直接归档,不询问用户
    archiveSnapshot(oldestSnapshot);
    log(`已归档最旧快照: ${oldestSnapshot.file}`);
  }

  // 保存新快照
  saveSnapshot(newSnapshot);
}
```

#### 与其他组件的边界

**与SessionStart Hook**:
```
memory-agent: 保存快照
SessionStart Hook: 恢复快照
```

**与清理agent** (未来):
```
memory-agent: 实时数量控制(每日最多5个)
清理agent: 定期归档(>30天)和深度清理
```

**状态**: ✅ 已完成设计

---

### 问题5: SessionStart Hook增强 ✅

#### 功能设计

**核心目标**: 会话开始时自动发现并提示恢复最近的上下文

**触发时机**: 每次会话开始(SessionStart Hook)

#### 执行流程

```
会话开始
  ↓
SessionStart Hook触发
  ↓
检查最近的context-snapshot
  ↓
找到且<24小时?
  ├─ YES → 显示摘要 → 询问是否恢复
  │   ├─ 用户选择Y → 读取并展示完整快照
  │   └─ 用户选择N → 继续正常启动
  └─ NO → 继续正常启动
```

#### 快照查找逻辑

**查找策略**:
```javascript
function findRecentSnapshot() {
  const snapshots = listAllSnapshots();
  const now = Date.now();
  const twentyFourHoursAgo = now - 24 * 60 * 60 * 1000;

  // 按时间倒序排序
  snapshots.sort((a, b) => b.timestamp - a.timestamp);

  // 找到最近的快照
  const recent = snapshots.find(s =>
    s.timestamp > twentyFourHoursAgo
  );

  return recent;
}
```

#### 摘要显示格式

**快照摘要** (从frontmatter提取):
```markdown
💡 发现最近的上下文快照

📅 时间: 2小时前 (2025-01-12 14:30)
📊 进度: 96/149 (64%)
🎯 当前讨论: 反作弊系统 (3/8问题已确认)

是否恢复完整上下文? [Y/n]
```

**前端matter格式**:
```yaml
---
summary: "上下文快照 - 压缩前自动保存"
created: 2025-01-12
trigger: pre-compact
usage_rate: 92
mode: full
confirmed_questions: 96
total_questions: 149
current_topic: "反作弊系统"
---
```

#### 用户交互设计

**场景1: 用户选择Y (恢复)**
```markdown
正在加载上下文快照...

━━━━━━━━━━━━━━━━

# 上下文快照 - 2025-01-12 14:30

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

## 🎯 当前状态

**正在讨论**: 反作弊系统

**已确认决策**:
- 善意度初始值: 100分
- 检测算法: 基于评分模式
- 处理策略: 分阶段处理

**待确认问题**:
- 排名系统: 15个问题
- 推荐位机制: 5个问题

━━━━━━━━━━━━━━━━

✅ 上下文已恢复,可以继续工作
```

**场景2: 用户选择N (不恢复)**
```markdown
ℹ️ 已跳过上下文恢复

提示: 如需手动恢复,运行:
/save-context --list

━━━━━━━━━━━━━━━━

🎯 惊蛰计划 v1.20
正常会话启动...
```

**场景3: 无最近快照**
```markdown
ℹ️ 未找到最近24小时的上下文快照

提示: 会话中重要节点会自动保存快照,
      或手动运行: /save-context

━━━━━━━━━━━━━━━━

🎯 惊蛰计划 v1.20
正常会话启动...
```

#### 实现细节

**SessionStart Hook文件**:
```markdown
# .claude/hooks/session-start/load-context.md

---
name: load-context
description: 会话开始时检查并提示恢复最近的上下文快照
version: 1.0
---

## 功能

检查最近24小时内的context-snapshot,如果存在则显示摘要并询问用户是否恢复。

## 执行逻辑

```javascript
// 1. 查找最近快照
const snapshot = findRecentSnapshot();

if (!snapshot) {
  // 无快照,正常启动
  return;
}

// 2. 显示摘要
const summary = extractSummary(snapshot);
display(`
💡 发现最近的上下文快照

📅 时间: ${timeAgo(snapshot.timestamp)}
📊 进度: ${snapshot.confirmed}/${snapshot.total} (${snapshot.percentage}%)
🎯 当前讨论: ${snapshot.current_topic}

是否恢复完整上下文? [Y/n]
`);

// 3. 等待用户输入
const choice = awaitUserInput();

if (choice === 'Y' || choice === 'y') {
  // 4. 读取完整快照
  const content = readFile(snapshot.path);

  // 5. 显示给用户
  display(content);

  log(`已恢复上下文快照: ${snapshot.file}`);
} else {
  log(`用户选择不恢复上下文`);
}
```

## 配置选项

```json
{
  "loadContext": {
    "enabled": true,
    "maxAge": 24,
    "autoLoad": false,
    "showSummary": true
  }
}
```

## 注意事项

- 快照文件大小限制: <100KB
- 如果快照过大,只显示摘要部分
- 用户可以随时跳过恢复
```

#### 智能恢复策略

**策略1: 时间窗口**
- **<24小时**: 提示恢复
- **24-72小时**: 显示摘要但不提示
- **>72小时**: 不显示

**策略2: 内容相关性** (高级)
- 分析快照主题与用户首次输入的相关性
- 相关度高则优先推荐

**策略3: 多快照选择** (未来)
```markdown
发现3个最近的上下文快照:

1. [2小时前] 反作弊系统讨论 (64%)
2. [昨天] 排名系统设计 (62%)
3. [3天前] 经济系统确认 (60%)

选择要恢复的快照 [1-3/N]:
```

#### 错误处理

**快照文件损坏**:
```markdown
⚠️ 快照文件损坏,无法恢复

文件: 2025-01-12-session-1.md

建议:
- 检查文件完整性
- 尝试恢复更早的快照

继续正常启动...
```

**快照过大**:
```markdown
⚠️ 快照文件较大 (150KB)

只显示摘要部分:
- 进度: 96/149 (64%)
- 当前: 反作弊系统

完整内容请手动查看:
development/memories/context-snapshots/2025-01-12-session-1.md
```

**状态**: ✅ 已完成设计

---

## 📁 待创建的文件

### 1. PostToolUse Hook
- 路径: `.claude/hooks/post-tool-use/context-monitor.md`
- 状态: 设计完成,待实现

### 2. memory-agent
- 路径: `.claude/agents/memory-agent.md`
- 状态: 设计中,待完成问题2-5讨论

### 3. SessionStart Hook增强
- 路径: `.claude/hooks/session-start/load-context.md`
- 状态: 设计中,待完成问题2-5讨论

### 4. /save-context命令 (可选)
- 路径: `.claude/commands/save-context.md`
- 用途: 手动强制保存上下文快照
- 状态: 可选,根据需求决定

---

## 💡 关键决策记录

### 决策1: 使用/context命令监控
- **时间**: 2025-01-12
- **理由**: /context是系统内置命令,返回可靠的使用率数据
- **影响**: 确定了技术实现路线
- **状态**: ✅ 已确认

### 决策2: 三级阈值机制
- **时间**: 2025-01-12
- **阈值**: 80%提醒 / 99%决策 / PreCompact快照
- **理由**: 渐进式处理,避免过度记录
- **状态**: ✅ 已确认
- **更新**: v1.2调整阈值为80%/99%

---

## 🎉 设计完成总结

### 已解决的问题

✅ **问题1**: 触发时机选择
- 采用PreCompact Hook作为主要触发器(系统级,100%可靠)
- PostToolUse Hook作为辅助触发器(80%提醒,99%记录决策)
- 手动触发(/save-context命令)作为补充

✅ **问题2**: 每日总结读取范围
- 读取最近3个summary,但不超过7天
- daily-summary和context-snapshot都需要,各司其职

✅ **问题3**: 文件结构和命名
- 双重保存机制(agent-memory + development/memories)
- 触发方式前缀命名(session-1, pre-compact-1, auto-1)
- 序号自动递增处理同一天多次保存

✅ **问题4**: memory-agent职责边界
- 负责:快照生成、决策提取、重复检测、数量控制
- 不负责:上下文恢复、定期归档、数据压缩
- 数量控制策略:超出5个时直接归档最旧的

✅ **问题5**: SessionStart Hook增强
- 检查最近24小时快照
- 显示摘要并询问是否恢复
- 智能恢复策略(时间窗口、内容相关性)

### 核心设计决策

**决策1: 三层触发机制**
```
P0: PreCompact Hook (系统级,完整快照)
P1: PostToolUse Hook (80-98%提醒, ≥99%决策)
P2: 手动触发 (/save-context)
```

**决策2: 双重保存策略**
```
系统级记忆 (.claude/skills/agent-memory/) → Claude读取
项目级记忆 (development/memories/) → 人类查阅
```

**决策3: 分级处理机制**
```
<80%: 无操作
80-98%: 显示友好提醒
≥99%: 记录决策
PreCompact: 完整快照
```

**决策4: 重复避免策略**
```
内容哈希去重
30分钟内重复跳过
每日最多5个快照,超出归档最旧的
```

### 架构总览

```
上下文监控系统架构

┌─────────────────────────────────────────┐
│         触发层 (Triggers)              │
├─────────────────────────────────────────┤
│ • PreCompact Hook (P0, 系统级)        │
│ • PostToolUse Hook (P1, 监控)         │
│ • /save-context命令 (P2, 手动)        │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│      处理层 (Memory-Agent)             │
├─────────────────────────────────────────┤
│ • 读取数据 (questions.md, claude.md)  │
│ • 生成快照 (full/decisions模式)       │
│ • 重复检测 (内容哈希)                 │
│ • 数量控制 (每日最多5个)              │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│      存储层 (Storage)                  │
├─────────────────────────────────────────┤
│ 系统级: .claude/skills/agent-memory/   │
│   ├─ context-snapshots/                │
│   ├─ decisions/                        │
│   └─ daily-summaries/                  │
│                                         │
│ 项目级: development/memories/          │
│   ├─ context-snapshots/                │
│   ├─ design-decisions/                 │
│   └─ project-notes/                    │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│      恢复层 (Restore)                  │
├─────────────────────────────────────────┤
│ • SessionStart Hook                    │
│ • 检查最近快照(<24小时)               │
│ • 显示摘要并询问用户                   │
│ • 加载完整快照内容                     │
└─────────────────────────────────────────┘
```

### 待创建的文件清单

#### Hook文件 (3个)

1. **.claude/hooks/pre-compact-context-save.md** ✅ 已创建
   - PreCompact Hook实现
   - 完整快照生成

2. **.claude/hooks/auto-context-snapshot.md** ✅ 已创建(v1.1)
   - PostToolUse Hook实现
   - 上下文监控和提醒

3. **.claude/hooks/session-start/load-context.md** ⏳ 待创建
   - SessionStart Hook增强
   - 上下文恢复功能

#### Agent文件 (1个)

4. **.claude/agents/memory-agent.md** ⏳ 待创建
   - 核心agent实现
   - 快照生成逻辑
   - 决策提取逻辑

#### 命令文件 (1个)

5. **.claude/commands/save-context.md** ✅ 已创建
   - 手动触发命令
   - full/decisions模式

### 实现优先级

**阶段1: 核心功能** (必须实现)
- [ ] memory-agent基础实现
- [ ] PreCompact Hook集成
- [ ] 基本快照生成和保存

**阶段2: 增强功能** (建议实现)
- [ ] PostToolUse Hook监控
- [ ] 重复检测和数量控制
- [ ] SessionStart Hook恢复

**阶段3: 高级功能** (可选)
- [ ] 智能快照检索
- [ ] 多快照选择恢复
- [ ] 快照内容分析

### 配置文件示例

```json
{
  "contextManagement": {
    "enabled": true,
    "triggers": {
      "preCompact": {
        "enabled": true,
        "mode": "full"
      },
      "postToolUse": {
        "enabled": true,
        "warningThreshold": 80,
        "decisionThreshold": 99,
        "snapshotThreshold": 85,
        "checkInterval": 60
      },
      "manual": {
        "enabled": true,
        "command": "/save-context"
      }
    },
    "storage": {
      "maxPerDay": 5,
      "archiveAfterDays": 30,
      "duplicateThresholdMinutes": 30,
      "maxSnapshotSizeKB": 100
    },
    "restore": {
      "maxAgeHours": 24,
      "autoLoad": false,
      "showSummary": true
    }
  }
}
```

### 监控指标

```javascript
{
  "contextMonitor": {
    "snapshots": {
      "total": 50,
      "thisWeek": 12,
      "thisMonth": 45,
      "averageSize": "45KB",
      "successRate": 0.98
    },
    "triggers": {
      "preCompact": 25,
      "postToolUse": 15,
      "manual": 10
    },
    "decisions": {
      "total": 30,
      "averageSize": "8KB"
    }
  }
}
```

### 下一步行动

1. ⏳ **创建memory-agent实现文件**
2. ⏳ **创建SessionStart Hook文件**
3. ⏳ **编写集成测试**
4. ⏳ **更新文档和CHANGELOG**

---

**设计状态**: ✅ 全部完成
**创建时间**: 2025-01-12
**完成时间**: 2025-01-12
**参与者**: 老黑(Claude) + 蜡烛先生
**版本**: v1.0

---

## 📁 项目结构重组 (2025-01-12)

### 重组完成

已实施完整的项目文件结构重组,解决了以下问题:

**问题1**: "新建文件夹"堆积杂物
- ✅ 创建 `input/` 作为临时输入区
- ✅ 创建 `resources/` 作为资料物料库
- ✅ 已将所有资料归档完成

**问题2**: 文档组织结构不清晰
- ✅ `development/` 重组为5大分区: active/memories/logs/workspace/archive
- ✅ 创建 `development/memories/` 作为项目记忆库
- ✅ 重组沟通记录: 惊蛰计划在 `development/logs/communications/`, 其他在 `communications/`

### 新的项目结构

```bash
Claude/
├── input/                    # 临时输入区 ⭐ 新增
│   ├── pending/              # 你放这里
│   ├── processing/           # AI处理中
│   └── archived/             # 已归档
│
├── resources/                # 资料物料库 ⭐ 新增
│   ├── research/
│   │   └── ranking-systems/  # 排名系统研究
│   ├── references/
│   ├── tools/
│   └── assets/
│
├── development/              # 重组后的开发文档
│   ├── active/               # 活跃项目
│   │   ├── issues/           # 问题清单
│   │   ├── planning/         # 计划文档
│   │   └── tracking/         # 进度追踪
│   ├── memories/             # 项目记忆库 ⭐ 新增
│   │   ├── context-snapshots/
│   │   ├── design-decisions/
│   │   └── project-notes/
│   ├── logs/                 # 工作日志
│   │   ├── communications/   # 惊蛰计划沟通 ⭐ 重组
│   │   ├── workflow/
│   │   └── context-monitor/
│   ├── workspace/            # 临时工作区 ⭐ 新增
│   └── archive/              # 归档区 ⭐ 新增
│
└── communications/           # 通用沟通 (非惊蛰计划)
```

### 记忆存储策略

**系统级记忆** (agent-memory):
- 位置: `.claude/skills/agent-memory/memories/`
- 用途: Claude AI的系统级记忆
- 存储: 上下文快照、每日总结、重要决策

**项目级记忆** (development/memories):
- 位置: `development/memories/`
- 用途: 人类可读的项目文档
- 存储: 设计决策、项目笔记、上下文快照副本

### 工作流程改进

**资料收集新流程**:
```
你找到资料 → input/pending/
    ↓
AI定期检查 → 分类归档到 resources/
    ↓
记录到 input/archived/
```

**沟通记录新流程**:
```
惊蛰计划相关 → development/logs/communications/
通用沟通 → communications/
```

### 已归档内容

**从"新建文件夹"归档**:
- ✅ 9个排名系统方案文档 → `resources/research/ranking-systems/`
- ✅ docx工具文档 → `resources/tools/docx/`
- ✅ 工作流改动总结 → `development/logs/workflow/`

**development文件夹重组**:
- ✅ 20+子文件夹重组为5大分区
- ✅ 创建清晰的记忆库系统
- ✅ 建立归档机制

---

---

## 📝 备注

**用户要求**: "你先等会儿,这块儿你先记录一下"

**暂停原因**: 用户可能需要思考或处理其他事务

**恢复提示**: 等待用户指示继续讨论问题2-5

---

**版本**: v1.0
**创建时间**: 2025-01-12
**状态**: in-progress
**下一步**: 继续讨论问题2-5
