# Hook集成指南 - Skill集成

> **更新时间**: 2025-01-11
> **目的**: 指导如何在各个Skill命令中集成Hook管理器

---

## 📋 需要集成的Skill列表

### 现有Skill命令

1. **/daily-push** ✅ (已是Agent,有Hook集成)
2. **/sync-docs** - 同步所有文档
3. **/check-progress** - 检查项目进度
4. **/verify-questions** - 核实问题状态
5. **/task-planner** - 任务计划管理
6. **/discuss** - 启动问题讨论
7. **/check-completion** - 检查模块完成度

---

## 🔧 Skill集成模式

### 标准集成流程

每个Skill命令的集成都遵循以下模式:

```yaml
1. Skill命令执行主逻辑
   ↓
2. 在关键节点触发Hook
   ↓
3. Hook执行增强功能
   ↓
4. 继续Skill执行
```

---

## 📝 /sync-docs 集成

### 集成位置

```python
def sync_docs_command():
    """
    /sync-docs 命令实现
    """
    print("🔄 开始同步文档...")

    # 执行同步逻辑
    synced_files = perform_sync()

    # 同步完成后触发文档质量检查Hook
    hook_manager.trigger("doc_quality_monitor", {
        "files": synced_files,
        "check_type": "post_sync"
    })

    print(f"✅ 同步完成! 已同步 {len(synced_files)} 个文件")

    # 如果同步发现问题,建议修复
    if quality_issues:
        suggest_fixes(quality_issues)
```

### 触发的Hook

1. **doc_quality_monitor** (文档同步后)
   - 检查同步后的文档质量
   - 检查版本号一致性
   - 检查交叉引用

---

## 📝 /check-progress 集成

### 集成位置

```python
def check_progress_command():
    """
    /check-progress 命令实现
    """
    # 获取当前进度
    progress = get_current_progress()

    # 显示进度报告
    display_progress_report(progress)

    # 检查是否达到里程碑
    if progress["percentage"] >= 50 and not milestone_notified("50%"):
        # 触发里程碑通知Hook
        hook_manager.trigger("milestone_notification", {
            "type": "phase_complete",
            "phase": "50%完成",
            "progress": progress
        })

        mark_milestone_notified("50%")
```

### 触发的Hook

1. **milestone_notification** (阶段性目标达成)
   - 50%进度达成
   - 75%进度达成
   - 100%进度达成

---

## 📝 /verify-questions 集成

### 集成位置

```python
def verify_questions_command():
    """
    /verify-questions 命令实现
    """
    print("🔍 开始核实问题状态...")

    # 执行核实逻辑
    verification_result = verify_question_status()

    # 显示核实报告
    display_verification_report(verification_result)

    # 如果发现问题需要确认,触发讨论Hook
    if verification_result["has_unconfirmed_questions"]:
        hook_manager.trigger("milestone_notification", {
            "type": "verification_warning",
            "unconfirmed_count": len(verification_result["unconfirmed"]),
            "suggestion": "继续讨论未确认的问题"
        })
```

### 触发的Hook

1. **milestone_notification** (发现问题警告)
   - 有未确认的问题
   - 建议继续讨论

---

## 📝 /task-planner 集成

### 集成位置

```python
def task_planner_command(user_input=None):
    """
    /task-planner 命令实现
    """
    # 生成任务清单
    task_list = generate_task_list(user_input)

    # 显示任务清单
    display_task_list(task_list)

    # 如果生成新任务,触发通知
    if task_list["new_tasks_created"]:
        hook_manager.trigger("milestone_notification", {
            "type": "task_plan_created",
            "task_count": len(task_list["tasks"]),
            "estimated_time": task_list["estimated_time"]
        })
```

### 触发的Hook

1. **milestone_notification** (任务计划生成)
   - 显示任务数量
   - 显示预估时间
   - 推荐开始执行

---

## 📝 /discuss 集成

### 集成位置

```python
def discuss_command(question_list=None):
    """
    /discuss 命令实现
    """
    # 启动discussion-agent
    print("🚀 启动问题讨论...")

    # discussion-agent内部会触发Hook
    # 这里不需要额外触发

    # 但可以在启动前触发准备通知
    hook_manager.trigger("milestone_notification", {
        "type": "discussion_started",
        "module": extract_module_name(question_list),
        "suggestion": "专注于回答问题,其他事情自动处理"
    })
```

### 触发的Hook

1. **milestone_notification** (讨论开始)
   - 提示用户专注讨论
   - 其他事情自动处理

---

## 📝 /check-completion 集成

### 集成位置

```python
def check_completion_command(module_name):
    """
    /check-completion 命令实现
    """
    # 检查模块完成度
    completion_result = check_module_completion(module_name)

    # 显示检查报告
    display_completion_report(completion_result)

    # 如果验证通过,触发里程碑通知
    if completion_result["verified"]:
        hook_manager.trigger("milestone_notification", {
            "type": "module_verified",
            "module": module_name,
            "completion_rate": completion_result["percentage"],
            "verification": completion_result
        })

        # 触发归档Hook
        hook_manager.trigger("agent_completion_archive", {
            "agent": "completion-check-agent",
            "module": module_name,
            "report": completion_result["report_path"]
        })
```

### 触发的Hook

1. **milestone_notification** (模块验证通过)
2. **agent_completion_archive** (归档验证报告)

---

## 🔔 Hook触发时机汇总

| Skill | 触发时机 | Hook类型 |
|-------|---------|---------|
| /sync-docs | 文档同步完成后 | doc_quality_monitor |
| /check-progress | 达到阶段性目标(50%/75%/100%) | milestone_notification |
| /verify-questions | 发现未确认问题时 | milestone_notification |
| /task-planner | 生成新任务计划时 | milestone_notification |
| /discuss | 讨论开始时 | milestone_notification |
| /check-completion | 模块验证通过时 | milestone_notification, agent_completion_archive |

---

## 🧪 Skill集成测试

### 测试步骤

1. **测试/sync-docs**
   ```bash
   /sync-docs
   ```
   验证:
   - 文档同步完成
   - 触发doc_quality_monitor Hook
   - 显示质量检查结果

2. **测试/check-progress**
   ```bash
   /check-progress
   ```
   验证:
   - 显示进度报告
   - 如果达到50%,触发里程碑通知
   - Windows通知弹出 + 音效

3. **测试/task-planner**
   ```bash
   /task-planner "创建daily-push-agent"
   ```
   验证:
   - 生成任务清单
   - 触发里程碑通知
   - Windows通知弹出

---

## 💡 Skill集成最佳实践

### 1. Hook调用时机

```yaml
✅ 推荐:
  - 在命令完成时触发Hook
  - 在达到里程碑时触发Hook
  - 在需要用户注意时触发Hook

❌ 不推荐:
  - 在命令开始前触发(除非是准备通知)
  - 在命令执行过程中频繁触发
  - 在错误时触发Hook(除非是专门的错误Hook)
```

### 2. Hook与Agent的区别

```yaml
Agent:
  - 复杂的多步骤流程
  - 需要状态管理
  - 需要用户交互
  - Hook集成在关键里程碑

Skill命令:
  - 相对简单的操作
  - 通常一次性完成
  - Hook集成在命令完成时
```

### 3. Hook数据传递

```python
# ✅ 推荐: 传递完整上下文
hook_manager.trigger("milestone_notification", {
    "type": "module_verified",
    "module": module_name,
    "completion_rate": 100,
    "verification": {
        "score": 95,
        "issues": [],
        "checks_passed": 10
    }
})

# ❌ 不推荐: 传递不完整的信息
hook_manager.trigger("milestone_notification", {
    "type": "module_verified",
    "module": module_name
})
```

---

## 📚 相关文档

- **Hook管理器**: [.claude/hooks/hook-manager.md](../hooks/hook-manager.md)
- **Agent集成指南**: [.claude/agents/hook-integration-guide.md](hook-integration-guide.md)
- **Hook配置总结**: [.claude/hooks/hooks-configuration-summary.md](../hooks/hooks-configuration-summary.md)

---

## ✅ Skill集成检查清单

每个Skill集成完成后,检查以下项目:

- [ ] Hook调用代码已添加
- [ ] Hook调用时机正确
- [ ] 传递的数据完整
- [ ] 集成说明已添加
- [ ] 测试通过
- [ ] Windows通知正常工作
- [ ] 音效正常播放

---

**创建时间**: 2025-01-11
**版本**: v1.0
**状态**: ✅ Skill集成指南已创建
**下一步**: 更新工作流文档,测试Hook系统