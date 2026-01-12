# 已安装Skill总览

> **快速了解所有可用的Skill及其功能**
> **更新时间**: 2025-01-11

---

## 📚 Skill清单

### 🎯 核心文档Skill（最重要）

#### 1. docs-write - 文档撰写 ⭐⭐⭐

**功能**: 按照Metabase风格指南撰写文档

**何时使用**:
- ✏️ 编写新文档（.md文件）
- ✏️ 更新现有文档
- ✏️ 编辑文档内容

**特点**:
- 对话式风格
- 用户友好
- 清晰易懂

**强制使用**: 是（PreToolUse Hook强制检查）

---

#### 2. docs-review - 文档审核 ⭐⭐⭐

**功能**: 按照Metabase风格指南审核文档

**何时使用**:
- 🔍 审核文档质量
- 🔍 审查包含文档的PR
- 🔍 检查文档格式

**审核内容**:
- 语气和风格
- 结构和清晰度
- 链接和引用
- 格式规范

**强制使用**: 是（PreToolUse Hook强制检查）

---

#### 3. doc-coauthoring - 文档协作

**功能**: 引导用户完成结构化文档协作

**何时使用**:
- 📝 编写重要文档（PRD、设计文档、决策文档）
- 📝 创建技术规范
- 📝 起草提案

**流程**:
1. Context Gathering - 收集上下文
2. Refinement & Structure - 迭代优化
3. Reader Testing - 读者测试

**特点**: 结构化工作流，确保文档质量

---

### 🛠️ 开发工具Skill

#### 4. hook-development - Hook开发

**功能**: 创建和配置Claude Code Hooks

**何时使用**:
- 🔧 创建PreToolUse/PostToolUse Hook
- 🔧 配置事件驱动自动化
- 🔧 实现prompt-based hooks

**支持的Hook类型**:
- PreToolUse - 工具执行前验证
- PostToolUse - 工具执行后响应
- SessionStart/SessionEnd - 会话管理
- UserPromptSubmit - 用户输入验证

---

#### 5. command-development - 命令开发

**功能**: 创建自定义斜杠命令

**何时使用**:
- ⚡ 创建/命令
- ⚡ 定义命令参数
- ⚡ 实现交互式命令

**命令功能**:
- Markdown文件格式
- YAML frontmatter配置
- 动态参数
- Bash执行

---

### 🎯 项目专用Skill

#### 6. workflow-skill (jingzhe-workflow) - 惊蛰计划协作流 ⭐

**功能**: 惊蛰计划专用协作工作流

**何时使用**:
- 🎮 游戏竞赛平台的所有协作任务
- 📊 设计问题讨论
- 💻 功能开发
- 🐛 Bug修复

**包含内容**:
- 设计问题管理
- 需求确认流程
- 任务分解
- 进度追踪
- 质量检查

**集成工具**: 14个自动化工具（Command/Hook/Agent）

---

### 📋 其他辅助Skill

#### 7. skill-creator - Skill创建器

**功能**: 创建新的Skill

**何时使用**:
- 🔨 创建新Skill
- 🔨 更新现有Skill

---

#### 8. agent-identifier - Agent识别

**功能**: 识别和使用Agent

**何时使用**:
- 🤖 需要启动Agent
- 🤖 协调多个Agent

---

#### 9. agent-memory - Agent记忆

**功能**: 管理Agent的记忆和上下文

**何时使用**:
- 💾 保存Agent会话记忆
- 💾 检索历史信息

---

#### 10. web-research - 网络搜索

**功能**: 搜索网络信息

**何时使用**:
- 🔍 查找最新信息
- 🔍 验证技术细节

---

#### 11. content-research-writer - 内容研究写作

**功能**: 研究并撰写内容

**何时使用**:
- 📝 需要研究的写作任务
- 📝 内容创作

---

#### 12. product-manager-toolkit - 产品经理工具包

**功能**: 产品经理辅助工具

**何时使用**:
- 📊 产品需求分析
- 📊 产品规划

---

#### 13. product-requirements - 产品需求

**功能**: 管理产品需求

**何时使用**:
- 📋 需求收集
- 📋 需求分析

---

#### 14. hybrid-search-implementation - 混合搜索实现

**功能**: 实现混合搜索功能

**何时使用**:
- 🔍 搜索功能开发
- 🔍 搜索优化

---

## 🎯 使用优先级

### 必须使用（强制）

| Skill | 场景 | 强制方式 |
|-------|------|---------|
| **docs-write** | 编写/更新.md文档 | PreToolUse Hook |
| **docs-review** | 审核文档 | PreToolUse Hook |

### 推荐使用（高优先级）

| Skill | 场景 | 说明 |
|-------|------|------|
| **workflow-skill** | 惊蛰计划所有任务 | 项目专用 |
| **doc-coauthoring** | 重要文档协作 | 结构化流程 |

### 按需使用（需要时）

| Skill | 场景 | 说明 |
|-------|------|------|
| hook-development | 创建Hook | Hook开发时 |
| command-development | 创建命令 | 命令开发时 |
| web-research | 网络搜索 | 需要外部信息时 |

---

## 💡 快速参考

### 文档任务

```
编写文档 → docs-write ⭐
审核文档 → docs-review ⭐
协作写作 → doc-coauthoring
```

### 开发任务

```
创建Hook → hook-development
创建命令 → command-development
惊蛰计划任务 → workflow-skill ⭐
```

### 其他任务

```
网络搜索 → web-research
创建Skill → skill-creator
产品分析 → product-manager-toolkit
```

---

## 🔗 详细文档

每个Skill的详细文档位于：
```
.claude/skills/<skill-name>/<skill-name>/SKILL.md
```

---

**版本**: v1.0
**更新时间**: 2025-01-11
**Skill总数**: 14个
**核心Skill**: 2个（docs-write、docs-review）
