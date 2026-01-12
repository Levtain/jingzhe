# workflow-orchestrator-agent 详细设计方案

> **优先级**: 🟢 P2 (中)
> **价值**: ⭐⭐⭐⭐
> **工作量**: 3-4小时
> **状态**: 📝 设计中

---

## 1. Agent概述

### 1.1 核心目标

智能协调所有Agent,根据项目当前状态自动调用合适的Agent,实现无缝的自动化工作流。

### 1.2 解决的问题

**当前痛点**:
- 需要手动判断使用哪个Agent
- 工作流程不连贯
- 不知道下一步该做什么
- 多个Agent之间的协调需要人工介入

**解决后的效果**:
- 自动识别当前状态
- 智能推荐下一步操作
- 自动协调多个Agent
- 生成工作日报和进度报告
- 一键启动日常工作

### 1.3 使用场景

```yaml
触发条件:
  - 用户说"开始工作"
  - 用户说"今天做什么"
  - 用户说"继续项目"
  - 每天开始工作时

典型场景:
  每日启动:
    → "开始今天的工作"
    → workflow-orchestrator-agent 分析当前状态
    → 推荐下一步操作
    → 自动调用合适的Agent

  项目继续:
    → "继续项目"
    → 分析项目进度
    → 识别阻塞问题
    → 提供行动建议

  工作日报:
    → 每天结束时
    → 自动生成工作日报
    → 总结今日完成
    → 规划明日任务
```

---

## 2. Agent配置

### 2.1 Frontmatter配置

```yaml
---
name: workflow-orchestrator-agent
description: Use this agent for coordinating all agents and managing project workflow. Examples:

<example>
Context: User starts their workday and wants to know what to work on next.
user: "Start my workday"
assistant: "I'll launch the workflow-orchestrator-agent to analyze the current project state, identify the next priority tasks, and automatically launch the appropriate agent."
<commentary>
Triggered when user wants to start work or continue the project.
</example>
</example>

<example>
Context: User wants to continue the project but isn't sure what needs to be done.
user: "What should I work on next?"
assistant: "Launching workflow-orchestrator-agent to check project progress, identify pending tasks, and recommend the next action."
<commentary>
Triggered to get context-aware recommendations for next steps.
</example>
</example>

model: inherit
color: blue
tools: ["Read", "Grep", "Glob", "Task"]
---
```

### 2.2 角色定义

```markdown
You are the Workflow Orchestrator Agent, specializing in coordinating all agents and managing the project workflow intelligently.

**Your Core Responsibilities:**
1. Analyze the current project state comprehensively
2. Identify the current phase (design, development, review, etc.)
3. Recommend next actions based on context
4. Automatically launch appropriate agents
5. Coordinate multi-agent workflows
6. Generate daily work reports
7. Track project progress and milestones

**Orchestration Philosophy:**
- **Context-Aware**: Understand the project state before making recommendations
- **Proactive**: Suggest next steps without waiting for explicit requests
- **Seamless**: Coordinate multiple agents smoothly
- **Efficient**: Minimize user friction and decision fatigue
```

---

## 3. 工作流程详解

### 3.1 完整工作流

```bash
用户触发: "开始今天的工作"
  ↓
Agent分析:
  1. 读取项目状态文件
  2. 分析当前阶段
  3. 检查未完成的任务
  4. 识别阻塞问题
  5. 评估优先级
  ↓
Agent决策:
  - 推荐下一步操作
  - 自动启动合适的Agent
  - 提供多个选项供用户选择
  ↓
用户选择:
  - 选项A: 自动执行推荐操作
  - 选项B: 查看更多详情
  - 选项C: 自定义操作
  ↓
Agent执行:
  - 调用相应的Agent
  - 监控执行进度
  - 记录结果
  ↓
Agent总结:
  - 更新项目状态
  - 生成进度报告
  - 规划下一步
```

### 3.2 状态分析逻辑

```python
def analyze_project_state():
    """
    分析项目当前状态

    返回: {
        "current_phase": "design" | "development" | "review" | "deployment",
        "progress": {
            "completed_modules": [...],
            "in_progress_modules": [...],
            "pending_modules": [...]
        },
        "blockers": [...],
        "next_actions": [...]
    }
    """
    # 1. 检查问题清单
    question_lists = glob("development/issues/*questions.md")
    has_unanswered = check_unanswered_questions(question_lists)

    # 2. 检查设计文档
    design_docs = glob("docs/design/*.md")
    missing_design_docs = identify_missing_designs()

    # 3. 检查代码完成度
    code_files = glob("src/**/*.{js,py,java}")
    code_completion = estimate_code_completion()

    # 4. 检查未解决的问题
    issues = load_open_issues()

    # 5. 确定当前阶段
    if has_unanswered:
        phase = "design_discussion"
    elif missing_design_docs:
        phase = "design"
    elif code_completion < 100:
        phase = "development"
    else:
        phase = "review"

    return {
        "current_phase": phase,
        "has_unanswered": has_unanswered,
        "missing_designs": missing_design_docs,
        "code_completion": code_completion,
        "issues": issues
    }
```

### 3.3 智能推荐逻辑

```python
def recommend_next_action(state):
    """
    根据项目状态推荐下一步操作

    返回: {
        "primary_action": {...},
        "secondary_actions": [...],
        "reasoning": "..."
    }
    """
    phase = state["current_phase"]

    if phase == "design_discussion":
        return {
            "primary_action": {
                "agent": "discussion-agent",
                "prompt": "继续讨论问题",
                "reason": "有未回答的问题需要确认"
            },
            "secondary_actions": [
                {
                    "agent": "design-audit-agent",
                    "prompt": "审核当前设计",
                    "reason": "提前发现设计问题"
                }
            ]
        }

    elif phase == "design":
        return {
            "primary_action": {
                "agent": "completion-check-agent",
                "prompt": "检查设计完整性",
                "reason": "确保设计完整后再开发"
            },
            "secondary_actions": [
                {
                    "agent": "doc-sync-agent",
                    "prompt": "同步文档",
                    "reason": "确保文档一致性"
                }
            ]
        }

    elif phase == "development":
        return {
            "primary_action": {
                "agent": "code-review-agent",
                "prompt": "审核代码",
                "reason": "确保代码质量"
            },
            "secondary_actions": [
                {
                    "task": "继续开发",
                    "reason": "完成剩余功能"
                }
            ]
        }

    elif phase == "review":
        return {
            "primary_action": {
                "agent": "completion-check-agent",
                "prompt": "验证完成度",
                "reason": "准备发布前的最终检查"
            }
        }
```

---

## 4. 输出格式

### 4.1 状态分析报告

```markdown
# 📊 项目状态分析

**分析时间**: YYYY-MM-DD HH:MM
**项目**: 惊蛰计划
**当前阶段**: 设计讨论

---

## 📍 当前状态

### 整体进度

**完成度**: 45% (9/20个模块)

**已完成的模块**:
- ✅ 评分系统设计 (100%)
- ✅ 排名系统设计 (100%)
- ✅ 团队系统设计 (100%)

**进行中的模块**:
- 🔄 游戏提交系统设计 (85%)
  - 问题确认: 29/29 (100%)
  - 设计文档: 完成
  - 等待: 设计审核

**待开始的模块**:
- ⏳ 经济系统设计 (0%)
- ⏳ 通知系统设计 (0%)

---

## 🎯 推荐的下一步操作

### 🚀 主要推荐

**启动 discussion-agent** - 继续讨论问题

**理由**:
- 游戏提交系统的问题已100%确认
- 建议先进行设计审核
- 然后开始经济系统的问题讨论

**预计时间**: 30分钟

---

### 📋 备选方案

**方案1**: 使用 design-audit-agent 审核游戏提交系统设计
- 优点: 提前发现设计问题
- 预计时间: 15分钟

**方案2**: 使用 completion-check-agent 验证完整性
- 优点: 确保可以进入下一阶段
- 预计时间: 10分钟

**方案3**: 开始经济系统设计
- 优点: 推进新模块
- 预计时间: 2小时

---

## 🚧 阻塞问题

**无阻塞问题** ✅

---

## 📝 待办事项

### 今日重点

1. ✅ 游戏提交系统设计审核
2. ⏳ 经济系统问题提取
3. ⏳ 经济系统问题讨论

### 本周目标

- 完成经济系统设计
- 完成通知系统设计
- 开始前端框架搭建

---

**你想执行哪个方案?**
- 输入 "1" / "主要" → 启动 discussion-agent
- 输入 "2" → 启动 design-audit-agent
- 输入 "3" → 启动 completion-check-agent
- 输入 "4" → 开始新模块设计
- 输入自定义指令
```

### 4.2 工作日报格式

```markdown
# 📋 工作日报 - YYYY-MM-DD

**项目**: 惊蛰计划
**报告时间**: HH:MM

---

## ✅ 今日完成

### 完成的任务

1. **游戏提交系统设计** (2小时)
   - ✅ 完成29个问题的讨论
   - ✅ 创建设计文档 v1.0
   - ✅ 通过设计审核

2. **代码审核Agent创建** (20分钟)
   - ✅ 完成设计方案
   - ✅ 实现Agent
   - ✅ 创建使用指南

3. **文档同步** (10分钟)
   - ✅ 同步问题决策到设计文档
   - ✅ 更新版本号

**今日总计**: 2.5小时

---

## 📊 进度更新

### 项目整体进度

- **之前进度**: 40%
- **当前进度**: 45%
- **提升**: +5%

### 模块进度

| 模块 | 状态 | 进度 |
|------|------|------|
| 评分系统 | ✅ 完成 | 100% |
| 排名系统 | ✅ 完成 | 100% |
| 团队系统 | ✅ 完成 | 100% |
| 游戏提交 | ✅ 完成 | 100% |
| 经济系统 | 🔄 进行中 | 0% → 15% |
| 通知系统 | ⏳ 未开始 | 0% |

---

## 🎯 明日计划

### 优先任务

1. **经济系统设计** (2小时)
   - 提取设计问题
   - 开始问题讨论
   - 目标: 完成50%问题

2. **通知系统设计** (1小时)
   - 分析需求
   - 创建问题清单

### 备选任务

- 前端框架搭建
- API设计

---

## 🚧 遇到的问题

**无** ✅

---

## 💡 经验总结

### 做得好的地方

1. 讨论Agent大大提升了问题讨论效率
2. 设计审核Agent提前发现了潜在问题
3. 自动化工具节省了大量时间

### 可以改进的地方

1. 文档同步可以更及时
2. 可以增加更多自动化检查

---

## 📈 数据统计

**今日工作时间**: 2.5小时

**时间分配**:
- 设计讨论: 60%
- Agent开发: 25%
- 文档工作: 15%

**完成项数**: 3项

**Agent使用次数**:
- discussion-agent: 5次
- design-audit-agent: 1次
- doc-sync-agent: 1次

---

**报告生成**: workflow-orchestrator-agent
**下次报告**: 明天此时
```

---

## 5. Agent协调机制

### 5.1 自动协调场景

```yaml
场景1: 设计阶段完成
  触发: 所有问题已确认
  流程:
    1. workflow-orchestrator-agent 识别状态
    2. 自动调用 completion-check-agent 验证
    3. 验证通过后调用 design-audit-agent 审核
    4. 审核通过后调用 doc-sync-agent 同步
    5. 提示可以进入开发阶段

场景2: 开发阶段完成
  触发: 代码开发完成
  流程:
    1. workflow-orchestrator-agent 识别状态
    2. 自动调用 code-review-agent 审核
    3. 审核通过后调用 completion-check-agent 验证
    4. 验证通过后提示可以部署

场景3: 每日工作流
  触发: "开始今天的工作"
  流程:
    1. workflow-orchestrator-agent 分析当前状态
    2. 推荐今日任务列表
    3. 询问用户选择
    4. 自动启动相应的Agent
    5. 监控执行进度
    6. 完成后生成工作日报
```

### 5.2 Agent调用顺序

```python
def orchestrate_agents(phase, context):
    """
    根据阶段协调Agent调用

    phase: 当前阶段
    context: 上下文信息
    """
    workflows = {
        "design_complete": [
            {"agent": "completion-check-agent", "wait": True},
            {"agent": "design-audit-agent", "wait": True},
            {"agent": "doc-sync-agent", "wait": False},
            {"action": "prompt_development"}
        ],
        "development_complete": [
            {"agent": "code-review-agent", "wait": True},
            {"agent": "completion-check-agent", "wait": True},
            {"action": "prompt_deployment"}
        ],
        "daily_start": [
            {"agent": "analyze_state", "wait": True},
            {"action": "recommend_tasks"},
            {"agent": "user_selection", "wait": True},
            {"agent": "execute", "wait": True},
            {"action": "generate_report"}
        ]
    }

    workflow = workflows.get(phase, [])
    for step in workflow:
        if "agent" in step:
            result = launch_agent(step["agent"], context)
            if step.get("wait"):
                context = result
        elif "action" in step:
            execute_action(step["action"], context)

    return context
```

---

## 6. 智能特性

### 6.1 上下文感知

```python
def context_aware_recommendation():
    """
    基于上下文的智能推荐
    """
    # 考虑因素:
    # 1. 当前时间 (早晨/下午/晚上)
    # 2. 工作日/周末
    # 3. 历史工作模式
    # 4. 项目紧急程度
    # 5. 用户偏好

    current_hour = get_current_hour()
    is_weekend = is_weekend_today()
    user_preference = load_user_preference()

    if current_hour < 12:
        # 上午: 推荐创造性工作
        return recommend_creative_work()

    elif current_hour < 18:
        # 下午: 推荐执行性工作
        return recommend_execution_work()

    else:
        # 晚上: 推荐总结和规划
        return generate_daily_report()
```

### 6.2 学习用户偏好

```python
def learn_user_preference():
    """
    学习用户工作偏好
    """
    # 记录:
    # 1. 用户常选择的方案
    # 2. 工作时间偏好
    # 3. Agent使用频率
    # 4. 任务优先级倾向

    # 分析:
    preferences = {
        "morning_routine": [...],
        "preferred_agents": [...],
        "task_order": [...],
        "break_pattern": [...]
    }

    # 应用:
    # 根据偏好调整推荐
    # 优先推荐常用的Agent
    # 遵循用户的工作节奏
```

### 6.3 进度预测

```python
def predict_completion():
    """
    预测项目完成时间
    """
    # 基于历史数据:
    # 1. 每个模块的平均时间
    # 2. 用户的工作速度
    # 3. 剩余工作量
    # 4. 可能的阻塞因素

    completion_rate = calculate_completion_rate()
    remaining_work = estimate_remaining_work()
    work_speed = calculate_work_speed()

    predicted_days = remaining_work / work_speed

    return {
        "estimated_completion": f"{predicted_days}天后",
        "confidence": "85%",
        "factors": [...]
    }
```

---

## 7. 边缘情况处理

### 7.1 无明确下一步

```markdown
❓ **需要你的输入**

当前状态:
- 所有模块都已完成 ✅
- 没有明确的下一步任务

**可选操作**:
1. 开始新功能开发
2. 进行代码重构
3. 编写测试
4. 优化性能
5. 更新文档

**请告诉我你想做什么,或者我可以推荐一些选项**
```

### 7.2 多个阻塞问题

```markdown
⚠️ **发现多个阻塞问题**

**阻塞问题** (3个):
1. 经济系统设计未完成
2. API设计不明确
3. 依赖库版本冲突

**建议优先级**:
1. 🔴 优先: 完成经济系统设计 (阻塞其他模块)
2. 🟡 其次: 明确API设计 (影响开发)
3. 🟢 最后: 解决依赖冲突 (可以暂缓)

**你想从哪个开始?**
```

### 7.3 项目暂停后恢复

```markdown
🔄 **欢迎回来!**

距离上次工作: 3天

**上次完成**:
- ✅ 游戏提交系统设计

**当前状态**:
- 进行中: 经济系统设计
- 进度: 15%

**建议**:
1. 继续经济系统设计 (推荐)
2. 回顾之前的工作
3. 查看项目进度报告

**你想做什么?**
```

---

## 8. 实施计划

### 8.1 开发步骤

```yaml
步骤1: 创建Agent文件 (5分钟)

步骤2: 实现状态分析 (40分钟)
  - 实现项目状态读取 (10分钟)
  - 实现阶段识别逻辑 (10分钟)
  - 实现进度计算 (10分钟)
  - 实现阻塞问题检测 (10分钟)

步骤3: 实现智能推荐 (30分钟)
  - 实现推荐逻辑 (15分钟)
  - 实现优先级评估 (10分钟)
  - 实现多方案生成 (5分钟)

步骤4: 实现Agent协调 (40分钟)
  - 实现Agent调用逻辑 (15分钟)
  - 实现工作流程编排 (15分钟)
  - 实现执行监控 (10分钟)

步骤5: 实现报告生成 (30分钟)
  - 实现状态分析报告 (15分钟)
  - 实现工作日报 (15分钟)

步骤6: 测试验证 (30分钟)
  - 测试状态分析
  - 测试Agent协调
  - 测试报告生成

步骤7: 部署和文档 (15分钟)
```

### 8.2 测试用例

```yaml
测试用例1: 设计阶段项目
  - 条件: 有未回答的问题
  - 预期: 推荐启动discussion-agent

测试用例2: 开发阶段项目
  - 条件: 代码开发完成
  - 预期: 推荐启动code-review-agent

测试用例3: 完整工作流
  - 条件: 用户说"开始今天的工作"
  - 预期: 分析状态、推荐任务、执行、生成报告
```

---

## 9. 与其他Agent的关系

### 9.1 协作关系

```yaml
workflow-orchestrator-agent (中心协调者):
  ↓ 调用
  ├─ discussion-agent (讨论问题)
  ├─ design-audit-agent (审核设计)
  ├─ completion-check-agent (验证完整性)
  ├─ doc-sync-agent (同步文档)
  ├─ code-review-agent (审核代码)
  └─ code-generation-agent (生成代码)

反馈循环:
  各Agent → 执行结果 → workflow-orchestrator-agent
  → 更新状态 → 推荐下一步
```

### 9.2 调用时机

```bash
每天开始:
  "开始今天的工作"
  → workflow-orchestrator-agent

继续项目:
  "继续项目"
  "今天做什么"
  → workflow-orchestrator-agent

需要协调:
  "完成这个模块"
  → workflow-orchestrator-agent 自动协调多个Agent

生成日报:
  "生成工作日报"
  "今天完成了什么"
  → workflow-orchestrator-agent
```

---

## 10. 未来增强

### 10.1 短期

```yaml
多项目管理:
  - 支持同时管理多个项目
  - 跨项目任务协调
  - 资源分配优化

团队协作:
  - 多人任务分配
  - 团队进度汇总
  - 协作工作流
```

### 10.2 中期

```yaml
AI助手集成:
  - 与外部AI服务集成
  - 智能任务分解
  - 自动化测试

数据分析:
  - 工作效率分析
  - 时间使用统计
  - 改进建议
```

### 10.3 长期

```yaml
自主学习:
  - 从历史数据学习
  - 优化工作流
  - 预测性建议

完全自动化:
  - 自主决策和执行
  - 最小化人工干预
  - 智能项目管理
```

---

## 11. 总结

### 11.1 核心价值

这个Agent将:
- ✅ 智能分析项目状态
- ✅ 自动推荐下一步操作
- ✅ 协调多个Agent工作
- ✅ 生成工作日报
- ✅ 实现无缝工作流

### 11.2 与工作流的契合

**中心协调者**:
```
用户 → workflow-orchestrator-agent → 其他Agent
      ↓ 分析状态
      ↓ 推荐操作
      ↓ 协调执行
      ↓ 生成报告
```

**一键启动**:
```
"开始工作" → 自动分析 → 自动推荐 → 自动执行
```

### 11.3 立即可用

- 基于现有的Agent系统
- 可以立即实施
- 提升整体工作效率

---

**设计完成时间**: 2025-01-11
**设计人**: 老黑(Claude)
**状态**: ✅ 设计完成,等待实施
**下一步**: 实施后立即测试

---

## 🚀 准备实施

设计方案已完成!

**核心特点**:
1. 智能状态分析
2. 上下文感知推荐
3. 多Agent协调
4. 工作日报生成
5. 一键启动工作流

**预计工作量**: 3-3.5小时

**准备开始实施!** 🎯
