# 模块完成自动通知Hook

> **Hook名称**: milestone-notification-hook
> **版本**: v1.0
> **创建时间**: 2025-01-11
> **目的**: 模块/里程碑完成时自动发送通知,推荐下一步操作

---

## 🎯 核心功能

### 1. 检测里程碑完成

**里程碑类型**:
```yaml
类型1: 问题讨论完成
  触发条件:
    - 问题清单100%确认
    - discussion-agent完成所有问题

类型2: 模块验证通过
  触发条件:
    - completion-check-agent验证通过
    - 所有关键指标达标

类型3: Agent开发完成
  触发条件:
    - Agent测试通过
    - 文档齐全

类型4: 阶段性目标达成
  触发条件:
    - 一组相关模块完成
    - 整体进度达到阈值
```

### 2. 生成完成通知

**通知内容**:
```yaml
基本信息:
  - 里程碑名称
  - 完成时间
  - 完成度统计

关键指标:
  - 问题确认数量
  - 文档完整性
  - 代码完成度
  - 测试覆盖率

成果展示:
  - 主要决策
  - 关键成果
  - 生成的文档
  - 创建的文件
```

### 3. Windows系统通知 🔔

**通知方式**:
```yaml
方式1: Windows Toast通知
  - 使用PowerShell的BurntToast模块
  - 或使用Windows API
  - 在右下角弹出通知
  - 包含标题和内容

方式2: 系统音效
  - 使用Windows系统音效
  - 播放提示音
  - 可配置音效类型

方式3: 终端内通知
  - Markdown格式通知
  - 彩色输出
  - 清晰的视觉提示
```

**Windows通知实现**:
```python
def show_windows_notification(title, message):
    """
    显示Windows系统通知
    """
    try:
        # 方法1: 使用PowerShell的BurntToast
        ps_command = f'''
        New-BurntToastNotification -Text "{title}", "{message}"
        '''
        subprocess.run(["powershell", "-Command", ps_command])

        # 方法2: 使用Windows API (fallback)
        # 或者使用plyer库的notification功能

    except Exception as e:
        # 如果Windows通知失败,回退到终端输出
        print(f"🔔 {title}: {message}")

def play_notification_sound(sound_type="milestone"):
    """
    播放通知音效
    """
    sound_files = {
        "milestone": "C:\\Windows\\Media\\notify.wav",
        "achievement": "C:\\Windows\\Media\\tada.wav",
        "warning": "C:\\Windows\\Media\\Windows Exclamation.wav",
        "error": "C:\\Windows\\Media\\Windows Error.wav"
    }

    sound_file = sound_files.get(sound_type, sound_files["milestone"])

    try:
        import winsound
        winsound.PlaySound(sound_file, winsound.SND_FILENAME)
    except:
        # Fallback: 系统铃声
        print('\a')  # ASCII bell character
```

### 4. 推荐下一步操作
```python
def recommend_next_actions(milestone_type, current_state):
    """
    根据里程碑类型和当前状态推荐下一步
    """
    if milestone_type == "questions_completed":
        return [
            {
                "action": "同步文档",
                "command": "/sync-docs",
                "priority": "P0",
                "reason": "确保所有文档与决策一致"
            },
            {
                "action": "验证模块完整性",
                "command": "/check-completion",
                "priority": "P1",
                "reason": "检查模块是否满足开发条件"
            },
            {
                "action": "创建设计文档",
                "command": "手动开始",
                "priority": "P1",
                "reason": "基于确认的问题创建设计"
            }
        ]

    elif milestone_type == "module_verified":
        return [
            {
                "action": "开始代码生成",
                "command": "/generate-code",
                "priority": "P0",
                "reason": "设计已完成,可以开始编码"
            },
            {
                "action": "代码审核",
                "command": "/review-code",
                "priority": "P1",
                "reason": "确保代码质量"
            }
        ]

    elif milestone_type == "phase_complete":
        return [
            {
                "action": "查看整体进度",
                "command": "/check-progress",
                "priority": "P0",
                "reason": "了解当前项目进度"
            },
            {
                "action": "规划下一阶段",
                "command": "/task-planner",
                "priority": "P1",
                "reason": "制定下一阶段计划"
            }
        ]
```

---

## 🔧 核心函数

### detect_milestone_completion()

```python
def detect_milestone_completion():
    """
    检测里程碑完成
    """
    milestones = []

    # 检测1: 问题讨论完成
    question_lists = glob("development/issues/*questions*.md")
    for ql in question_lists:
        completion = check_question_completion(ql)
        if completion["is_complete"] and not is_notified(ql):
            milestones.append({
                "type": "questions_completed",
                "module": extract_module_name(ql),
                "file": ql,
                "completion": completion
            })

    # 检测2: 模块验证通过
    verification_reports = glob("development/testing/*verification*.md")
    for vr in verification_reports:
        if is_verification_passed(vr) and not is_notified(vr):
            milestones.append({
                "type": "module_verified",
                "module": extract_module_name(vr),
                "file": vr
            })

    # 检测3: 阶段性目标
    overall_progress = get_overall_progress()
    if overall_progress["percentage"] >= 50 and not is_notified("50%"):
        milestones.append({
            "type": "phase_complete",
            "phase": "50%完成",
            "progress": overall_progress
        })

    return milestones
```

### generate_milestone_notification(milestone)

```python
def generate_milestone_notification(milestone):
    """
    生成里程碑完成通知
    """
    if milestone["type"] == "questions_completed":
        return generate_questions_completed_notification(milestone)
    elif milestone["type"] == "module_verified":
        return generate_module_verified_notification(milestone)
    elif milestone["type"] == "phase_complete":
        return generate_phase_complete_notification(milestone)

def generate_questions_completed_notification(milestone):
    """
    生成问题讨论完成通知
    """
    module = milestone["module"]
    completion = milestone["completion"]

    # Windows通知
    show_windows_notification(
        "🎉 里程碑达成!",
        f"{module} 问题讨论 100%完成!"
    )
    play_notification_sound("achievement")

    # 终端通知
    notification = f"""🎉 **里程碑达成: 问题讨论完成!**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**模块**: {module}
**完成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 **完成统计**:
- 问题总数: {completion['total']}个
- 已确认: {completion['confirmed']}个
- 完成度: {completion['completion_rate']:.0f}% ✅

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏆 **主要成果**:
{extract_key_achievements(milestone)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{recommend_next_actions(milestone)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎊 **恭喜!** 已完成问题讨论阶段
"""

    return notification
```

### recommend_next_actions(milestone)

```python
def recommend_next_actions(milestone):
    """
    推荐下一步操作
    """
    actions = get_recommendations(milestone["type"], milestone)

    recommendation = "🎯 **推荐下一步操作**:\n\n"

    for i, action in enumerate(actions, 1):
        priority_icon = {
            "P0": "🔴",
            "P1": "🟡",
            "P2": "🟢",
            "P3": "⚪"
        }.get(action["priority"], "⚪")

        recommendation += f"{priority_icon} **{action['action']}**\n"
        recommendation += f"   命令: `{action['command']}`\n"
        recommendation += f"   原因: {action['reason']}\n\n"

    return recommendation
```

---

## 📋 Hook触发配置

### 在completion-check-agent中集成

```python
# completion-check-agent验证通过后
def verify_module_completion(module_name):
    """
    验证模块完成度
    """
    # ... 验证逻辑 ...

    if verification_passed:
        # 生成验证报告
        generate_verification_report()

        # 触发里程碑通知Hook
        trigger_hook("milestone-notification", {
            "type": "module_verified",
            "module": module_name,
            "verification": verification_result
        })
```

### 在discussion-agent中集成

```python
# discussion-agent完成所有问题后
def complete_discussion(question_list_file):
    """
    完成问题讨论
    """
    # ... 讨论逻辑 ...

    if is_last_question and all_confirmed:
        # 触发里程碑通知Hook
        trigger_hook("milestone-notification", {
            "type": "questions_completed",
            "module": extract_module_name(question_list_file),
            "file": question_list_file
        })
```

---

## 📊 输出格式

### 问题讨论完成通知

```markdown
🎉 **里程碑达成: 问题讨论完成!**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**模块**: 游戏提交系统
**完成时间**: 2025-01-11 14:30:00

📊 **完成统计**:
- 问题总数: 9个
- 已确认: 9个
- 完成度: 100% ✅

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏆 **主要成果**:

1. **作者列表自动生成**
   - 确认: 自动同步团队快照
   - 影响: 简化提交流程

2. **硬核玩家标记机制**
   - 确认: 区分历史成就和赛季特权
   - 影响: 激励系统完善

3. **源码有效性验证**
   - 确认: 前端+后端+举报三重机制
   - 影响: 数据质量保证

... (其他成果)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 **推荐下一步操作**:

🔴 **同步文档**
   命令: `/sync-docs`
   原因: 确保所有文档与决策一致

🟡 **验证模块完整性**
   命令: `/check-completion`
   原因: 检查模块是否满足开发条件

🟡 **创建设计文档**
   命令: 手动开始
   原因: 基于确认的问题创建设计

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎊 **恭喜!** 已完成问题讨论阶段

**下一步**: 建议先运行 `/sync-docs` 同步文档
```

### 模块验证通过通知

```markdown
🎉 **里程碑达成: 模块验证通过!**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**模块**: 游戏提交系统
**验证时间**: 2025-01-11 15:00:00

📊 **验证结果**:
- 总体完成度: 100% ✅
- 设计文档质量: 95/100
- 问题确认完成度: 100%
- 文档完整性: 100%
- 交叉引用正确性: 98%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏆 **关键指标**:

✅ 所有核心问题已确认
✅ 设计文档已创建
✅ 技术方案已明确
✅ 风险已评估
✅ 依赖关系已理清

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 **推荐下一步操作**:

🔴 **开始代码生成**
   命令: `/generate-code`
   原因: 设计已完成,可以开始编码

🟡 **代码审核**
   命令: `/review-code`
   原因: 确保代码质量

🟢 **查看整体进度**
   命令: `/check-progress`
   原因: 了解当前项目进度

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎊 **恭喜!** 模块已满足开发条件

**下一步**: 建议运行 `/generate-code` 开始代码生成
```

### 阶段性目标达成通知

```markdown
🎉 **里程碑达成: 50%进度完成!**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**达成时间**: 2025-01-11 16:00:00

📊 **整体进度**:
- Agent开发: 6/6 (100%) ✅
- 模块开发: 3/6 (50%)
- 文档完成: 85%
- 代码完成: 30%

**总体完成度**: 50%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏆 **已完成的模块**:

1. ✅ 用户角色系统
2. ✅ 评分系统
3. ✅ 游戏提交系统

⏳ **进行中的模块**:

1. 🔄 排名系统 (70%)
2. 🔄 团队系统 (40%)

⏸️ **未开始的模块**:

1. ⏸️ 成就系统
2. ⏸️ 经济系统

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 **推荐下一步操作**:

🔴 **继续排名系统**
   命令: `/discuss development/issues/ranking-system-questions.md`
   原因: 完成度70%,即将完成

🟡 **规划下一阶段**
   命令: `/task-planner`
   原因: 制定剩余模块开发计划

🟢 **查看详细进度**
   命令: `/check-progress`
   原因: 了解各模块详细状态

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎊 **恭喜!** 项目已完成一半

**下一步**: 建议先完成排名系统,再规划下一阶段
```

---

## 💡 核心价值

### 改进前

```yaml
手动追踪流程:
  1. 模块完成
  2. 不知道下一步做什么
  3. 需要手动查看进度
  4. 可能遗漏重要步骤
  5. 缺乏成就感

问题:
  - 不清楚下一步
  - 可能遗漏同步步骤
  - 缺乏进度可视化
  - 用户体验不佳
```

### 改进后

```yaml
自动通知流程:
  1. 模块完成
  2. 自动发送通知
  3. 明确推荐下一步
  4. 提供清晰指引
  5. 增强成就感

优势:
  - 清晰的下一步指引
  - 不会遗漏重要步骤
  - 实时进度可视化
  - 提升用户体验
```

---

## ⚙️ 配置选项

### Hook配置

```json
{
  "hooks": {
    "milestone-notification": {
      "enabled": true,
      "notification_types": [
        "questions_completed",
        "module_verified",
        "phase_complete"
      ],
      "show_recommendations": true,
      "show_statistics": true,
      "track_notifications": true,
      "windows_notification": {
        "enabled": true,
        "use_toast": true,
        "use_sound": true,
        "sound_type": "achievement",
        "fallback_to_terminal": true
      }
    }
  }
}
```

### 通知配置说明

```yaml
windows_notification:
  enabled:
    - true: 启用Windows系统通知
    - false: 仅使用终端通知

  use_toast:
    - true: 使用Windows Toast通知(右下角弹出)
    - false: 不使用Toast通知

  use_sound:
    - true: 播放音效
    - false: 静音

  sound_type:
    - milestone: 普通里程碑音效
    - achievement: 成就解锁音效(tada.wav)
    - warning: 警告音效
    - error: 错误音效

  fallback_to_terminal:
    - true: Windows通知失败时回退到终端输出
    - false: 仅Windows通知,失败则不显示
```

### 音效文件路径

```yaml
Windows系统音效位置:
  C:\Windows\Media\

可选音效:
  - notify.wav: 普通通知
  - tada.wav: 成就解锁(推荐用于里程碑)
  - Windows Exclamation.wav: 警告
  - Windows Error.wav: 错误
  - chimes.wav: 提示
  - ringout.wav: 电话铃声
```

### PowerShell BurntToast安装

```powershell
# 如果需要使用Toast通知,需要安装BurntToast模块
# 以管理员身份运行PowerShell:

Install-Module -Name BurntToast -Force

# 或使用:
Install-Module -Name BurntToast -Scope CurrentUser
```

### 简化版通知(无需安装模块)

如果不希望安装PowerShell模块,可以使用Windows自带的通知API:

```python
def show_windows_notification_simple(title, message):
    """
    简化版Windows通知(无需额外模块)
    """
    try:
        # 使用Windows API通过VBScript
        vb_script = f'''
        Set objShell = CreateObject("WScript.Shell")
        objShell.Popup "{message}", 0, "{title}", 64
        '''
        subprocess.run(["cscript", "//NoLogo", "//B"], input=vb_script, text=True)
    except:
        # 最终回退: 终端输出
        print(f"🔔 {title}: {message}")
```

---

## 🔗 与其他Hook的配合

### auto-doc-sync-hook

```yaml
配合流程:
  1. 问题清单100%完成
  2. milestone-notification-hook发送通知
  3. auto-doc-sync-hook执行同步
  4. 同步完成后发送二次通知
```

### agent-completion-archive-hook

```yaml
配合流程:
  1. 模块验证通过
  2. agent-completion-archive-hook归档报告
  3. milestone-notification-hook发送通知
  4. 包含归档位置信息
```

---

## ✅ 总结

**核心功能**:
1. 检测里程碑完成
2. 生成完成通知
3. **Windows系统通知(右下角Toast + 音效)** 🔔
4. 推荐下一步操作
5. 增强用户体验

**核心价值**:
- 清晰的下一步指引
- 不会遗漏重要步骤
- 实时进度可视化
- 提升成就感
- **不会被错过!** (Windows通知 + 音效)

**实施建议**:
- 通知内容简洁明了
- 推荐操作优先级清晰
- 与其他Hook良好配合
- 记录通知历史
- **启用Windows通知和音效**(防止错过)

**快速启用**:
```json
{
  "windows_notification": {
    "enabled": true,
    "use_sound": true,
    "sound_type": "achievement"
  }
}
```

---

**创建时间**: 2025-01-11
**版本**: v1.1
**状态**: ✅ Hook已更新(添加Windows通知)
**下一步**: 集成到相关Agent中,启用Windows通知