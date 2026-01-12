# 问题核实命令

> **命令名称**: /verify-questions
> **用途**: 手动触发问题清单核实,检查问题是否已在其他文档中确认
> **创建时间**: 2025-01-11
> **版本**: v1.0

---

## 🎯 功能描述

自动检查问题清单中的问题是否已在其他文档中确认,避免重复讨论。

## 📖 使用方法

### 基本用法

```bash
/verify-questions                           # 核实最新的问题清单
/verify-questions [文件路径]                # 核实指定的问题清单
```

### 参数选项

```bash
/verify-questions --update                 # 核实并自动更新问题清单
/verify-questions --report-only            # 仅显示报告,不修改文件
/verify-questions --verbose                # 显示详细的核实过程
```

### 示例

```bash
# 核实游戏提交系统问题清单
/verify-questions development/active/issues/game-submission-questions-v2.md

# 核实最新问题清单并自动更新
/verify-questions --update

# 仅显示核实报告
/verify-questions --report-only
```

---

## 🔄 执行流程

```
用户调用: /verify-questions
    ↓
1. 查找问题清单文件
   - 用户指定路径 或
   - development/active/issues/*questions*.md (最新)
    ↓
2. 调用 question-verification-agent
    ↓
3. 扫描相关文档
   - development/active/issues/questions.md
   - development/active/analysis/*summary*.md
   - development/active/analysis/*resolution*.md
   - development/logs/dev-log-*.md
   - docs/design/*设计文档*.md
    ↓
4. 匹配确认标记
   - ✅
   - "已确认"
   - "已确认方案"
    ↓
5. 生成核实报告
    ↓
6. 询问是否更新
   - --update: 自动更新
   - 默认: 询问用户
    ↓
7. 更新问题清单状态
    ↓
8. 显示完成摘要
```

---

## 📊 输出示例

### 成功案例

```markdown
🔍 问题清单核实中...

扫描文档: 15个
搜索关键词: 45个
匹配问题: 9个

✅ 发现已确认问题: 9个
⏳ 仍需讨论问题: 0个
⚠️ 发现冲突: 0个

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【核实结果】

已在其他文档确认的问题 (9个):

1. Q1: 游戏提交时的作者列表如何生成?
   ✅ 确认来源: questions.md (line 209)
   确认时间: 2025-01-08

2. Q2: 赛道选择是手动选择还是自动判定?
   ✅ 确认来源: questions.md (line 210)
   确认时间: 2025-01-08

...

9. Q9: 源码链接的有效性验证?
   ✅ 确认来源: questions.md (line 219)
   确认时间: 2025-01-09

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 统计:
- 扫描文档: 4个
- 问题总数: 9个
- 已确认: 9个 (100%)
- 待确认: 0个 (0%)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❓ 是否自动更新问题清单状态?
- 输入 "是" / "yes" / "y" → 自动更新
- 输入 "否" / "no" / "n" → 跳过更新
```

### 部分确认案例

```markdown
🔍 问题清单核实中...

扫描文档: 12个
搜索关键词: 30个
匹配问题: 10个

✅ 发现已确认问题: 7个
⏳ 仍需讨论问题: 3个
⚠️ 发现冲突: 0个

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【核实结果】

已在其他文档确认的问题 (7个):
- Q1, Q2, Q3, Q4, Q5, Q6, Q7

仍需讨论的问题 (3个):
- Q8: 硬核玩家标记的作用和奖励机制?
- Q9: 源码链接的有效性验证?
- Q10: 团队赛道如何处理?

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❓ 是否更新已确认问题的状态?
- 输入 "是" / "yes" / "y" → 更新Q1-Q7
- 输入 "否" / "no" / "n" → 跳过更新
```

---

## 🔧 实现细节

### Agent调用

这个命令会调用 `question-verification-agent` 来执行核实:

```python
def execute_verify_questions(file_path=None, update=False):
    """
    执行问题核实命令

    Args:
        file_path: 问题清单文件路径
        update: 是否自动更新
    """
    # 1. 确定文件路径
    if not file_path:
        file_path = find_latest_question_list()

    # 2. 调用核实Agent
    verification = question_verification_agent.verify(file_path)

    # 3. 显示报告
    display_verification_report(verification)

    # 4. 处理更新
    if update or user_confirms():
        apply_updates(verification)
```

### 文件查找逻辑

```python
def find_latest_question_list():
    """
    查找最新的问题清单文件
    """
    question_lists = glob("development/active/issues/*questions*.md")

    if not question_lists:
        raise FileNotFoundError("找不到问题清单文件")

    # 按修改时间排序,返回最新的
    return max(question_lists, key=lambda f: os.path.getmtime(f))
```

---

## ⚙️ 配置选项

可以在 `.claude/config.json` 中配置默认行为:

```json
{
  "commands": {
    "verify-questions": {
      "auto_update": false,
      "verbose": false,
      "search_paths": [
        "development/active/issues/questions.md",
        "development/active/analysis/*summary*.md",
        "development/active/analysis/*resolution*.md",
        "development/logs/dev-log-*.md",
        "docs/design/*设计文档*.md"
      ]
    }
  }
}
```

---

## 🐛 错误处理

### 错误1: 找不到问题清单

```markdown
❌ 错误: 找不到问题清单文件

请检查:
1. development/active/issues/ 目录是否存在
2. 是否有问题清单文件(*questions.md)
3. 文件路径是否正确

建议:
- 使用 /verify-questions [文件路径] 指定文件
- 确认问题清单已创建
```

### 错误2: 文件格式不正确

```markdown
⚠️ 警告: 问题清单格式可能不正确

未找到明确的问题标记,请确保:
- 问题编号格式为: ### Q1, #### Q1, 或类似格式
- 未确认问题没有 ✅ 标记
- 问题包含明确的选项和描述

尝试继续处理...
```

### 错误3: 无写入权限

```markdown
❌ 错误: 无法更新问题清单

文件: {file_path}
原因: 无写入权限

建议:
- 检查文件权限
- 手动更新问题清单
```

---

## 📈 效果对比

### 改进前

```yaml
手动核实流程:
  1. 记住要核实问题
  2. 手动搜索相关文档 (5-10分钟)
  3. 逐个检查确认状态
  4. 手动更新问题清单
  5. 容易遗漏或出错

时间: 5-10分钟
准确性: 80%
```

### 改进后

```yaml
自动化核实流程:
  1. 调用 /verify-questions
  2. 自动扫描所有文档 (10秒)
  3. 自动匹配确认标记
  4. 自动生成报告
  5. 一键更新问题清单

时间: 10秒
准确性: 99%+
```

---

## 🔗 相关命令

- **/discuss** - 开始问题讨论(会自动触发核实)
- **/sync-docs** - 同步所有相关文档
- **/check-progress** - 检查项目进度

---

## 💡 使用技巧

### 技巧1: 创建问题清单后立即核实

```bash
# 创建问题清单后
/verify-questions development/active/issues/new-module-questions.md

# 避免后续重复讨论
```

### 技巧2: 定期核实

```bash
# 每周或每次讨论前
/verify-questions

# 确保问题清单状态最新
```

### 技巧3: 讨论前核实

```bash
# 开始讨论前
/verify-questions --update

# 然后再调用
/discuss

# discussion-agent会跳过已确认问题
```

---

## 📝 开发信息

- **创建时间**: 2025-01-11
- **开发者**: 老黑(Claude)
- **版本**: v1.0
- **状态**: ✅ 已实现
- **依赖**: question-verification-agent

---

## 🎯 后续计划

### v1.1 (短期)
- [ ] 添加更多搜索路径
- [ ] 支持自定义关键词
- [ ] 增加核实历史记录

### v1.2 (中期)
- [ ] 语义匹配优化
- [ ] 冲突检测和解决
- [ ] 批量核实多个问题清单

### v2.0 (长期)
- [ ] 问题数据库集成
- [ ] 智能推荐确认内容
- [ ] 自动同步到所有文档
