# Hook集成指南 - Agent集成

> **更新时间**: 2025-01-11
> **目的**: 指导如何在各个Agent中集成Hook管理器

---

## 📋 需要集成的Agent列表

### 已完成集成 ✅

1. **discussion-agent** ✅
   - 集成点: 所有问题确认完成时
   - 触发Hook: milestone_notification, auto_doc_sync

### 待集成Agent

2. **completion-check-agent**
3. **code-generation-agent**
4. **code-review-agent**
5. **design-audit-agent**
6. **workflow-orchestrator-agent**

---

## 🔧 集成步骤

### 标准集成流程

每个Agent的集成都遵循以下步骤:

```yaml
1. 在Agent文档中添加Hook导入
   from .claude.hooks.hook_manager import hook_manager

2. 在适当的位置调用hook_manager.trigger()
   hook_manager.trigger("hook_name", data)

3. 添加Hook集成说明文档
   - 触发时机
   - 触发条件
   - 传递的数据
   - 预期效果
```

---

## 📝 completion-check-agent 集成

### 集成位置

```python
def verify_module_completion(module_name):
    """
    验证模块完成度
    """
    # ... 验证逻辑 ...

    if verification_passed:
        # 🔔 触发里程碑通知Hook
        hook_manager.trigger("milestone_notification", {
            "type": "module_verified",
            "module": module_name,
            "verification": verification_result,
            "completion_rate": 100
        })

        # 🔔 触发Agent完成报告归档Hook
        hook_manager.trigger("agent_completion_archive", {
            "agent": "completion-check-agent",
            "module": module_name,
            "report": verification_report_path
        })
```

### 触发的Hook

1. **milestone_notification** (模块验证通过)
   - Windows通知 + 音效
   - 显示验证结果
   - 推荐下一步操作

2. **agent_completion_archive** (验证完成)
   - 归档验证报告
   - 更新总体进度

---

## 📝 code-generation-agent 集成

### 集成位置

```python
def complete_code_generation(module_name):
    """
    完成代码生成
    """
    # ... 生成逻辑 ...

    if code_generated:
        # 🔔 触发里程碑通知Hook
        hook_manager.trigger("milestone_notification", {
            "type": "code_generation_completed",
            "module": module_name,
            "files": generated_files,
            "lines_of_code": total_lines
        })

        # 🔔 触发Agent完成报告归档Hook
        hook_manager.trigger("agent_completion_archive", {
            "agent": "code-generation-agent",
            "module": module_name,
            "report": generation_report_path
        })
```

### 触发的Hook

1. **milestone_notification** (代码生成完成)
2. **agent_completion_archive** (归档生成报告)

---

## 📝 code-review-agent 集成

### 集成位置

```python
def complete_code_review(module_name):
    """
    完成代码审核
    """
    # ... 审核逻辑 ...

    if review_completed:
        # 🔔 触发里程碑通知Hook
        hook_manager.trigger("milestone_notification", {
            "type": "code_review_completed",
            "module": module_name,
            "issues_found": issue_count,
            "issues_fixed": fixed_count
        })
```

### 触发的Hook

1. **milestone_notification** (代码审核完成)

---

## 📝 design-audit-agent 集成

### 集成位置

```python
def complete_design_audit(module_name):
    """
    完成设计审核
    """
    # ... 审核逻辑 ...

    if audit_completed:
        # 🔔 触发里程碑通知Hook
        hook_manager.trigger("milestone_notification", {
            "type": "design_audit_completed",
            "module": module_name,
            "audit_score": score,
            "issues": issues
        })
```

### 触发的Hook

1. **milestone_notification** (设计审核完成)

---

## 📝 workflow-orchestrator-agent 集成

### 集成位置

```python
def generate_daily_summary():
    """
    生成工作日报
    """
    # ... 生成逻辑 ...

    # 🔔 触发每日推送Hook
    hook_manager.trigger("daily_push", {
        "trigger": "daily_summary",
        "summary": daily_summary,
        "auto_commit": True
    })
```

### 触发的Hook

1. **daily_push** (生成日报时自动推送)
2. **milestone_notification** (阶段性目标达成)

---

## 🔔 Hook触发时机汇总

| Agent | 触发时机 | Hook类型 |
|-------|---------|---------|
| discussion-agent | 所有问题100%确认 | milestone_notification, auto_doc_sync |
| completion-check-agent | 模块验证通过 | milestone_notification, agent_completion_archive |
| code-generation-agent | 代码生成完成 | milestone_notification, agent_completion_archive |
| code-review-agent | 代码审核完成 | milestone_notification |
| design-audit-agent | 设计审核完成 | milestone_notification |
| workflow-orchestrator-agent | 生成日报 | daily_push, milestone_notification |

---

## ⚙️ Hook配置示例

### 全局配置 (.claude/hooks/hook-config.json)

```json
{
  "hooks_enabled": true,
  "log_hook_calls": true,
  "hooks": {
    "milestone-notification": {
      "enabled": true,
      "windows_notification": {
        "enabled": true,
        "use_sound": true,
        "sound_type": "achievement"
      }
    },
    "auto-doc-sync": {
      "enabled": true,
      "auto_sync": true
    },
    "agent-completion-archive": {
      "enabled": true,
      "auto_archive": true
    },
    "daily-push": {
      "enabled": true,
      "auto_commit": true,
      "time": "22:00"
    }
  }
}
```

---

## ✅ 集成检查清单

每个Agent集成完成后,检查以下项目:

- [ ] Hook导入语句已添加
- [ ] Hook调用代码已添加
- [ ] Hook集成说明已添加到Agent文档
- [ ] 触发时机明确
- [ ] 传递的数据格式正确
- [ ] Hook配置已添加到hook-config.json
- [ ] 测试Hook触发

---

## 🧪 测试Hook集成

### 测试步骤

1. **手动触发测试**
   ```python
   # 在Agent中手动触发Hook测试
   hook_manager.trigger("milestone_notification", {
       "type": "questions_completed",
       "module": "测试模块",
       "completion": {"total": 9, "confirmed": 9}
   })
   ```

2. **验证Windows通知**
   - 检查右下角是否弹出通知
   - 检查是否播放音效

3. **验证日志记录**
   - 检查Hook调用是否被记录
   - 检查执行结果是否正确

4. **验证Agent功能**
   - 完成Agent的正常流程
   - 验证Hook是否在正确的时机触发

---

## 💡 最佳实践

### 1. Hook调用时机

```yaml
✅ 推荐:
  - 在关键里程碑达成时触发
  - 在任务完成时触发
  - 在需要通知用户时触发

❌ 不推荐:
  - 在循环中频繁触发
  - 在错误处理中触发(除非是错误通知Hook)
  - 在调试时触发(会产生噪音)
```

### 2. 数据传递

```python
# ✅ 推荐: 清晰的数据结构
hook_manager.trigger("milestone_notification", {
    "type": "questions_completed",
    "module": module_name,
    "completion": {
        "total": 9,
        "confirmed": 9,
        "completion_rate": 100
    }
})

# ❌ 不推荐: 扁平的数据结构
hook_manager.trigger("milestone_notification", {
    "type": "questions_completed",
    "module": module_name,
    "total": 9,
    "confirmed": 9,
    "completion_rate": 100
})
```

### 3. 错误处理

```python
# Hook调用可能失败,但不应该影响Agent主流程
try:
    hook_manager.trigger("milestone_notification", data)
except Exception as e:
    # 记录错误,但不中断Agent执行
    print(f"Hook触发失败: {e}")
```

---

## 📚 相关文档

- **Hook管理器**: [.claude/hooks/hook-manager.md](../hooks/hook-manager.md)
- **Hook配置总结**: [.claude/hooks/hooks-configuration-summary.md](../hooks/hooks-configuration-summary.md)
- **milestone-notification Hook**: [.claude/hooks/milestone-notification-hook.md](../hooks/milestone-notification-hook.md)

---

**创建时间**: 2025-01-11
**版本**: v1.0
**状态**: 🔄 进行中
**下一步**: 集成到各个Skill中