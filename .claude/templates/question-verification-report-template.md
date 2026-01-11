# 问题清单核实报告模板

> **模板版本**: v1.0
> **创建时间**: 2025-01-11
> **用途**: question-verification-agent 生成核实报告的标准格式

---

# 🔍 问题清单核实报告

**核实时间**: {TIMESTAMP}
**问题清单**: {FILE_PATH}
**问题总数**: {TOTAL}

---

## 📊 核实结果统计

| 类别 | 数量 | 占比 |
|------|------|------|
| ✅ 已在其他文档确认 | {CONFIRMED_COUNT} | {CONFIRMED_PCT}% |
| ⏳ 仍需讨论确认 | {UNCONFIRMED_COUNT} | {UNCONFIRMED_PCT}% |
| ⚠️ 发现冲突 | {CONFLICT_COUNT} | - |

---

## 📁 扫描的文档 ({SCANNED_DOCS_COUNT}个)

{# For each scanned document}
{#}. **{FILE_PATH}**
   - 类型: {TYPE}
   - 大小: {SIZE}
   - 扫描结果: {RESULT}

---

## ✅ 已在其他文档确认的问题 ({CONFIRMED_COUNT}个)

{# For each confirmed question}
### {QUESTION_NUMBER}. {QUESTION_TITLE}

**确认来源**: [{SOURCE_FILE}]({SOURCE_LINK})
**确认时间**: {CONFIRMATION_DATE}
**原文位置**: {LINE_NUMBER}行

**已确认方案**:
```
{CONFIRMATION_DETAILS}
```

**建议**: ✅ 无需讨论,直接同步状态

**操作**:
- [ ] 同步到当前问题清单
- [ ] 标记为 ✅ 已确认
- [ ] 添加确认来源链接

---

## ⏳ 仍需讨论的问题 ({UNCONFIRMED_COUNT}个)

{# For each unconfirmed question}
### {QUESTION_NUMBER}. {QUESTION_TITLE}

**问题描述**: {DESCRIPTION}

**建议**: ⏳ 需要讨论确认

**下一步**:
- 使用 `/discuss` 开始讨论
- 准备选项和推荐方案

---

## ⚠️ 发现的冲突 ({CONFLICT_COUNT}个)

{# If any conflicts found}
### 冲突: {QUESTION_TITLE}

**当前问题清单状态**: {CURRENT_STATUS}
**其他文档状态**: {OTHER_STATUS}

**冲突详情**:
```
{CONFLICT_DETAILS}
```

**建议**: 请人工审核是否采纳该确认

**操作**:
- [ ] 人工审核确认内容
- [ ] 决定采纳或重新讨论
- [ ] 记录决策理由

---

## 🔍 核实方法说明

### 搜索的关键词 ({KEYWORD_COUNT}个)

{# List keywords extracted from questions}
- {KEYWORD_1}
- {KEYWORD_2}
- ...

### 搜索的文档类型

1. **主问题汇总**
   - development/issues/questions.md

2. **其他问题清单**
   - development/issues/*questions*.md

3. **分析和总结文档**
   - development/analysis/*summary*.md
   - development/analysis/*confirmation*.md
   - development/analysis/*resolution*.md
   - development/analysis/*risk*.md

4. **开发日志**
   - development/logs/dev-log-*.md

5. **设计文档**
   - docs/design/*设计文档*.md

### 确认标记识别

识别以下标记为"已确认":
- ✅ (emoji checkmark)
- "已确认"
- "已确认方案"
- "确认时间"

---

## 🎯 建议操作

### 立即执行

1. **更新已确认问题** ({CONFIRMED_COUNT}个)
   ```bash
   # 自动更新
   /verify-questions --update {FILE_PATH}

   # 或手动更新
   标记为 ✅ 已确认
   添加确认来源链接
   同步确认内容
   ```

2. **讨论待确认问题** ({UNCONFIRMED_COUNT}个)
   ```bash
   # 开始讨论
   /discuss {FILE_PATH}

   # discussion-agent会自动跳过已确认问题
   ```

3. **解决冲突** ({CONFLICT_COUNT}个)
   ```bash
   # 人工审核
   查看冲突详情
   决定采纳或重新讨论
   记录决策理由
   ```

### 后续操作

1. **运行文档同步**
   ```bash
   /sync-docs
   ```

2. **验证模块完整性**
   ```bash
   /check-completion
   ```

3. **创建设计文档** (如果所有问题已确认)
   ```bash
   所有问题确认后即可开始设计文档
   ```

---

## 📈 质量评估

### 文档完整性

| 维度 | 得分 | 说明 |
|------|------|------|
| **确认覆盖率** | {COVERAGE_PCT}% | {CONFIRMED_COUNT}/{TOTAL} 问题已确认 |
| **文档一致性** | {CONSISTENCY_SCORE}/100 | 文档间交叉引用清晰度 |
| **可追溯性** | {TRACEABILITY_SCORE}/100 | 确认来源可追溯度 |

### 改进建议

{# If any issues found}
- {SUGGESTION_1}
- {SUGGESTION_2}
- ...

---

## 📝 核实日志

```
{TIMESTAMP} 开始核实
{TIMESTAMP} 扫描文档: {SCANNED_DOCS_COUNT}个
{TIMESTAMP} 提取问题: {TOTAL}个
{TIMESTAMP} 搜索关键词: {KEYWORD_COUNT}个
{TIMESTAMP} 发现已确认: {CONFIRMED_COUNT}个
{TIMESTAMP} 发现冲突: {CONFLICT_COUNT}个
{TIMESTAMP} 生成报告: 完成
```

---

## 🔗 相关文档

- **问题清单**: [{FILE_NAME}]({FILE_PATH})
- **核实Agent**: [.claude/agents/question-verification-agent.md](../../.claude/agents/question-verification-agent.md)
- **Hooks配置**: [.claude/hooks/question-list-hooks.md](../../.claude/hooks/question-list-hooks.md)

---

**报告生成时间**: {TIMESTAMP}
**Agent版本**: v1.0
**核实耗时**: {DURATION}

---

## 📋 批量更新清单

使用此清单进行批量更新问题清单状态:

### 已确认问题批量更新 ({CONFIRMED_COUNT}个)

{# Checkbox list for confirmed questions}
- [ ] {QUESTION_NUMBER}: {QUESTION_TITLE}
  - 状态: ⏳ → ✅
  - 添加: **确认来源**: [{SOURCE_FILE}]({SOURCE_LINK})
  - 添加: **确认时间**: {CONFIRMATION_DATE}
  - 添加: **已确认方案**: {CONFIRMATION_SUMMARY}

---

**更新完成标记**: [ ] 全部更新完成
**更新完成时间**: ___________
**更新执行人**: ___________
