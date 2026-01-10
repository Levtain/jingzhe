# completion-check-agent 详细设计方案

> **优先级**: 🟡 P1 (高)
> **价值**: ⭐⭐⭐⭐
> **工作量**: 1-2小时
> **状态**: 📝 设计中

---

## 1. Agent概述

### 1.1 核心目标

智能验证模块完整性,防止遗漏问题,确保设计或开发质量达到可进入下一阶段的标准。

### 1.2 解决的问题

**当前痛点**:
- 模块完成后不清楚是否真的"完成"
- 不知道还缺什么
- 可能遗漏重要文档或问题
- 没有明确的"完成"标准

**解决后的效果**:
- 系统化检查所有必需的文档和问题
- 清晰的待办事项清单
- 明确的完成度评估
- 智能的下一步行动建议

### 1.3 使用场景

```yaml
触发条件:
  - 模块所有问题已确认
  - 用户说"检查完成度"
  - 用户说"验证模块完整性"
  - 准备进入下一阶段前

典型场景:
  设计阶段:
    - 问题讨论完成
    → completion-check-agent 验证设计完整性
    → 发现遗漏的文档或问题
    → 补充后重新验证

  开发阶段:
    - 代码开发完成
    → completion-check-agent 验证开发完整性
    → 发现遗漏的测试或文档
    → 补充后重新验证
```

---

## 2. Agent配置

### 2.1 Frontmatter配置

```yaml
---
name: completion-check-agent
description: Use this agent when verifying module completeness before moving to the next phase. Examples:

<example>
Context: User has finished discussing all questions for a module and wants to verify everything is complete.
user: "Check if the game submission system module is complete"
assistant: "I'll launch the completion-check-agent to systematically verify document consistency, check all questions are confirmed, validate version numbers, and generate a completion report with a TODO list."
<commentary>
Triggered when a module reaches a milestone and needs verification before proceeding.
</example>
</example>

<example>
Context: User wants to ensure nothing is missing before starting development.
user: "Verify the module completeness"
assistant: "Launching completion-check-agent to scan all related documents, check for consistency, validate cross-references, and provide a comprehensive completion status report."
<commentary>
Triggered to ensure quality gates are met before transitioning to the next phase.
</example>
</example>

model: inherit
color: green
tools: ["Read", "Grep", "Glob"]
---
```

### 2.2 角色定义

```markdown
You are the Completion Check Agent, specializing in verifying module completeness and quality before moving to the next phase.

**Your Core Responsibilities:**
1. Scan all related documents for the module
2. Check question lists for 100% completion
3. Validate design document synchronization status
4. Check version number consistency
5. Validate cross-reference effectiveness
6. Generate completion report with TODO list
7. Suggest next actions

**Verification Philosophy:**
- **Comprehensive**: Check all aspects, not just obvious ones
- **Systematic**: Use a checklist approach to avoid missing items
- **Pragmatic**: Focus on what matters most, not perfectionism
- **Actionable**: Always provide specific next steps
```

---

## 3. 验证维度详解

### 3.1 维度1: 文档完整性检查

**检查项**:

```yaml
必需文档是否存在:
  - 设计文档: docs/design/{module}-design_v{version}.md
  - 问题清单: development/issues/{module}-questions.md
  - 决策记录: development/decisions/{module}-decisions.md (可选)

文档是否完整:
  - 设计文档包含所有必需章节
  - 问题清单所有问题都已确认
  - 文档有明确的版本号

文档是否最新:
  - 设计文档最后更新时间
  - 问题清单最后更新时间
  - 版本号是否一致
```

**输出示例**:
```markdown
### 📄 文档完整性

✅ **存在的文档**:
- ✅ 设计文档: docs/design/游戏提交系统设计文档_v1.0.md
- ✅ 问题清单: development/issues/game-submission-questions-v2.md
- ⚠️  决策记录: development/decisions/game-submission-decisions.md (不存在)

❌ **缺失的文档**:
- ❌ API文档: docs/api/game-submission-api.md (建议创建)
- ❌ 测试计划: tests/game-submission-test-plan.md (建议创建)

✅ **文档完整性**: 80% (4/5项)
```

### 3.2 维度2: 问题完成度检查

**检查项**:

```yaml
问题清单状态:
  - 所有问题是否已确认(标记✅)
  - 是否有未讨论的问题
  - 是否有部分确认的问题

决策记录:
  - 已确认问题的决策是否记录
  - 决策理由是否详细
  - 决策日期是否记录
```

**输出示例**:
```markdown
### ✅ 问题完成度

**问题清单**: game-submission-questions-v2.md
- ✅ 已确认: 29个问题 (100%)
- 🔄 讨论中: 0个问题
- ❌ 未讨论: 0个问题

**完成度**: ⭐⭐⭐⭐⭐ 100%

✅ **问题100%完成,可以进行下一阶段**
```

### 3.3 维度3: 文档同步状态检查

**检查项**:

```yaml
设计文档 vs 问题清单:
  - 已确认问题是否已同步到设计文档
  - 数值/规则是否一致
  - 章节引用是否正确

版本号一致性:
  - claude.md 版本号
  - CHANGELOG.md 版本号
  - 设计文档版本号
```

**输出示例**:
```markdown
### 🔄 文档同步状态

✅ **一致的文档** (4个):
- 评分系统设计方案_v1.0.md
- 排名系统技术实现文档_v1.0.md
- 用户角色与权限定义.md
- CHANGELOG.md

⚠️ **发现不一致** (1个):
- scoring-system-questions.md vs 评分系统设计方案_v1.0.md
  → Q1.5: 问题清单说"评审团权重×3",设计文档说"×2"
  → 建议: 同步正确的数值

❌ **缺失同步** (2个):
- Q2.1-Q2.3 已确认但未同步到设计文档
  → 缺失在: 排名系统技术实现文档_v1.0.md
  → 建议: 立即同步

**同步完整性**: 70% (需要补充2个问题的同步)
```

### 3.4 维度4: 版本号一致性检查

**检查项**:

```yaml
版本号检查:
  - CHANGELOG.md 当前版本
  - claude.md 当前版本
  - 设计文档版本号
  - 问题清单引用的版本号

交叉引用检查:
  - 搜索引用旧版本的地方
  - 验证链接有效性
  - 检查章节号引用
```

**输出示例**:
```markdown
### 🔢 版本号一致性

**当前版本**: v1.2

✅ **版本号一致**:
- CHANGELOG.md: v1.2 ✅
- claude.md: v1.2 ✅
- 大部分设计文档: v1.0 (可以接受,非关键文档)

⚠️ **版本号不一致**:
- 评分系统设计文档: v1.0
  → 建议: 更新为 v1.2

❌ **失效的交叉引用** (2个):
- {file}:{line} → 引用了旧版本 v1.0
  → 应该引用: v1.2
```

### 3.5 维度5: 交叉引用有效性检查

**检查项**:

```yaml
内部链接:
  - [文档名](路径) 是否有效
  - §章节号 引用是否正确
  - @文件引用 是否存在

外部链接:
  - (可选) 检查外部链接是否有效
```

**输出示例**:
```markdown
### 🔗 交叉引用有效性

✅ **有效的引用**: 25个

❌ **失效的引用** (2个):
- development/issues/questions.md:45 → [已归档文档](../archive/old.md)
  → 文件已移动,应该引用: ../archive/scoring-system-discussion-2025-01-05.md

- docs/design/system-design.md:78 → §5.2
  → §5.2 不存在,应该是 §5.1

**引用有效性**: 92% (25/27有效)
```

---

## 4. 输出格式

### 4.1 完整报告结构

```markdown
# ✅ 模块完成度验证报告

**验证模块**: {模块名称}
**验证时间**: YYYY-MM-DD HH:MM
**验证标准**: "全面检查,确保无遗漏"
**验证人**: completion-check-agent

---

## 📄 文档完整性

✅ **存在的文档**:
- {文档列表}

❌ **缺失的文档**:
- {文档列表}

✅ **文档完整性**: {X}%

---

## ✅ 问题完成度

**问题清单**: {文件名}
- ✅ 已确认: {X}个问题 (100%)
- 🔄 讨论中: {Y}个问题
- ❌ 未讨论: {Z}个问题

**完成度**: ⭐⭐⭐⭐⭐ {X}%

---

## 🔄 文档同步状态

✅ **一致的文档**: {数量}个
⚠️ **发现不一致**: {数量}个
❌ **缺失同步**: {数量}个

**同步完整性**: {X}%

---

## 🔢 版本号一致性

**当前版本**: v{X}

✅ **版本号一致**
❌ **版本号不一致**

---

## 🔗 交叉引用有效性

✅ **有效引用**: {X}个
❌ **失效引用**: {Y}个

**引用有效性**: {X}%

---

## 📊 总体评估

**完成度评分**: ⭐⭐⭐⭐ (4/5星)

**完成的部分**:
1. {完成项1}
2. {完成项2}

**待完成的部分**:
1. {待办项1}
2. {待办项2}

---

## 📝 待办事项清单

### 🔴 必须完成 (阻塞进入下一阶段)

- [ ] {待办1}
- [ ] {待办2}

**预计时间**: {X}小时

### 🟡 建议完成 (提升质量)

- [ ] {待办1}
- [ ] {待办2}

**预计时间**: {X}小时

### 🟢 可选优化 (锦上添花)

- [ ] {待办1}
- [ ] {待办2}

**预计时间**: {X}分钟

---

## 💡 下一步行动

### 立即行动:
1. {行动1}
2. {行动2}

### 建议行动:
1. {行动1}
2. {行动2}

---

## 🎯 结论

**完成状态**: {可以进入下一阶段 / 需要补充后进入}

**理由**: {为什么可以或不可以}

**建议**:
- ✅ 可以进入开发阶段
- ⏳ 需要补充文档后进入
- ❌ 需要完成所有待办事项后进入

---

**报告生成时间**: YYYY-MM-DD HH:MM
**Agent版本**: v1.0
**下次验证建议**: {何时重新验证}
```

---

## 5. 完成度标准

### 5.1 设计阶段完成标准

```yaml
必需文档:
  ✅ 设计文档 v1.0+
  ✅ 问题清单 (100%确认)
  ✅ CHANGELOG已更新

问题完成度:
  ✅ 100%问题已确认

文档同步:
  ✅ 所有问题已同步到设计文档
  ✅ 版本号一致

无阻塞性问题:
  ✅ 无A级问题
  ✅ B级问题已解决或可接受
```

### 5.2 开发阶段完成标准

```yaml
必需文档:
  ✅ 设计文档
  ✅ API文档
  ✅ 测试计划
  ✅ 部署文档

代码完成度:
  ✅ 所有功能已实现
  ✅ 所有测试已通过
  ✅ 代码审查已通过

质量标准:
  ✅ 无严重bug
  ✅ 测试覆盖率 >80%
  ✅ 性能达标
```

---

## 6. 边缘情况处理

### 6.1 模块不存在

```markdown
❌ **错误: 找不到模块相关文档**

请确认:
1. 模块名称是否正确
2. 是否有相关的设计文档
3. 是否有问题清单

**建议**:
- 使用 /check-progress 查看所有模块
- 检查 docs/design/ 目录
```

### 6.2 问题未100%完成

```markdown
⚠️ **警告: 问题未100%完成**

**当前进度**: {X}%

**未完成的问题**:
- {问题列表}

**建议**:
- 先完成所有问题讨论
- 使用 discussion-agent 继续讨论
- 完成后重新验证
```

### 6.3 严重问题阻塞

```markdown
🔴 **阻塞问题: 发现未解决的A级问题**

**问题列表**:
- A1: {问题1}
- A2: {问题2}

**建议**:
- 使用 design-audit-agent 深度审核
- 解决所有A级问题
- 重新验证完成度
```

---

## 7. 实施计划

### 7.1 开发步骤

```yaml
步骤1: 创建Agent文件 (5分钟)

步骤2: 实现验证逻辑 (30分钟)
  - 实现文档完整性检查 (10分钟)
  - 实现问题完成度检查 (5分钟)
  - 实现文档同步检查 (10分钟)
  - 实现版本号检查 (5分钟)

步骤3: 实现报告生成 (30分钟)
  - 生成5个维度的检查结果
  - 计算完成度评分
  - 生成待办事项清单
  - 提供下一步行动建议

步骤4: 测试验证 (15分钟)
  - 测试设计阶段验证
  - 测试开发阶段验证

步骤5: 部署和文档 (10分钟)
```

### 7.2 测试计划

```yaml
测试用例1: 设计完成验证
  - 条件: 所有问题已确认
  - 预期: 生成完整报告,列出待办事项

测试用例2: 开发完成验证
  - 条件: 代码和测试已完成
  - 预期: 验证代码和测试完整性

测试用例3: 不完整模块
  - 条件: 问题未100%完成
  - 预期: 给出明确建议
```

---

## 8. 预期效果

### 8.1 量化指标

```yaml
验证速度:
  - 小型模块: 5-10分钟
  - 中型模块: 10-20分钟
  - 大型模块: 20-30分钟

准确性:
  - 遗漏检测率: 95%+
  - 待办项准确率: 90%+
```

### 8.2 质量提升

```yaml
防遗漏:
  - 系统化检查清单
  - 不遗漏重要文档
  - 不遗漏关键问题

质量保证:
  - 确保完成标准
  - 防止匆忙进入下一阶段
  - 减少返工
```

---

## 9. 与其他Agent的关系

### 9.1 协作关系

```yaml
设计阶段流程:
  1. discussion-agent → 所有问题确认
  2. completion-check-agent → 验证完整性
  3. doc-sync-agent → 补充缺失的同步
  4. design-audit-agent → 质量审核
  5. 准备进入开发阶段

开发阶段流程:
  1. 代码完成
  2. completion-check-agent → 验证开发完整性
  3. code-review-agent → 代码审核
  4. 准备部署上线
```

### 9.2 调用时机

```bash
问题讨论完成:
  /check-progress → 显示100%完成
  "验证模块完整性"
  → completion-check-agent

准备进入下一阶段:
  "检查是否可以开始开发"
  → completion-check-agent
```

---

## 10. 总结

### 10.1 核心价值

这个Agent将:
- ✅ 系统化验证模块完整性
- ✅ 防止遗漏重要文档或问题
- ✅ 提供明确的待办事项清单
- ✅ 确保质量标准

### 10.2 使用时机

**设计完成后**:
- 所有问题讨论完成
- 准备进入开发阶段前

**开发完成后**:
- 代码开发完成
- 准备部署上线前

### 10.3 立即可用

- 技术成熟,易于实现
- 基于/check-completion Command
- 可立即投入使用

---

**设计完成时间**: 2025-01-10
**设计人**: 老黑(Claude)
**状态**: ✅ 设计完成,等待实施
**下一步**: 实施后立即测试

---

## 🚀 准备实施

设计方案已完成!

**核心特点**:
1. 5维验证系统(文档、问题、同步、版本、引用)
2. 清晰的待办事项清单
3. 明确的完成度评估
4. 智能的下一步建议

**预计工作量**: 1-1.5小时 (比原计划1-2小时略少)

**准备开始实施!** 🎯
