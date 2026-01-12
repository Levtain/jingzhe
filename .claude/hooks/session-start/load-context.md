---
name: load-context
description: 会话开始时检查并提示恢复最近的上下文快照
version: 1.0
trigger: session-start
timeout: 5000
---

# SessionStart Hook - 上下文恢复

## 功能说明

会话开始时自动检查最近24小时内的context-snapshot,如果存在则显示摘要并询问用户是否恢复。

---

## 执行流程

```
会话开始
  ↓
SessionStart Hook触发
  ↓
查找最近的context-snapshot (<24小时)
  ↓
找到?
  ├─ YES → 显示摘要 → 询问是否恢复
  │   ├─ 用户输入Y → 读取并展示完整快照
  │   └─ 用户输入N → 继续正常启动
  └─ NO → 继续正常启动
```

---

## 实现代码

### 主流程

```javascript
async function sessionStartHook() {
  try {
    // 1. 查找最近快照
    const snapshot = await findRecentSnapshot(24); // 24小时内

    if (!snapshot) {
      // 无快照,正常启动
      log('未找到最近24小时的上下文快照');
      return;
    }

    // 2. 显示摘要
    const summary = extractSummary(snapshot);
    displaySnapshotSummary(summary);

    // 3. 等待用户输入
    const choice = await waitForUserInput('是否恢复完整上下文? [Y/n]: ', 10000);

    if (choice === 'Y' || choice === 'y' || choice === '') {
      // 用户选择恢复
      await loadFullSnapshot(snapshot);
    } else {
      // 用户选择不恢复
      log('用户选择不恢复上下文');
    }

  } catch (error) {
    // 错误不影响正常启动
    logError(`SessionStart Hook error: ${error.message}`);
  }
}
```

### 查找最近快照

```javascript
async function findRecentSnapshot(maxAgeHours) {
  const snapshotDir = '.claude/skills/agent-memory/memories/context-snapshots/';
  const files = await glob(snapshotDir + '*.md');

  // 按时间倒序排序
  const snapshots = files
    .map(file => ({
      path: file.path,
      filename: file.name,
      timestamp: file.mtime,
      size: file.size
    }))
    .sort((a, b) => b.timestamp - a.timestamp);

  // 找到最近的快照
  const now = Date.now();
  const maxAge = maxAgeHours * 60 * 60 * 1000;

  const recent = snapshots.find(s =>
    (now - s.timestamp) < maxAge && s.size < 100 * 1024 // 小于100KB
  );

  return recent || null;
}
```

### 提取快照摘要

```javascript
function extractSummary(snapshot) {
  const content = readFile(snapshot.path);
  const frontmatter = parseFrontmatter(content);

  return {
    timeAgo: formatTimeAgo(snapshot.timestamp),
    exactTime: new Date(snapshot.timestamp).toLocaleString('zh-CN'),
    confirmed: frontmatter.confirmed_questions || 0,
    total: frontmatter.total_questions || 0,
    percentage: frontmatter.confirmed_questions && frontmatter.total_questions
      ? Math.round((frontmatter.confirmed_questions / frontmatter.total_questions) * 100)
      : 0,
    currentTopic: frontmatter.current_topic || '未知',
    trigger: frontmatter.trigger || 'unknown',
    size: formatBytes(snapshot.size),
    filename: snapshot.filename
  };
}
```

### 显示摘要

```javascript
function displaySnapshotSummary(summary) {
  const output = `
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 发现最近的上下文快照
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 时间: ${summary.timeAgo} (${summary.exactTime})
📊 进度: ${summary.confirmed}/${summary.total} (${summary.percentage}%)
🎯 当前讨论: ${summary.currentTopic}
📦 大小: ${summary.size}

是否恢复完整上下文? [Y/n]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`;

  display(output);
}
```

### 加载完整快照

```javascript
async function loadFullSnapshot(snapshot) {
  display('\n正在加载上下文快照...\n');

  const content = readFile(snapshot.path);
  const divider = '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━';

  display(`${divider}\n`);
  display(content);
  display(`${divider}\n`);

  display('✅ 上下文已恢复,可以继续工作\n');

  log(`已恢复上下文快照: ${snapshot.filename}`);
}
```

---

## 用户交互场景

### 场景1: 用户选择Y (恢复)

```markdown
💡 发现最近的上下文快照
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 时间: 2小时前 (2025-01-12 14:30)
📊 进度: 96/149 (64%)
🎯 当前讨论: 反作弊系统
📦 大小: 45KB

是否恢复完整上下文? [Y/n]: Y

正在加载上下文快照...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 上下文快照 - 2025-01-12 14:30

> ⚠️ 系统即将压缩上下文,已自动保存当前状态

## 📊 进度概览

**问题确认**: 96/149 (64%)
**当前阶段**: 设计讨论
**上下文使用率**: 92%

...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ 上下文已恢复,可以继续工作
```

### 场景2: 用户选择N (不恢复)

```markdown
💡 发现最近的上下文快照
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 时间: 2小时前 (2025-01-12 14:30)
📊 进度: 96/149 (64%)

是否恢复完整上下文? [Y/n]: n

ℹ️ 已跳过上下文恢复

提示: 如需手动恢复,运行: /save-context --list
```

### 场景3: 无最近快照

```markdown
ℹ️ 未找到最近24小时的上下文快照

提示: 会话中重要节点会自动保存快照,
      或手动运行: /save-context
```

---

## 配置选项

```json
{
  "loadContext": {
    "enabled": true,
    "maxAgeHours": 24,
    "maxSnapshotSizeKB": 100,
    "autoLoad": false,
    "showSummary": true,
    "inputTimeout": 10000,
    "snapshotPath": ".claude/skills/agent-memory/memories/context-snapshots/"
  }
}
```

**配置说明**:
- `enabled`: 是否启用上下文恢复功能
- `maxAgeHours`: 快照最大年龄(小时)
- `maxSnapshotSizeKB`: 快照最大大小(KB),超过则只显示摘要
- `autoLoad`: 是否自动加载(不询问用户)
- `showSummary`: 是否显示摘要
- `inputTimeout`: 等待用户输入的超时时间(毫秒)

---

## 辅助函数

### 时间格式化

```javascript
function formatTimeAgo(timestamp) {
  const now = Date.now();
  const diff = now - timestamp;

  const minutes = Math.floor(diff / 1000 / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (days > 0) {
    return `${days}天前`;
  } else if (hours > 0) {
    return `${hours}小时前`;
  } else if (minutes > 0) {
    return `${minutes}分钟前`;
  } else {
    return '刚刚';
  }
}
```

### 字节格式化

```javascript
function formatBytes(bytes) {
  if (bytes < 1024) return bytes + 'B';
  if (bytes < 1024 * 1024) return Math.round(bytes / 1024) + 'KB';
  return Math.round(bytes / 1024 / 1024) + 'MB';
}
```

### 等待用户输入

```javascript
async function waitForUserInput(prompt, timeout) {
  return new Promise((resolve) => {
    const timer = setTimeout(() => {
      // 超时,默认选择不恢复
      resolve('n');
    }, timeout);

    // 监听用户输入
    waitForInput(prompt).then(input => {
      clearTimeout(timer);
      resolve(input.trim());
    });
  });
}
```

---

## 错误处理

### 快照文件损坏

```javascript
try {
  const content = readFile(snapshot.path);
} catch (error) {
  display(`⚠️ 快照文件损坏,无法恢复\n`);
  display(`文件: ${snapshot.filename}\n`);
  display(`建议:\n`);
  display(`- 检查文件完整性\n`);
  display(`- 尝试恢复更早的快照\n\n`);
  display(`继续正常启动...\n`);
}
```

### 快照过大

```javascript
if (snapshot.size > maxSnapshotSizeKB * 1024) {
  display(`⚠️ 快照文件较大 (${formatBytes(snapshot.size)})\n\n`);
  display(`只显示摘要部分:\n`);
  display(`- 进度: ${summary.confirmed}/${summary.total} (${summary.percentage}%)\n`);
  display(`- 当前: ${summary.currentTopic}\n\n`);
  display(`完整内容请手动查看:\n`);
  display(`${snapshot.path}\n\n`);
  return; // 不加载完整内容
}
```

### 解析失败

```javascript
try {
  const frontmatter = parseFrontmatter(content);
} catch (error) {
  log(`Frontmatter解析失败: ${error.message}`);
  // 使用默认值
  const summary = {
    timeAgo: formatTimeAgo(snapshot.timestamp),
    confirmed: 0,
    total: 0,
    percentage: 0,
    currentTopic: '未知'
  };
}
```

---

## 智能恢复策略 (未来扩展)

### 策略1: 时间窗口分级

```javascript
function getRestoreLevel(snapshot) {
  const age = Date.now() - snapshot.timestamp;
  const hours = age / 1000 / 60 / 60;

  if (hours < 2) {
    return 'prompt'; // 提示恢复
  } else if (hours < 24) {
    return 'summary'; // 只显示摘要
  } else {
    return 'ignore'; // 忽略
  }
}
```

### 策略2: 多快照选择

```javascript
async function showMultipleSnapshots() {
  const snapshots = await findRecentSnapshots(72, 3); // 72小时内最多3个

  display(`发现${snapshots.length}个最近的上下文快照:\n\n`);

  snapshots.forEach((s, i) => {
    const summary = extractSummary(s);
    display(`${i + 1}. [${summary.timeAgo}] ${summary.currentTopic} (${summary.percentage}%)\n`);
  });

  display(`\n选择要恢复的快照 [1-${snapshots.length}/N]: `);

  const choice = await waitForUserInput();
  // ...
}
```

### 策略3: 内容相关性分析

```javascript
function calculateRelevance(snapshot, userFirstMessage) {
  const keywords = extractKeywords(snapshot.content);
  const userKeywords = extractKeywords(userFirstMessage);

  const intersection = keywords.filter(k => userKeywords.includes(k));
  const relevance = intersection.length / Math.max(keywords.length, 1);

  return relevance;
}
```

---

## 日志记录

### 日志位置

```bash
development/logs/session-start/
└── 2025-01-12-session-start.log
```

### 日志格式

```
[2025-01-12 14:30:22] session_start - snapshot_found:2025-01-12-pre-compact-1.md, age:2小时
[2025-01-12 14:30:25] user_choice: Y
[2025-01-12 14:30:26] context_loaded: 2025-01-12-pre-compact-1.md, size:45KB

[2025-01-12 15:00:10] session_start - snapshot_not_found
[2025-01-12 16:00:15] session_start - snapshot_found, user_choice: N
```

---

## 性能优化

### 1. 缓存快照列表

```javascript
let snapshotCache = null;
let cacheTime = null;
const CACHE_TTL = 60 * 1000; // 1分钟

async function findRecentSnapshot(maxAgeHours) {
  if (!snapshotCache || (Date.now() - cacheTime) > CACHE_TTL) {
    snapshotCache = await loadSnapshotList();
    cacheTime = Date.now();
  }

  return findInCache(snapshotCache, maxAgeHours);
}
```

### 2. 延迟加载

```javascript
// 只在用户选择Y时才读取完整内容
async function sessionStartHook() {
  const snapshot = await findRecentSnapshot(24);
  if (snapshot) {
    const summary = extractSummary(snapshot); // 只读取frontmatter
    displaySnapshotSummary(summary);

    const choice = await waitForUserInput();
    if (choice === 'Y') {
      await loadFullSnapshot(snapshot); // 此时才读取完整内容
    }
  }
}
```

### 3. 异步非阻塞

```javascript
// Hook不应该阻塞会话启动
async function sessionStartHook() {
  // 设置超时保护
  const result = await Promise.race([
    executeRestoreFlow(),
    timeout(5000) // 5秒超时
  ]);

  if (result === 'timeout') {
    log('SessionStart Hook超时,跳过上下文恢复');
  }
}
```

---

## 测试检查清单

- [ ] 正常情况下能找到并显示快照
- [ ] 用户选择Y能正确加载完整内容
- [ ] 用户选择N能跳过恢复
- [ ] 无快照时不报错
- [ ] 快照文件损坏时不影响启动
- [ ] 快照过大时只显示摘要
- [ ] 超时后能正常启动
- [ ] 日志记录正确

---

## 集成说明

### Hook配置文件

确保在 `.claude/settings.json` 中配置:

```json
{
  "hooks": {
    "session-start": [
      {
        "file": ".claude/hooks/session-start/load-context.md",
        "enabled": true
      }
    ]
  }
}
```

### 依赖项

此Hook依赖以下组件:
- `memory-agent` - 用于生成快照
- `.claude/skills/agent-memory/memories/context-snapshots/` - 快照存储路径

---

## 故障排除

### 问题1: Hook不触发

**检查**:
1. `.claude/settings.json` 中是否正确配置
2. 文件路径是否正确
3. 文件格式是否符合要求

### 问题2: 找不到快照

**检查**:
1. 快照目录是否存在
2. 是否有快照文件
3. 快照时间戳是否正确

### 问题3: 解析frontmatter失败

**解决**:
- 使用默认值,不中断流程
- 记录错误日志
- 继续正常启动

---

**版本**: 1.0
**创建时间**: 2025-01-12
**作者**: Claude & User
**状态**: ✅ 实现完成
