# 惊蛰计划自动化工具开发仓库

> **创建时间**: 2025-01-06
> **用途**: 存放开发中的Command、Hook、Agent工具
> **流程**: 在此开发 → 测试 → 部署到.claude/

---

## 📂 文件夹说明

### development/automation-tools/

**开发工作区** - 所有新工具在此开发、测试、完善

```
development/automation-tools/
├── commands/          # 开发中的Command (.md文件)
├── hooks/             # 开发中的Hook (.json文件)
├── agents/            # 开发中的Agent (.md文件)
└── README.md          # 本文件
```

### .claude/

**生产部署区** - 测试通过后的工具部署到这里

```
.claude/
├── commands/          # 部署的Command
├── hooks/             # 部署的Hook
└── agents/            # 部署的Agent
```

---

## 🔄 开发到部署流程

### 1. 开发阶段

```
在 development/automation-tools/ 中创建工具
  ↓
编写功能代码
  ↓
本地测试(模拟运行)
  ↓
检查是否符合规范
```

### 2. 测试阶段

```
复制到 .claude/ 测试
  ↓
实际运行测试
  ↓
收集反馈
  ↓
修复问题
```

### 3. 部署阶段

```
确认功能正常
  ↓
保留开发版本在 development/automation-tools/
  ↓
生产版本在 .claude/
  ↓
更新开发清单,标注状态为"已部署"
```

---

## 📋 工具命名规范

### Command命名

- 格式: 小写，连字符分隔
- 示例: `discuss.md`, `sync-docs.md`, `check-progress.md`
- 调用: `/discuss`, `/sync-docs`, `/check-progress`

### Hook命名

- 格式: 小写，连字符分隔
- 示例: `post-tool-use.json`, `session-start.json`
- 触发: 系统自动触发

### Agent命名

- 格式: 小写，连字符分隔，以-agent结尾
- 示例: `doc-sync-agent.md`, `progress-summary-agent.md`
- 调用: Task tool或Command调用

---

## 📝 工具模板

### Command模板

```markdown
---
description: 简短描述(显示在/help中)
argument-hint: [参数说明]
allowed-tools: Read, Write, Edit (可选)
---

# 命令标题

使用此命令会自动执行以下操作:

1. 操作1
2. 操作2
3. 操作3

## 使用示例

/discuss [参数]

## 输出格式

(示例输出)

---
```

### Hook模板

```json
{
  "description": "Hook用途说明",
  "hooks": {
    "事件名": [
      {
        "matcher": "工具名|通配符",
        "hooks": [
          {
            "type": "prompt|command",
            "prompt": "LLM提示词" 或 "command": "bash命令",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

### Agent模板

```markdown
---
name: agent-name
description: Use this agent when... Examples: <example>...</example>
model: inherit
color: blue
tools: ["Read", "Write", "Grep"]
---

You are [agent role] specializing in [domain].

**Your Core Responsibilities:**
1. Responsibility 1
2. Responsibility 2

**Analysis Process:**
1. Step one
2. Step two

**Output Format:**
Provide results in this format: ...
```

---

## 🧪 测试检查清单

### Command测试

- [ ] 命令能正确执行
- [ ] 参数处理正确
- [ ] 输出格式清晰
- [ ] 错误提示友好
- [ ] 边界情况处理

### Hook测试

- [ ] 触发时机正确
- [ ] 执行时间<5秒
- [ ] 不影响主流程
- [ ] 异常处理得当
- [ ] 日志记录完整

### Agent测试

- [ ] 触发条件准确
- [ ] 分析逻辑正确
- [ ] 输出结构化
- [ ] 决策可追溯
- [ ] 边界情况处理

---

## 📊 开发进度追踪

参考主清单: [自动化工具开发清单_2025-01-06.md](../自动化工具开发清单_2025-01-06.md)

### 当前进度

- ✅ 开发清单已创建
- ✅ 文件夹结构已建立
- ⏳ 优先级1工具开发中
- ⏳ 优先级2工具待开发
- ⏳ 优先级3工具待开发

---

## 🔧 开发工具和资源

### 已安装的Skill

- **command-development**: 命令开发指南
- **hook-development**: Hook开发指南
- **agent-identifier**: Agent开发指南

### 参考文档

- **开发清单**: `development/自动化工具开发清单_2025-01-06.md`
- **Command Skill**: `.claude/skills/command-development/command-development/SKILL.md`
- **Hook Skill**: `.claude/skills/hook-development/hook-development/SKILL.md`
- **Agent Skill**: `.claude/skills/agent-identifier/agent-identifier/SKILL.md`

---

## 📞 开发支持

开发过程中遇到问题时:

1. 查看对应的Skill文档
2. 参考开发清单中的示例
3. 查看已有工具的实现
4. 咨询蜡烛先生确认需求

---

**仓库创建时间**: 2025-01-06
**最后更新**: 2025-01-06
**维护人**: 老黑(Claude)
