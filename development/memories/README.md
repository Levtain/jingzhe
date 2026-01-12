# 项目记忆库

存放惊蛰计划的长期记忆和重要决策记录。

---

## 📂 目录结构

### context-snapshots/ - 上下文快照

自动保存的上下文状态快照:
- 在上下文使用率达到85%时自动触发
- 包含当前进度、问题讨论状态、下一步计划
- 用于会话恢复和上下文重建

**命名格式**: `YYYY-MM-DD-session-N.md`

### design-decisions/ - 设计决策记录

重要设计决策的记录:
- 决策背景
- 讨论过程
- 最终决策
- 决策理由

**命名格式**: `YYYY-MM-DD-{功能名称}-decision.md`

### project-notes/ - 项目重要笔记

项目过程中的重要笔记:
- 技术选型
- 架构思考
- 优化建议
- 问题解决方案

**命名格式**: `YYYY-MM-DD-{主题}-notes.md`

---

## 🔄 与 agent-memory 的区别

### agent-memory (系统级)
- 位置: `.claude/skills/agent-memory/memories/`
- 用途: Claude AI的系统级记忆
- 访问: Claude直接读取

### memories/ (项目级)
- 位置: `development/memories/`
- 用途: 人类可读的项目文档
- 访问: 方便团队成员查阅

---

## 📝 使用场景

**什么时候记录到 memories/**:
- 重要设计决策确认后
- 技术难点解决后
- 架构讨论完成时
- 项目里程碑达成时

**什么时候记录到 agent-memory**:
- 自动由memory-agent记录
- 上下文快照自动触发
- Claude需要跨会话记忆时

---

**创建时间**: 2025-01-12
**维护者**: AI (Claude)
