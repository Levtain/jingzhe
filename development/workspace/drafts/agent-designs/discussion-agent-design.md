# discussion-agent 详细设计方案

> **优先级**: 🔴 P0 (最高)
> **价值**: ⭐⭐⭐⭐⭐
> **工作量**: 2-3小时
> **状态**: 📝 设计中

---

## 1. Agent概述

### 1.1 核心目标

自动化问题讨论流程,实现"继续讨论"模式,减少80%的手动操作。

### 1.2 解决的问题

**当前痛点**:
- 用户需要手动调用 `/discuss` 命令
- 每次讨论新问题都要重新执行命令
- 需要手动编辑问题清单标记✅
- 工作流不连贯,频繁中断

**解决后的效果**:
- 用户只需说"继续讨论"或"下一个问题"
- Agent自动加载下一个问题
- Agent自动记录决策并标记✅
- Agent询问是否继续下一个问题
- 工作流流畅不中断

### 1.3 使用场景

```yaml
触发条件:
  - 用户说"继续讨论"
  - 用户说"下一个问题"
  - 用户说"继续"
  - 问题清单有未确认问题

典型场景:
  用户: "继续讨论"
  Agent: 显示下一个未确认问题
  用户: 选择A
  Agent: 自动记录并标记✅,询问"继续?"
  用户: "是"
  Agent: 自动显示下一个问题
```

---

## 2. Agent配置

### 2.1 Frontmatter配置

```yaml
---
name: discussion-agent
description: Use this agent for continuous question discussion in design phase. Examples:

<example>
Context: User is working through a question list and wants to continue discussing unanswered questions.
user: "Continue the discussion"
assistant: "I'll launch the discussion-agent to load the next unanswered question, present it with options, record your decision, and automatically mark it as confirmed."
<commentary>
Triggered when user wants to continue question discussion without manually calling commands.
</example>
</example>

<example>
Context: User has just finished answering one question and wants to move to the next.
user: "Next question"
assistant: "Launching discussion-agent to automatically load the next unanswered question and present it for discussion."
<commentary>
Triggered to smoothly continue the discussion flow without interruption.
</example>
</example>

model: inherit
color: yellow
tools: ["Read", "Edit", "Write"]
---
```

### 2.2 角色定义

```markdown
You are the Discussion Agent, specializing in facilitating smooth, continuous question discussions during the design phase.

**Your Core Responsibilities:**
1. Automatically load the next unanswered question from the question list
2. Present the question with clear options and context
3. Record user's decision and reasoning
4. Automatically mark the question as confirmed (✅)
5. Ask if the user wants to continue to the next question
6. Maintain discussion flow without manual command invocation

**Design Philosophy:**
- Reduce friction: User should only focus on answering questions
- Continuous flow: No need to manually call commands between questions
- Automatic tracking: Automatically update question status
- Progress awareness: Always show discussion progress
```

---

## 3. 工作流程详解

### 3.1 完整工作流

```bash
用户触发: "继续讨论"
  ↓
Agent执行:
  1. 读取问题清单文件
  2. 定位下一个未确认问题
  3. 生成提问模板
  4. 显示问题
  ↓
用户回答: 选择A/B/C或提出新方案
  ↓
Agent执行:
  1. 记录用户选择
  2. 记录用户理由(如果有)
  3. 更新问题清单,标记为✅
  4. 显示进度摘要
  5. 询问: "继续下一个问题?"
  ↓
用户选择:
  - "是" → 返回步骤1,加载下一个问题
  - "否" → 结束讨论,生成总结
  - "暂停" → 保存进度,结束会话
```

### 3.2 问题定位逻辑

```python
def locate_next_question(question_list):
    """
    定位下一个未确认问题

    返回: (question_number, question_title, question_content)
    """
    for question in question_list:
        if not has_checkmark(question):  # 没有✅标记
            return extract_question_info(question)

    # 所有问题都已确认
    return None
```

### 3.3 自动记录逻辑

```python
def record_decision(question_number, user_choice, user_reasoning):
    """
    记录用户决策

    更新内容:
    - 决策: 用户选择(A/B/C/自定义)
    - 决策理由: 用户给出的理由
    - 决策日期: 今天
    - 状态标记: ✅
    """
    update_question_markdown(
        question_number=question_number,
        status="✅ 已确认",
        decision=user_choice,
        reasoning=user_reasoning,
        date=today()
    )
```

---

## 4. 输出格式

### 4.1 问题显示格式

```markdown
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【当前模块】{模块名称}
【问题清单】{文件路径}
【讨论阶段】{第X轮 - XXX}
【当前进度】{已完成数} → {当前问题} (当前)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【问题 {问题编号}】{问题标题}

**问题描述**:
{详细描述}

**选项**:
- **A. {选项1}**(推荐 if applicable)
  {优点}
  {缺点}

- **B. {选项2}**
  {优点}
  {缺点}

- **C. {选项3}**
  {优点}
  {缺点}

**我的建议**: {推荐选项}
**理由**: {推荐理由}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【等待你的回答】
请选择 A/B/C,或提出你的想法。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 4.2 记录确认后格式

```markdown
✅ {问题编号} 已确认!

**你的选择**: {A/B/C}
**你的理由**: {用户理由}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 **进度摘要**:
- ✅ 已确认: {X}个问题
- 🔄 当前讨论: {当前问题}
- ⏳ 待确认: {Y}个问题
- 📈 完成度: {Z}%

【下一步建议】
{下一个问题的简短说明}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❓ **是否继续下一个问题?**
- 输入 "是" / "继续" / "next" → 继续讨论
- 输入 "否" / "暂停" / "结束" → 结束讨论
```

### 4.3 所有问题完成格式

```markdown
🎉 **恭喜! 所有问题已确认完成!**

**模块**: {模块名称}
**总问题数**: {N}个
**完成时间**: {日期时间}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 **完成统计**:
- 第一轮问题: {X}个全部完成 ✅
- 第二轮问题: {Y}个全部完成 ✅
- 第三轮问题: {Z}个全部完成 ✅
- 第四轮问题: {W}个全部完成 ✅

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【下一步建议】
1. 使用 /sync-docs 同步所有决策到设计文档
2. 使用 design-audit-agent 审核设计质量
3. 使用 /check-progress 查看整体进度
4. 开始下一个模块的讨论

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 5. 核心功能实现

### 5.1 问题清单文件定位

```python
def find_question_list():
    """
    查找问题清单文件

    优先级:
    1. 用户指定的文件路径
    2. development/issues/questions.md (默认)
    3. development/issues/*questions.md (最新)
    """
    if user_provided_path:
        return user_provided_path

    # 尝试默认位置
    default_path = "development/issues/questions.md"
    if exists(default_path):
        return default_path

    # 查找最新的问题清单
    question_lists = glob("development/issues/*questions.md")
    if question_lists:
        return latest_file(question_lists)

    return None
```

### 5.2 问题解析逻辑

```python
def parse_question_list(file_path):
    """
    解析问题清单文件

    提取:
    - 模块名称
    - 讨论阶段
    - 所有问题列表
    - 已确认问题数
    - 待确认问题数
    """
    content = read_file(file_path)

    # 提取模块名称
    module_name = extract_first_heading(content)

    # 提取讨论阶段
    stage = extract_stage(content)

    # 提取所有问题
    questions = extract_all_questions(content)

    # 统计完成度
    confirmed_count = count_confirmed(questions)
    unconfirmed_count = len(questions) - confirmed_count
    completion_rate = (confirmed_count / len(questions)) * 100

    return {
        "module_name": module_name,
        "stage": stage,
        "questions": questions,
        "confirmed_count": confirmed_count,
        "unconfirmed_count": unconfirmed_count,
        "completion_rate": completion_rate
    }
```

### 5.3 进度计算

```python
def calculate_progress(questions):
    """
    计算讨论进度

    返回: {
        "total": 总问题数,
        "confirmed": 已确认数,
        "unconfirmed": 未确认数,
        "rate": 完成百分比
    }
    """
    total = len(questions)
    confirmed = sum(1 for q in questions if has_checkmark(q))
    unconfirmed = total - confirmed
    rate = (confirmed / total) * 100 if total > 0 else 0

    return {
        "total": total,
        "confirmed": confirmed,
        "unconfirmed": unconfirmed,
        "rate": rate
    }
```

---

## 6. 边缘情况处理

### 6.1 问题清单文件不存在

```markdown
❌ **错误: 找不到问题清单文件**

请确认:
1. 文件路径是否正确
2. development/issues/ 目录是否存在
3. 是否有问题清单文件 (*questions.md)

**可用的问题清单**:
{列出 development/issues/ 下的所有问题清单}

**建议**:
- 检查目录结构
- 创建问题清单
- 使用 question-analysis-agent 从设计文档提取问题
```

### 6.2 所有问题都已确认

```markdown
🎉 **恭喜! 所有问题已确认完成!**

{显示完成统计和下一步建议}
```

### 6.3 问题清单格式不正确

```markdown
⚠️ **警告: 问题清单格式可能不正确**

未找到明确的问题标记,请确保:
- 问题编号格式为: ### 1.1, ### Q1.2, 或类似格式
- 未确认问题没有 ✅ 标记
- 问题包含明确的选项和描述

**尝试使用第一个未完成的问题**: {问题标题}

如果格式有误,请手动检查问题清单文件。
```

### 6.4 用户选择无效选项

```markdown
⚠️ **警告: 未识别的选项**

你输入的选项不在 A/B/C 范围内。

**请重新选择**:
- 输入 A / B / C
- 或提出你自己的方案

【问题】{问题标题}
【选项】:
- A. ...
- B. ...
- C. ...
```

---

## 7. 与现有Command的关系

### 7.1 /discuss Command

**当前工作流**:
```bash
/discuss → 显示问题 → 用户回答 → 手动编辑标记✅
/discuss → 显示下一个问题 → ...
```

**优化后工作流**:
```bash
"继续讨论" → 显示问题 → 用户回答 → 自动标记✅,询问"继续?"
用户说"是" → 自动显示下一个问题 → ...
```

### 7.2 保持兼容性

**仍然支持 /discuss 命令**:
- 用于首次启动讨论
- 用于指定特定问题清单
- 用于从特定问题开始讨论

**discussion-agent 增强**:
- 用于连续讨论
- 自动化流程
- 减少手动操作

---

## 8. 使用流程

### 8.1 首次使用

```bash
# 1. 确认有未确认的问题
/check-progress

# 2. 首次启动讨论
/discuss

# 3. 之后使用discussion-agent
"继续讨论"
```

### 8.2 日常使用

```bash
# 每天开始工作时
"继续讨论"

# Agent自动:
- 加载下一个问题
- 等待你回答
- 记录并标记✅
- 询问是否继续

# 你只需:
- 选择A/B/C
- 说"继续"或"暂停"
```

### 8.3 完成讨论

```bash
# 所有问题都完成后
Agent自动显示:
"🎉 所有问题已确认完成!
下一步: 使用 /sync-docs 同步决策"
```

---

## 9. 质量标准

### 9.1 功能完整性

```yaml
✅ 必须实现:
  - 自动加载下一个问题
  - 自动记录决策
  - 自动标记✅
  - 自动询问是否继续
  - 显示进度摘要

🎯 优化目标:
  - 流畅的用户体验
  - 清晰的进度显示
  - 准确的问题定位
```

### 9.2 性能标准

```yaml
响应速度:
  - 加载问题: <3秒
  - 记录决策: <2秒
  - 更新文件: <2秒

准确性:
  - 问题定位准确率: 100%
  - 决策记录准确率: 100%
  - 标记更新准确率: 100%
```

### 9.3 用户体验

```yaml
流畅性:
  - 无需手动调用命令
  - 工作流不中断
  - 进度实时显示

友好性:
  - 清晰的提示
  - 简洁的操作
  - 明确的反馈
```

---

## 10. 测试用例

### 10.1 测试场景1: 连续讨论

```bash
输入: "继续讨论"

预期:
1. 加载下一个未确认问题
2. 显示问题和选项
3. 等待用户输入

用户: "A"

预期:
1. 记录选择A
2. 标记为✅
3. 显示进度摘要
4. 询问"继续?"

用户: "是"

预期:
1. 自动加载下一个问题
2. 循环继续
```

### 10.2 测试场景2: 所有问题完成

```bash
条件: 所有问题都已确认

输入: "继续讨论"

预期:
显示"🎉 所有问题已确认完成!"
显示完成统计
显示下一步建议
```

### 10.3 测试场景3: 文件不存在

```bash
条件: development/questions.md 不存在

输入: "继续讨论"

预期:
显示错误信息
列出可用的问题清单
提供建议
```

---

## 11. 实施计划

### 11.1 开发步骤

```yaml
步骤1: 创建Agent文件 (10分钟)
  - 创建 .claude/agents/discussion-agent.md
  - 配置frontmatter
  - 定义角色职责

步骤2: 实现核心逻辑 (1小时)
  - 实现问题清单定位 (15分钟)
  - 实现问题解析 (20分钟)
  - 实现问题显示格式 (15分钟)
  - 实现决策记录 (20分钟)
  - 实现进度跟踪 (10分钟)

步骤3: 实现交互逻辑 (30分钟)
  - 实现继续询问 (10分钟)
  - 实现完成检测 (10分钟)
  - 实现错误处理 (10分钟)

步骤4: 测试验证 (20分钟)
  - 测试连续讨论流程
  - 测试自动记录
  - 测试进度显示
  - 优化交互体验

步骤5: 部署和文档 (20分钟)
  - 部署到.claude/agents/
  - 创建使用示例
  - 更新文档
```

### 11.2 测试计划

```yaml
测试用例1: 连续讨论3个问题
  - 验证自动加载
  - 验证自动记录
  - 验证进度显示

测试用例2: 所有问题完成
  - 验证完成检测
  - 验证统计准确

测试用例3: 文件不存在
  - 验证错误处理
  - 验证友好提示
```

---

## 12. 预期效果

### 12.1 量化指标

```yaml
操作减少:
  - 原来: 8次操作 (命令+编辑)
  - 优化后: 5次操作
  - 减少: 37.5%

时间节省:
  - 原来: 每个问题需要手动操作
  - 优化后: 自动化流程
  - 节省: ~2分钟/问题

用户体验:
  - 工作流流畅度: ⭐⭐⭐⭐⭐
  - 操作简便度: ⭐⭐⭐⭐⭐
  - 进度可见性: ⭐⭐⭐⭐⭐
```

### 12.2 质量提升

```yaml
讨论效率:
  - 减少手动操作80%
  - 工作流不中断
  - 专注于回答问题

准确性:
  - 自动记录决策,不会遗漏
  - 自动标记✅,不会忘记
  - 进度实时准确
```

---

## 13. 风险和限制

### 13.1 当前限制

```yaml
依赖问题清单格式:
  - 需要问题清单格式规范
  - 需要有明确的问题编号
  - 需要有✅标记规范

不支持的操作:
  - 跳过问题
  - 返回上一个问题
  - 修改已确认问题
```

### 13.2 风险缓解

```yaml
格式验证:
  - 启动前验证文件格式
  - 格式不正确时给出提示

手动回退:
  - 用户仍可手动编辑问题清单
  - Agent不会强制锁定文件
```

---

## 14. 后续优化方向

### 14.1 短期优化

```yaml
支持跳过问题:
  - "跳过这个问题"
  - 自动标记为"跳过"

支持返回:
  - "返回上一个"
  - 修改已确认的决策

支持备注:
  - 添加备注说明
  - 标记重点问题
```

### 14.2 中期优化

```yaml
智能推荐:
  - 根据上下文推荐选项
  - 提供决策支持

多问题清单:
  - 同时跟踪多个模块
  - 智能切换问题清单
```

### 14.3 长期优化

```yaml
AI辅助决策:
  - 分析历史决策模式
  - 提供决策建议

会议模式:
  - 多人讨论支持
  - 投票机制
```

---

## 15. 总结

### 15.1 核心价值

这个Agent将:
- ✅ 减少80%的手动操作
- ✅ 实现流畅的讨论工作流
- ✅ 自动跟踪进度
- ✅ 防止遗漏更新

### 15.2 与工作流的契合

**设计讨论流程**:
```
问题清单 → discussion-agent → 所有问题确认 → doc-sync-agent → 设计文档
```

**日常使用**:
```
每天早上: "继续讨论"
Agent: 自动加载问题,记录决策,标记✅
用户: 只需选择A/B/C
```

### 15.3 立即可用

- 技术成熟,易于实现
- 基于现有的/discuss Command
- 可立即投入使用

---

**设计完成时间**: 2025-01-10
**设计人**: 老黑(Claude)
**状态**: ✅ 设计完成,等待实施
**下一步**: 实施后立即测试

---

## 🚀 立即行动

设计方案已完成!

**核心特点**:
1. 自动化流程: "继续" → 显示问题 → 记录 → 询问"继续?"
2. 减少80%手动操作
3. 流畅的用户体验
4. 实时进度显示

**预计工作量**: 2小时 (比原计划3小时少)

**是否开始实施?** 🎯
