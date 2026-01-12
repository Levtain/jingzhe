---
name: memory-agent
description: 上下文快照和决策记录的核心Agent,负责生成、保存和管理上下文记忆
version: 1.0
author: Claude & User
created: 2025-01-12
---

# Memory Agent - 上下文记忆管理Agent

## 核心职责

1. **上下文快照生成** - 读取并保存完整上下文状态
2. **决策记录提取** - 从确认的问题中提取决策要点
3. **重复检测** - 避免保存重复内容
4. **数量控制** - 每日最多5个快照,超出归档最旧的

## 调用接口

### 输入参数

```javascript
memoryAgent.generateSnapshot({
  mode: 'full' | 'decisions',      // 模式选择
  trigger: 'pre-compact' | 'question-confirmed' | 'manual',  // 触发方式
  message: '用户自定义备注',        // 可选
  force: false                     // 是否强制保存(忽略重复检测)
});
```

### 输出结果

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

---

## 实现细节

### 1. 文件命名规则

```javascript
function generateSnapshotFileName(type, message) {
  const date = new Date().toISOString().split('T')[0]; // YYYY-MM-DD
  const existing = listSnapshotsByDate(date);
  const nextSeq = existing.length + 1;

  if (message) {
    // 用户自定义描述
    const shortMsg = message
      .substring(0, 30)
      .replace(/\s+/g, '-')
      .replace(/[^a-zA-Z0-9\u4e00-\u9fa5-]/g, '');
    return `${date}-${shortMsg}-${type}-${nextSeq}.md`;
  } else {
    // 默认命名
    return `${date}-${type}-${nextSeq}.md`;
  }
}
```

**命名示例**:
```bash
2025-01-12-session-1.md           # 手动触发
2025-01-12-pre-compact-1.md       # PreCompact触发
2025-01-12-auto-1.md              # PostToolUse自动触发
2025-01-12-anti-cheat-session-2.md # 带描述的手动触发
```

### 2. 数据读取

```javascript
function readContextData() {
  const data = {
    // 1. 问题列表
    questions: readFile('development/active/issues/questions.md'),
    questions_stats: extractQuestionStats(),

    // 2. 项目进度
    claude_md: readFile('docs/product/claude.md'),
    claude_progress: extractClaudeProgress(),

    // 3. 最近工作总结
    daily_summaries: getRecentDailySummaries(3, 7), // 最近3个,但不超过7天

    // 4. 当前上下文
    current_time: new Date().toISOString(),
    usage_rate: getCurrentContextUsage(),
  };

  return data;
}
```

### 3. 快照生成 (Full Mode)

```javascript
function generateFullSnapshot(data, trigger, message) {
  const content = `---
summary: "上下文快照 - ${getTriggerLabel(trigger)}${message ? ': ' + message : ''}"
created: ${data.current_time.split('T')[0]}
trigger: ${trigger}
usage_rate: ${data.usage_rate}
mode: full
confirmed_questions: ${data.questions_stats.confirmed}
total_questions: ${data.questions_stats.total}
current_topic: "${data.questions_stats.current_topic || '未知'}"
---

# 上下文快照 - ${data.current_time.split('T')[0]}

> ⚠️ ${getTriggerDescription(trigger)}
> ${message ? '备注: ' + message : ''}

## 📊 进度概览

**问题确认**: ${data.questions_stats.confirmed}/${data.questions_stats.total} (${data.questions_stats.percentage}%)
**当前阶段**: ${data.claude_progress.stage || '设计中'}
**上下文使用率**: ${data.usage_rate}%

## 💬 最近工作总结

### 最近3日工作

${formatDailySummaries(data.daily_summaries)}

## 🎯 当前状态

**正在讨论**: ${data.questions_stats.current_topic || '无'}

**最近确认的决策**:
${formatRecentDecisions(data.questions_stats.recent_confirmed)}

**待确认问题**:
${formatPendingQuestions(data.questions_stats.pending)}

## 📁 相关文件

- 问题列表: \`development/active/issues/questions.md\`
- 项目文档: \`docs/product/claude.md\`
- 设计文档: \`docs/design/\`

---
**生成时间**: ${data.current_time}
**触发方式**: ${trigger}
**Agent版本**: memory-agent v1.0
`;

  return content;
}
```

### 4. 决策记录生成 (Decisions Mode)

```javascript
function generateDecisionsSnapshot(data, message) {
  // 1. 扫描新确认的问题
  const newConfirmed = scanNewConfirmedItems(data.questions);

  // 2. 提取决策要点
  const decisions = [];
  for (const item of newConfirmed) {
    decisions.push({
      question: item.question,
      answer: item.answer,
      timestamp: item.timestamp,
      category: item.category
    });
  }

  // 3. 如果没有新决策,返回null
  if (decisions.length === 0) {
    return null;
  }

  // 4. 生成文档
  const content = `---
summary: "决策记录 - ${newConfirmed.length}个新确认"
created: ${data.current_time.split('T')[0]}
trigger: question-confirmed
mode: decisions
questions_count: ${newConfirmed.length}
categories: ${[...new Set(decisions.map(d => d.category))].join(', ')}
tags: [decisions${decisions.length > 0 ? ', ' + decisions[0].category : ''}]
---

# 决策记录 - ${data.current_time.split('T')[0]}

## 📋 本次确认的决策

${decisions.map((d, i) => `
### 决策${i + 1}: ${d.question}
- **时间**: ${d.timestamp}
- **分类**: ${d.category}
- **决策**: ${d.answer}
`).join('\n')}

---
**记录时间**: ${data.current_time}
**相关问题**: ${newConfirmed.length}个
**Agent版本**: memory-agent v1.0
`;

  return content;
}
```

### 5. 重复检测

```javascript
function isDuplicate(content) {
  const contentHash = calculateHash(content); // SHA-256
  const lastSnapshot = getLastSnapshot();

  if (!lastSnapshot) {
    return { duplicate: false };
  }

  // 读取最后保存的快照
  const lastContent = readFile(lastSnapshot.path);
  const lastHash = calculateHash(lastContent);

  if (lastHash === contentHash) {
    const timeDiff = Date.now() - lastSnapshot.timestamp;
    if (timeDiff < 30 * 60 * 1000) { // 30分钟内
      return {
        duplicate: true,
        reason: '内容完全相同',
        timeSinceLast: Math.floor(timeDiff / 1000 / 60) + '分钟'
      };
    }
  }

  return { duplicate: false };
}
```

### 6. 数量控制

```javascript
function controlSnapshotCount(newSnapshot) {
  const today = new Date().toISOString().split('T')[0];
  const todaySnapshots = listSnapshotsByDate(today);
  const maxPerDay = 5;

  if (todaySnapshots.length >= maxPerDay) {
    // 找到最旧的快照
    const oldestSnapshot = todaySnapshots
      .sort((a, b) => a.timestamp - b.timestamp)[0];

    // 归档到archive/
    const archiveDir = 'development/memories/context-snapshots/archive/';
    const archivePath = archiveDir + oldestSnapshot.file;

    ensureDir(archiveDir);
    moveFile(oldestSnapshot.path, archivePath);

    log(`已归档最旧快照: ${oldestSnapshot.file} → ${archivePath}`);
  }

  // 保存新快照
  saveSnapshot(newSnapshot);
}
```

### 7. 双重保存机制

```javascript
function saveSnapshot(content, filename) {
  const paths = {
    system: `.claude/skills/agent-memory/memories/context-snapshots/${filename}`,
    project: `development/memories/context-snapshots/${filename}`
  };

  // 保存到系统级(供Claude读取)
  ensureDir(dirname(paths.system));
  writeFile(paths.system, content);

  // 保存到项目级(供人类查阅)
  ensureDir(dirname(paths.project));
  writeFile(paths.project, content);

  return {
    success: true,
    snapshot_file: filename,
    size: formatBytes(content.length),
    saved_locations: [
      dirname(paths.system),
      dirname(paths.project)
    ],
    timestamp: new Date().toISOString()
  };
}
```

---

## 主流程

```javascript
async function generateSnapshot(options) {
  const { mode, trigger, message, force = false } = options;

  try {
    // 1. 读取数据
    const data = readContextData();

    // 2. 生成内容
    let content;
    if (mode === 'full') {
      content = generateFullSnapshot(data, trigger, message);
    } else if (mode === 'decisions') {
      content = generateDecisionsSnapshot(data, message);

      // 如果没有新决策,跳过保存
      if (!content) {
        return {
          success: true,
          skipped: true,
          reason: '没有新确认的决策'
        };
      }
    }

    // 3. 重复检测(除非强制保存)
    if (!force) {
      const duplicateCheck = isDuplicate(content);
      if (duplicateCheck.duplicate) {
        return {
          success: true,
          skipped: true,
          reason: `重复快照: ${duplicateCheck.reason}, 距上次${duplicateCheck.timeSinceLast}`
        };
      }
    }

    // 4. 生成文件名
    const type = getTriggerType(trigger);
    const filename = generateSnapshotFileName(type, message);

    // 5. 数量控制
    if (mode === 'full') {
      controlSnapshotCount({ filename, content });
    } else {
      // decisions模式不限制数量
      saveSnapshot(content, filename);
    }

    // 6. 记录日志
    logAction({
      action: 'snapshot_created',
      mode,
      trigger,
      filename,
      size: content.length
    });

    return {
      success: true,
      snapshot_file: filename,
      mode,
      trigger
    };

  } catch (error) {
    logError(`Memory agent error: ${error.message}`);
    return {
      success: false,
      error: error.message
    };
  }
}
```

---

## 辅助函数

### 提取问题统计

```javascript
function extractQuestionStats() {
  const content = readFile('development/active/issues/questions.md');

  // 解析frontmatter
  const frontmatter = parseFrontmatter(content);

  // 扫描确认的问题
  const confirmed = (content.match(/\[x\]/g) || []).length;
  const total = (content.match(/\[[ x]\]/g) || []).length;
  const percentage = total > 0 ? Math.round((confirmed / total) * 100) : 0;

  // 提取当前主题
  const currentTopic = extractCurrentTopic(content);

  return {
    confirmed,
    total,
    percentage,
    current_topic: currentTopic,
    recent_confirmed: extractRecentConfirmed(content, 5),
    pending: extractPendingQuestions(content, 10)
  };
}
```

### 提取Claude进度

```javascript
function extractClaudeProgress() {
  const content = readFile('docs/product/claude.md');
  const frontmatter = parseFrontmatter(content);

  return {
    stage: frontmatter.stage || '设计中',
    completion: frontmatter.completion || 0,
    last_updated: frontmatter.last_updated
  };
}
```

### 获取最近Daily Summaries

```javascript
function getRecentDailySummaries(count, maxDays) {
  const summaries = [];
  const summaryDir = 'development/logs/daily-summary-*.md';
  const files = glob(summaryDir);

  // 按时间倒序
  files.sort((a, b) => b.mtime - a.mtime);

  const sevenDaysAgo = Date.now() - maxDays * 24 * 60 * 60 * 1000;

  for (const file of files) {
    if (summaries.length >= count) break;
    if (file.mtime < sevenDaysAgo) break;

    const content = readFile(file.path);
    summaries.push({
      date: file.date,
      content: extractSummaryContent(content)
    });
  }

  return summaries;
}
```

---

## 配置选项

```json
{
  "memoryAgent": {
    "enabled": true,
    "storage": {
      "maxPerDay": 5,
      "archiveAfterDays": 30,
      "duplicateThresholdMinutes": 30,
      "maxSnapshotSizeKB": 100
    },
    "paths": {
      "system": ".claude/skills/agent-memory/memories/",
      "project": "development/memories/"
    }
  }
}
```

---

## 使用示例

### 示例1: PreCompact触发(完整快照)

```bash
# 系统自动触发
memoryAgent.generateSnapshot({
  mode: 'full',
  trigger: 'pre-compact',
  message: null
});
```

### 示例2: 问题确认后(决策记录)

```bash
# Hook自动触发
memoryAgent.generateSnapshot({
  mode: 'decisions',
  trigger: 'question-confirmed',
  message: '反作弊系统8个问题确认'
});
```

### 示例3: 手动触发(带备注)

```bash
# 用户执行 /save-context --message "完成排名系统讨论"
memoryAgent.generateSnapshot({
  mode: 'full',
  trigger: 'manual',
  message: '完成排名系统讨论',
  force: false
});
```

---

## 错误处理

### 文件读取失败

```javascript
try {
  const questions = readFile('development/active/issues/questions.md');
} catch (error) {
  if (error.code === 'ENOENT') {
    // 文件不存在,使用默认值
    log('questions.md不存在,跳过问题统计');
    return { confirmed: 0, total: 0 };
  }
  throw error;
}
```

### 磁盘空间不足

```javascript
function checkDiskSpace(requiredBytes) {
  const freeSpace = getFreeDiskSpace();
  if (freeSpace < requiredBytes * 2) {
    throw new Error('磁盘空间不足,无法保存快照');
  }
}
```

---

## 日志记录

### 日志位置

```bash
development/logs/memory-agent/
├── 2025-01-12-memory-agent.log
└── memory-agent-stats.json
```

### 日志格式

```
[2025-01-12 14:30:22] snapshot_created - mode:full, trigger:pre-compact, file:2025-01-12-pre-compact-1.md, size:45KB
[2025-01-12 14:35:08] snapshot_skipped - reason:duplicate, timeSinceLast:8分钟
[2025-01-12 14:40:15] snapshot_created - mode:decisions, trigger:question-confirmed, file:2025-01-12-auto-1.md, size:8KB
```

---

## 测试检查清单

- [ ] 完整快照生成正确
- [ ] 决策记录提取准确
- [ ] 重复检测有效
- [ ] 数量控制正常工作
- [ ] 双重保存成功
- [ ] 错误处理覆盖完整
- [ ] 日志记录正确
- [ ] 文件命名符合规范
