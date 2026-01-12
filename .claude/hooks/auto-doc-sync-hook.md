# 问题确认后自动文档同步Hook

> **Hook名称**: auto-doc-sync-hook
> **版本**: v1.0
> **创建时间**: 2025-01-11
> **目的**: 问题清单100%完成后自动调用doc-sync-agent同步所有文档

---

## 🎯 核心功能

### 1. 检测问题清单100%完成

**检测逻辑**:
```python
def check_question_completion(question_list_file):
    """
    检查问题清单是否100%完成
    """
    content = read_file(question_list_file)

    # 提取所有问题
    questions = extract_questions(content)

    # 统计确认状态
    total = len(questions)
    confirmed = count_confirmed(questions)
    completion_rate = confirmed / total * 100

    return {
        "is_complete": completion_rate == 100,
        "total": total,
        "confirmed": confirmed,
        "completion_rate": completion_rate
    }
```

**触发条件**:
```yaml
触发事件:
  - 问题清单中所有问题标记✅
  - discussion-agent完成最后一个问题
  - completion-check-agent验证100%完成

监控文件:
  - development/active/issues/*questions*.md
  - development/active/issues/game-submission-questions-v2.md
```

### 2. 自动调用doc-sync-agent

**调用流程**:
```yaml
检测到100%完成
  ↓
1. 通知用户
   "检测到问题清单100%完成,准备同步文档..."
  ↓
2. 调用doc-sync-agent
   执行完整同步流程:
   - 检查文档一致性
   - 同步已确认问题
   - 更新CHANGELOG
   - 同步版本号
   - 更新交叉引用
   - 创建开发日志
  ↓
3. 生成同步报告
  - 同步文件数量
  - 更新内容摘要
  - 错误和警告
  ↓
4. 通知用户
   "文档同步完成!"
```

### 3. 验证同步结果

**验证检查点**:
```yaml
验证项:
  1. 设计文档已更新
     - 所有问题已同步
     - 数值/规则一致

  2. CHANGELOG已更新
     - 新版本条目
     - 变更记录完整

  3. 版本号已同步
     - claude.md版本号
     - 设计文档版本号
     - 一致性检查

  4. 交叉引用已更新
     - 引用链接有效
     - 版本号正确

  5. 开发日志已创建
     - 今日同步记录
     - 文件列表
```

---

## 🔧 核心函数

### trigger_auto_sync(question_list_file)

```python
def trigger_auto_sync(question_list_file):
    """
    问题清单100%完成时触发自动同步
    """
    # 1. 检查完成度
    completion = check_question_completion(question_list_file)

    if not completion["is_complete"]:
        return  # 未完成,不触发

    # 2. 通知用户
    notify_completion(completion)

    # 3. 询问是否立即同步
    # (或者配置为自动同步,无需询问)
    if should_auto_sync():
        # 自动同步
        sync_result = execute_doc_sync()

        # 4. 验证结果
        validation = validate_sync_result(sync_result)

        # 5. 通知结果
        notify_sync_result(sync_result, validation)
    else:
        # 提示用户手动同步
        suggest_manual_sync()
```

### execute_doc_sync()

```python
def execute_doc_sync():
    """
    调用doc-sync-agent执行同步
    """
    # 这里调用doc-sync-agent的核心逻辑
    # 或者调用/sync-docs命令

    result = {
        "synced_files": [],
        "updated_content": [],
        "errors": [],
        "warnings": []
    }

    # 执行同步流程
    # 1. 检查文档一致性
    consistency = check_document_consistency()

    # 2. 同步已确认问题
    synced = sync_confirmed_questions()

    # 3. 更新CHANGELOG
    changelog = update_changelog()

    # 4. 同步版本号
    versions = sync_version_numbers()

    # 5. 更新交叉引用
    references = update_cross_references()

    # 6. 创建开发日志
    log = create_development_log()

    result["synced_files"] = (
        synced["files"] +
        changelog["files"] +
        versions["files"] +
        references["files"] +
        log["files"]
    )

    return result
```

### validate_sync_result(sync_result)

```python
def validate_sync_result(sync_result):
    """
    验证同步结果
    """
    validation = {
        "passed": True,
        "checks": [],
        "errors": [],
        "warnings": []
    }

    # 检查1: 设计文档已更新
    design_check = check_design_documents_updated()
    validation["checks"].append(design_check)

    # 检查2: CHANGELOG已更新
    changelog_check = check_changelog_updated()
    validation["checks"].append(changelog_check)

    # 检查3: 版本号已同步
    version_check = check_versions_synced()
    validation["checks"].append(version_check)

    # 检查4: 交叉引用已更新
    reference_check = check_cross_references_updated()
    validation["checks"].append(reference_check)

    # 检查5: 开发日志已创建
    log_check = check_development_log_created()
    validation["checks"].append(log_check)

    # 汇总结果
    for check in validation["checks"]:
        if not check["passed"]:
            validation["passed"] = False
            validation["errors"].append(check.get("error"))

        if check.get("warnings"):
            validation["warnings"].extend(check["warnings"])

    return validation
```

---

## 📋 Hook触发配置

### 在discussion-agent中集成

```python
# discussion-agent的完成逻辑
def complete_discussion(question_list_file):
    """
    完成问题讨论
    """
    # ... 讨论逻辑 ...

    # 最后一个问题确认后
    if is_last_question:
        # 更新问题清单
        update_question_list(question_list_file)

        # 检查是否100%完成
        completion = check_question_completion(question_list_file)

        if completion["is_complete"]:
            # 触发自动同步Hook
            trigger_hook("auto-doc-sync", {
                "question_list": question_list_file,
                "completion": completion
            })
```

### 在completion-check-agent中集成

```python
# completion-check-agent的验证逻辑
def verify_completion(module_name):
    """
    验证模块完成度
    """
    # ... 验证逻辑 ...

    # 如果验证通过且100%完成
    if completion_percentage == 100:
        # 生成完成报告
        generate_completion_report()

        # 触发自动同步Hook
        trigger_hook("auto-doc-sync", {
            "module": module_name,
            "completion_rate": 100
        })
```

---

## 📊 输出格式

### 完成通知

```markdown
🎉 **问题清单100%完成!**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**模块**: 游戏提交系统
**文件**: development/active/issues/game-submission-questions-v2.md

📊 **完成统计**:
- 问题总数: 9个
- 已确认: 9个
- 完成度: 100% ✅

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔄 **准备自动同步文档**...

将执行以下操作:
1. ✅ 检查文档一致性
2. ✅ 同步已确认问题
3. ✅ 更新CHANGELOG
4. ✅ 同步版本号
5. ✅ 更新交叉引用
6. ✅ 创建开发日志

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❓ **是否立即执行?**
- 输入 "是" / "yes" / "y" → 立即同步
- 输入 "否" / "no" / "n" → 稍后手动同步

(配置为自动同步时将跳过此提示)
```

### 同步完成报告

```markdown
✅ **文档同步完成!**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**模块**: 游戏提交系统
**同步时间**: 2025-01-11 14:30:00

📊 **同步统计**:
- 同步文件: 5个
- 更新内容: 15处
- 修复问题: 0个

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 **已同步文件**:

1. ✅ 评分系统设计方案_v1.0.md
   - 同步Q1-Q6决策
   - 更新核心规则

2. ✅ 排名系统技术实现文档_v1.0.md
   - 同步Q7-Q9决策
   - 更新硬核玩家逻辑

3. ✅ CHANGELOG.md
   - 新增v1.3版本条目
   - 记录7项变更

4. ✅ claude.md
   - 版本号: v1.2 → v1.3

5. ✅ development/logs/dev-log-2025-01-11.md
   - 创建日志条目
   - 记录同步过程

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ **验证结果**:

所有检查项通过:
- ✅ 设计文档已更新
- ✅ CHANGELOG已更新
- ✅ 版本号已同步
- ✅ 交叉引用已更新
- ✅ 开发日志已创建

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 **下一步建议**:
1. 运行 /check-completion 验证模块完整性
2. 开始创建设计文档
3. 或继续下一个模块的问题讨论

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 💡 核心价值

### 改进前

```yaml
手动同步流程:
  1. 问题清单100%完成
  2. 用户需要手动调用 /sync-docs
  3. 容易忘记同步
  4. 文档可能不一致
  5. 需要手动检查结果

问题:
  - 遗漏同步步骤
  - 文档版本不一致
  - 交叉引用失效
  - 需要记忆和手动操作
```

### 改进后

```yaml
自动同步流程:
  1. 问题清单100%完成
  2. Hook自动检测
  3. 自动调用doc-sync-agent
  4. 自动验证同步结果
  5. 通知用户完成状态

优势:
  - 不会遗漏同步
  - 文档保持一致
  - 交叉引用有效
  - 零手动操作
```

---

## ⚙️ 配置选项

### Hook配置

```json
{
  "hooks": {
    "auto-doc-sync": {
      "enabled": true,
      "auto_sync": true,
      "require_confirmation": false,
      "validate_result": true,
      "notification": true
    }
  }
}
```

### 配置说明

```yaml
enabled:
  - true: 启用Hook
  - false: 禁用Hook

auto_sync:
  - true: 自动执行同步,无需用户确认
  - false: 检测到100%完成时询问用户

require_confirmation:
  - true: 每次同步前询问用户
  - false: 直接执行同步

validate_result:
  - true: 同步后自动验证结果
  - false: 跳过验证

notification:
  - true: 发送完成通知
  - false: 静默执行
```

---

## 🔗 与其他Hook的配合

### agent-completion-archive-hook

```yaml
配合流程:
  1. 问题清单100%完成
  2. auto-doc-sync-hook同步文档
  3. 生成完成报告
  4. agent-completion-archive-hook归档报告
```

### milestone-notification-hook

```yaml
配合流程:
  1. 问题清单100%完成
  2. auto-doc-sync-hook同步文档
  3. milestone-notification-hook发送通知
  4. 推荐里程碑达成后的下一步
```

---

## ✅ 总结

**核心功能**:
1. 检测问题清单100%完成
2. 自动调用doc-sync-agent
3. 验证同步结果
4. 通知用户完成状态

**核心价值**:
- 不会遗漏同步
- 文档保持一致
- 交叉引用有效
- 零手动操作

**实施建议**:
- 配置为自动同步
- 启用结果验证
- 确保通知及时
- 与其他Hook良好配合

---

**创建时间**: 2025-01-11
**版本**: v1.0
**状态**: ✅ Hook已定义
**下一步**: 集成到discussion-agent和completion-check-agent