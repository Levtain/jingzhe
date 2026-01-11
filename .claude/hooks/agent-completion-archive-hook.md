# Agent完成报告自动归档Hook

> **Hook名称**: agent-completion-archive-hook
> **版本**: v1.0
> **创建时间**: 2025-01-11
> **目的**: 自动归档Agent完成报告,更新总体进度

---

## 🎯 核心功能

### 1. 检测新的完成报告

**触发条件**:
```yaml
检测事件:
  - development/testing/*completion-summary*.md 文件创建
  - development/testing/*complete*.md 文件创建
  - development/*完成报告*.md 文件创建
  - development/*summary*.md 文件创建

触发时机:
  - Agent任务完成时
  - 模块验收通过时
  - 里程碑达成时
```

### 2. 自动归档到标准位置

**归档规则**:
```yaml
目标位置:
  development/archive/completion-reports/
  ├── agent-completion-reports/
  │   ├── design-audit-agent-completion-YYYY-MM-DD.md
  │   ├── code-generation-agent-completion-YYYY-MM-DD.md
  │   └── ...
  ├── module-completion-reports/
  │   ├── game-submission-system-completion-YYYY-MM-DD.md
  │   ├── scoring-system-completion-YYYY-MM-DD.md
  │   └── ...
  └── milestone-reports/
      ├── phase1-complete-YYYY-MM-DD.md
      └── ...

归档内容:
  - 原始报告完整内容
  - 归档时间戳
  - Agent名称/模块名称
  - 完成度统计
  - 关键指标
```

### 3. 更新总体进度

**进度跟踪**:
```yaml
进度文件: development/progress/overall-progress.md

更新内容:
  - 已完成的Agent数量
  - 已完成的模块数量
  - 整体完成度百分比
  - 最后更新时间

进度指标:
  - Agent开发进度: X/6 (设计X个,开发X个)
  - 模块开发进度: X/Y (X个完成,Y个总数)
  - 文档完成度: X%
  - 代码完成度: X%
```

---

## 🔧 核心函数

### detect_completion_reports()

```python
def detect_completion_reports():
    """
    检测新增的完成报告
    """
    new_reports = []

    # 扫描testing目录
    testing_files = glob("development/testing/*completion*.md")
    for file_path in testing_files:
        if is_new_file(file_path):
            new_reports.append({
                "type": "agent_completion",
                "path": file_path,
                "created_time": get_file_created_time(file_path)
            })

    # 扫描其他目录
    all_reports = glob("development/**/*complete*.md", recursive=True)
    for file_path in all_reports:
        if is_new_file(file_path) and "/archive/" not in file_path:
            new_reports.append({
                "type": "module_completion",
                "path": file_path,
                "created_time": get_file_created_time(file_path)
            })

    return new_reports
```

### archive_report(report_info)

```python
def archive_report(report_info):
    """
    归档报告到标准位置
    """
    # 读取报告内容
    content = read_file(report_info["path"])

    # 提取元数据
    metadata = extract_metadata(content)

    # 生成归档文件名
    if report_info["type"] == "agent_completion":
        agent_name = extract_agent_name(content)
        archive_name = f"{agent_name}-completion-{date.today()}.md"
        archive_path = f"development/archive/completion-reports/agent-completion-reports/{archive_name}"
    else:
        module_name = extract_module_name(content)
        archive_name = f"{module_name}-completion-{date.today()}.md"
        archive_path = f"development/archive/completion-reports/module-completion-reports/{archive_name}"

    # 添加归档元数据
    archived_content = add_archive_metadata(content, metadata)

    # 写入归档文件
    write_file(archive_path, archived_content)

    return archive_path
```

### update_overall_progress()

```python
def update_overall_progress():
    """
    更新总体进度
    """
    progress_file = "development/progress/overall-progress.md"

    # 统计已完成的Agent
    agent_reports = glob("development/archive/completion-reports/agent-completion-reports/*.md")
    completed_agents = len(agent_reports)

    # 统计已完成的模块
    module_reports = glob("development/archive/completion-reports/module-completion-reports/*.md")
    completed_modules = len(module_reports)

    # 计算整体完成度
    total_agents = 6  # 已知总数
    total_modules = 10  # 预估总数

    agent_progress = f"{completed_agents}/{total_agents}"
    module_progress = f"{completed_modules}/{total_modules}"

    overall_percentage = (completed_agents + completed_modules) / (total_agents + total_modules) * 100

    # 生成进度报告
    progress_report = f"""# 总体进度报告

**更新时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 整体进度

**完成度**: {overall_percentage:.1f}%

### Agent开发进度
- 已完成: {completed_agents}个
- 总数: {total_agents}个
- 进度: {agent_progress}

### 模块开发进度
- 已完成: {completed_modules}个
- 总数: {total_modules}个
- 进度: {module_progress}

---

## ✅ 已完成的Agent

{format_agent_list(agent_reports)}

---

## ✅ 已完成的模块

{format_module_list(module_reports)}

---

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Hook版本**: v1.0
"""

    # 写入进度文件
    write_file(progress_file, progress_report)
```

---

## 📋 Hook触发配置

### 在Agent完成时触发

```yaml
触发位置:
  - design-audit-agent 完成时
  - code-generation-agent 完成时
  - completion-check-agent 验证通过时

触发方式:
  - 在Agent的完成逻辑中调用
  - 生成completion-summary后自动触发

示例:
  # 在Agent完成逻辑中
  if task_completed:
      generate_completion_summary()
      trigger_hook("agent-completion-archive")
```

### 在模块验收通过时触发

```yaml
触发位置:
  - completion-check-agent 验证通过
  - 所有核心问题确认完成

触发方式:
  - completion-check-agent内部触发
  - 检测到100%完成时自动触发

示例:
  # completion-check-agent逻辑
  if completion_percentage == 100:
      generate_completion_report()
      trigger_hook("agent-completion-archive")
```

---

## 📊 输出格式

### 归档报告格式

```markdown
# Agent完成报告 - design-audit-agent

> **归档时间**: 2025-01-11 14:30:00
> **Agent名称**: design-audit-agent
> **完成时间**: 2025-01-11 14:00:00
> **归档来源**: development/testing/design-audit-agent-completion-summary_2025-01-11.md

---

## 📊 完成统计

**任务总数**: 10个
**已完成**: 10个
**完成度**: 100%

**关键指标**:
- 设计文档质量得分: 95/100
- 问题确认完成度: 100%
- 文档完整性: 100%
- 交叉引用正确性: 98%

---

## 📝 原始报告

[这里插入原始completion-summary的完整内容]

---

## 🔗 相关文档

- **Agent定义**: [.claude/agents/design-audit-agent.md](../../.claude/agents/design-audit-agent.md)
- **测试报告**: [development/testing/design-audit-agent-test-report_2025-01-11.md](../testing/design-audit-agent-test-report_2025-01-11.md)

---

**归档执行人**: agent-completion-archive-hook
**归档执行时间**: 2025-01-11 14:30:00
```

### 进度更新通知

```markdown
📊 **进度更新通知**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ **新完成的模块**: 游戏提交系统

完成时间: 2025-01-11 14:00:00
完成度: 100% (9/9核心问题已确认)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 **整体进度更新**:

Agent开发进度: 6/6 (100%) ✅
模块开发进度: 3/10 (30%)

总体完成度: 45% (9/20)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 **归档位置**:
development/archive/completion-reports/module-completion-reports/game-submission-system-completion-2025-01-11.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 **下一步建议**:
- 继续下一个模块的开发
- 或查看总体进度: /check-progress
```

---

## 💡 核心价值

### 改进前

```yaml
手动归档流程:
  1. Agent完成,生成报告
  2. 报告散落在各处
  3. 需要手动整理归档
  4. 需要手动更新进度
  5. 容易遗漏或重复

问题:
  - 报告分散,难以查找
  - 进度统计不准确
  - 缺乏系统性管理
```

### 改进后

```yaml
自动归档流程:
  1. Agent完成,生成报告
  2. Hook自动检测
  3. 自动归档到标准位置
  4. 自动更新总体进度
  5. 生成进度通知

优势:
  - 报告集中管理
  - 进度实时准确
  - 系统化追踪
  - 零手动操作
```

---

## ⚙️ 配置选项

### Hook配置

```json
{
  "hooks": {
    "agent-completion-archive": {
      "enabled": true,
      "auto_archive": true,
      "update_progress": true,
      "archive_dir": "development/archive/completion-reports",
      "progress_file": "development/progress/overall-progress.md",
      "notification": true
    }
  }
}
```

---

## 🔗 与其他Hook的配合

### doc-sync-hook

```yaml
配合流程:
  1. 问题清单100%完成
  2. doc-sync-hook同步文档
  3. 生成完成报告
  4. agent-completion-archive-hook归档报告
  5. 更新总体进度
```

### milestone-notification-hook

```yaml
配合流程:
  1. 模块100%完成
  2. agent-completion-archive-hook归档
  3. milestone-notification-hook发送通知
  4. 推荐下一步操作
```

---

## ✅ 总结

**核心功能**:
1. 检测新的完成报告
2. 自动归档到标准位置
3. 更新总体进度
4. 生成进度通知

**核心价值**:
- 报告集中管理
- 进度实时准确
- 系统化追踪
- 零手动操作

**实施建议**:
- 在所有Agent完成逻辑中集成
- 确保归档目录结构清晰
- 定期检查进度文件准确性

---

**创建时间**: 2025-01-11
**版本**: v1.0
**状态**: ✅ Hook已定义
**下一步**: 集成到各个Agent的完成逻辑中