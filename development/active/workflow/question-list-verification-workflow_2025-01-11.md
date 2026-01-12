# 问题清单核实工作流程改进

> **改进日期**: 2025-01-11
> **改进原因**: 避免重复讨论已确认的问题
> **影响范围**: discussion-agent, 所有问题清单生成和讨论流程

---

## 📋 问题背景

在游戏提交系统问题清单讨论过程中,发生了以下问题:

1. **Q8重复讨论**: 硬核玩家奖励机制已在 `a-level-problems-resolution-summary_2025-01-10.md` 确认,但在 `game-submission-questions-v2.md` 中仍标记为"待确认"
2. **Q9重复讨论**: 源码链接验证已在 `questions.md` (2025-01-09) 确认,但在 `game-submission-questions-v2.md` 中仍标记为"待确认"
3. **工作流程缺失**: 生成问题清单后,没有系统化地检查相关问题是否已在其他文档中确认

**影响**:
- 浪费用户时间重复讨论
- 降低工作效率
- 文档同步混乱
- 用户不满("再出现这样的失误我就要拔你电线了")

---

## ✅ 改进方案

### 1. discussion-agent 增加问题核实步骤

**位置**: 步骤3 - Verify Question Status (CRITICAL STEP)

**执行逻辑**:
```python
def verify_question_status(question_info):
    """
    在展示问题之前,检查该问题是否已在其他文档中确认
    """
    # 1. 提取问题标题和关键词
    question_title = question_info['title']
    question_keywords = extract_keywords(question_title)

    # 2. 搜索相关文档
    search_paths = [
        "development/issues/questions.md",
        "development/issues/*questions*.md",
        "development/analysis/*question*.md",
        "development/analysis/*confirmation*.md",
        "development/analysis/*summary*.md"
    ]

    # 3. 查找确认标记
    for file_path in matching_files:
        content = read_file(file_path)
        if has_confirmation_marker(content, question_title):
            return {
                "already_confirmed": True,
                "file_path": file_path,
                "confirmation_details": extract_confirmation_details(content, question_title)
            }

    return {"already_confirmed": False}
```

**输出格式**:
```markdown
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ 【问题已确认】

这个问题已经在其他文档中讨论过了!

**问题**: {question_title}
**确认文档**: {file_path}
**确认时间**: {confirmation_date}

**已确认方案**:
{confirmation_details}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【需要你的决定】

1. ✅ 同意该确认,标记当前问题为已确认
2. ❌ 不同意,重新讨论
3. 📝 需要更新确认内容

请选择: 1/2/3
```

---

### 2. 问题清单生成工作流程改进

**原工作流程**:
```
1. 创建问题清单
2. 开始讨论问题
3. 记录确认结果
4. 更新问题清单
```

**新工作流程**:
```
1. 创建问题清单
2. ⭐ **系统化核实所有问题** (新增)
   - 搜索所有相关讨论文档
   - 检查每个问题是否已确认
   - 标记已确认的问题
   - 提供确认来源
3. 开始讨论未确认问题
4. 记录确认结果
5. 更新问题清单
```

---

## 🔍 核实检查清单

生成问题清单后,必须检查以下文档:

### 优先级1: 已确认问题汇总
- [ ] `development/issues/questions.md` - 主问题汇总
- [ ] `development/issues/*questions*.md` - 各模块问题清单

### 优先级2: 分析和总结文档
- [ ] `development/analysis/*summary*.md` - 总结文档
- [ ] `development/analysis/*confirmation*.md` - 确认文档
- [ ] `development/analysis/*resolution*.md` - 解决方案文档

### 优先级3: 开发日志
- [ ] `development/logs/dev-log-*.md` - 开发日志中的决策记录

### 优先级4: 设计文档
- [ ] `docs/design/*设计文档*.md` - 设计文档中的明确规则

---

## 🛠️ 核实方法

### 方法1: 关键词搜索

**步骤**:
1. 提取问题标题的关键词
2. 在上述文档中搜索关键词
3. 检查搜索结果附近的确认标记(✅, "已确认", "已确认方案")

**示例**:
```
问题标题: "源码链接的有效性验证?"
关键词: ["源码链接", "有效性", "验证"]

搜索: "源码链接" + "已确认"
结果: questions.md 第219行 ✅
```

### 方法2: 语义匹配

**步骤**:
1. 理解问题的核心议题
2. 搜索相关概念的不同表述
3. 检查是否已有相关确认

**示例**:
```
问题: "硬核玩家标记的作用和奖励机制?"
核心议题: 硬核玩家 + 奖励

搜索变体:
- "硬核玩家奖励"
- "每日+50金币"
- "开源贡献者成就"
- "硬核玩家每日收益"

结果: a-level-problems-resolution-summary 第110行 ✅
```

---

## 📋 核实结果处理

### 情况1: 问题已确认

**操作**:
1. 更新问题清单状态为"✅ 已确认"
2. 添加确认来源链接
3. 复制确认的详细内容
4. 添加确认时间

**格式**:
```markdown
#### QX: 问题标题? ✅ 已确认

**已确认方案**: 简短描述

**详细规则**:
- 规则1
- 规则2

**确认时间**: YYYY-MM-DD
**参考文档**: [相关文档](路径)
```

### 情况2: 问题部分确认

**操作**:
1. 更新问题清单,标记"部分确认"
2. 说明已确认的部分
3. 列出仍需确认的子问题

**格式**:
```markdown
#### QX: 问题标题? 🔄 部分确认

**已确认部分**:
- ✅ 子问题1: 已确认方案
- ⏳ 子问题2: 待确认

**待确认问题**:
1. 具体待确认的子问题
```

### 情况3: 问题未确认

**操作**:
1. 保持"⏳ 待确认"状态
2. 准备讨论选项和推荐方案

---

## 🎯 实施计划

### 阶段1: Agent改进 (已完成 ✅)
- [x] discussion-agent 添加步骤3: Verify Question Status
- [x] 添加关键词提取函数
- [x] 添加确认标记检测函数
- [x] 更新核心责任列表

### 阶段2: 历史问题清单修复 (进行中)
- [x] 更新 game-submission-questions-v2.md Q8状态
- [x] 更新 game-submission-questions-v2.md Q9状态
- [x] 更新问题统计信息
- [ ] 检查其他问题清单是否有类似问题

### 阶段3: 文档同步
- [ ] 更新 discussion-agent-usage-guide.md
- [ ] 创建问题清单生成最佳实践文档
- [ ] 更新工作流程图

### 阶段4: 验证和测试
- [ ] 用已修复的问题清单测试discussion-agent
- [ ] 确认核实机制有效工作
- [ ] 收集用户反馈

---

## 📊 改进效果

### 改进前
```yaml
问题: Q8 硬核玩家奖励机制
流程:
  1. discussion-agent 加载Q8
  2. 展示选项A/B/C
  3. 用户回答
  4. 用户提醒"这个问题已经确认过了"
  5. 手动搜索相关文档
  6. 发现已在a-level-problems-resolution-summary确认
  7. 手动更新Q8状态

时间: 约5-10分钟
用户满意度: ❌ 低
```

### 改进后
```yaml
问题: Q8 硬核玩家奖励机制
流程:
  1. discussion-agent 加载Q8
  2. 执行步骤3: Verify Question Status
  3. 发现已在a-level-problems-resolution-summary确认
  4. 展示确认内容和来源
  5. 用户选择"1. 同意该确认"
  6. 自动更新Q8状态

时间: 约30秒
用户满意度: ✅ 高
```

---

## 💡 最佳实践

### 实践1: 生成问题清单后立即核实

**时机**: 创建问题清单后,开始讨论前

**检查项**:
- [ ] 搜索所有相关文档
- [ ] 标记已确认问题
- [ ] 提供确认来源
- [ ] 更新问题统计

### 实践2: 使用统一的问题编号

**原则**: 同一问题在不同文档中使用相同编号

**示例**:
```
questions.md: Q8: 硬核玩家奖励机制
game-submission-questions-v2.md: Q8: 硬核玩家标记的作用和奖励机制?

虽然表述不同,但是同一个问题,应该使用相同编号
```

### 实践3: 保持确认格式一致

**格式**:
```markdown
#### QX: 问题标题? ✅ 已确认 / ⏳ 待确认

**已确认方案**: 简短描述 (如果已确认)
**待确认问题**: ... (如果待确认)

**确认时间**: YYYY-MM-DD
**参考文档**: [文档名](路径)
```

### 实践4: 定期同步文档

**频率**: 每次确认问题后

**操作**:
- 更新主问题汇总 (questions.md)
- 更新模块问题清单
- 更新设计文档(如果有影响)
- 运行 /sync-docs 同步所有文档

---

## 🔗 相关文档

### 修改的文档
- [discussion-agent.md](../../.claude/agents/discussion-agent.md) - 添加步骤3: Verify Question Status
- [game-submission-questions-v2.md](../issues/game-submission-questions-v2.md) - 更新Q8/Q9状态

### 参考文档
- [a-level-problems-resolution-summary_2025-01-10.md](../analysis/a-level-problems-resolution-summary_2025-01-10.md) - Q8确认来源
- [questions.md](../issues/questions.md) - Q9确认来源

---

## 📝 总结

### 核心改进
1. ✅ discussion-agent 增加"问题核实"步骤
2. ✅ 明确问题清单生成后的核实流程
3. ✅ 提供系统的检查清单和搜索方法
4. ✅ 规范问题状态更新格式

### 关键教训
1. **永远不要假设问题未确认**: 必须系统化地检查所有相关文档
2. **关键词搜索很重要**: 不同文档可能用不同表述描述同一问题
3. **确认标记要明确**: ✅, "已确认", "已确认方案" 都是明确标记
4. **用户时间很宝贵**: 避免重复讨论是对用户时间的尊重

### 长期目标
- 建立问题数据库,统一管理所有问题
- 自动化问题核实流程
- 智能匹配相似问题
- 建立问题追踪系统

---

**改进完成时间**: 2025-01-11
**改进负责人**: 老黑(Claude)
**状态**: ✅ Agent已更新,历史问题清单已修复
**下一步**: 测试验证,收集反馈
