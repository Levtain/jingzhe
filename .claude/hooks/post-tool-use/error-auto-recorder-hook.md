# Error Auto Recorder Hook

> **Hook名称**: error-auto-recorder
> **版本**: v1.1
> **创建时间**: 2025-01-12
> **目的**: 自动检测Claude的错误模式并记录到error-log.md，实现持续自我优化
> **优先级**: P0 (高)
> **类型**: PostToolUse

---

## 🎯 核心功能

### 1. 自动错误检测

**检测类型**:
```yaml
类型1: 技能相关错误
  检测条件:
    - Skill工具返回"Unknown skill"
    - 应该先调用skill但直接执行

类型2: 文档路径错误
  检测条件:
    - 应该写入.active/但写到了development/根目录
    - 创建重复文档而非更新现有文档

类型3: 用户负面反馈
  检测关键词:
    - "又犯错误"、"又错了"、"你没理解"
    - "应该先"、"你没做"、"还是不行"

类型4: Hook相关错误
  检测条件:
    - Hook未生效
    - 期望自动批准但仍需手动确认
```

### 2. 自动错误记录

**记录流程**:
```yaml
1. 检测到错误
   ↓
2. 生成唯一错误ID (ERR-YYYYMMDD-NN)
   ↓
3. 格式化错误条目
   ↓
4. 追加到error-log.md
   ↓
5. 返回JSON响应
```

### 3. 智能ID生成

**ID格式**: `ERR-YYYYMMDD-NN`
- 自动读取现有error-log.md
- 找到今日最大编号并递增
- 确保ID唯一性

---

## 🔧 核心函数

### detect_error_patterns(context)

```python
def detect_error_patterns(context):
    """
    检测错误模式
    """
    tool_name = context.get('tool_name', '')
    tool_input = context.get('tool_input', {})
    result = context.get('result', '')

    errors = []

    # 检测技能相关错误
    if tool_name == 'Skill' and 'Unknown skill' in str(result):
        errors.append({
            'type': 'skill_not_found',
            'severity': 'high',
            'description': '尝试使用未安装的skill',
            'skill_name': tool_input.get('skill', 'unknown')
        })

    # 检测文档路径错误
    if tool_name in ['Write', 'Edit']:
        file_path = tool_input.get('file_path', '')
        if 'development/' in file_path and '.active/' not in file_path:
            if file_path.endswith('.md'):
                errors.append({
                    'type': 'wrong_document_path',
                    'severity': 'medium',
                    'description': f'文档路径错误：应该使用.active/目录',
                    'file_path': file_path
                })

    # 检测用户负面反馈
    conversation_history = context.get('conversation_history', [])
    recent_messages = conversation_history[-5:] if conversation_history else []

    negative_keywords = [
        '又犯错误', '又错了', '你没理解', '这不是我要求的',
        '应该先', '你没做', '还是不行', '没生效'
    ]

    for msg in recent_messages:
        if any(keyword in msg for keyword in negative_keywords):
            errors.append({
                'type': 'user_negative_feedback',
                'severity': 'high',
                'description': f'用户负面反馈: {msg[:100]}...'
            })
            break

    return errors
```

### generate_error_id()

```python
def generate_error_id():
    """
    生成错误ID - 自动递增
    """
    now = datetime.now()
    date_str = now.strftime('%Y%m%d')

    # 读取现有error-log.md，找到今日最大编号
    error_log_path = 'development/active/tracking/error-log.md'
    max_num = 0

    if os.path.exists(error_log_path):
        with open(error_log_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # 查找今日所有错误编号
            pattern = f'ERR-{date_str}-(\\d+)'
            matches = re.findall(pattern, content)
            if matches:
                max_num = max(int(m) for m in matches)

    # 递增编号
    new_num = max_num + 1
    return f'ERR-{date_str}-{new_num:02d}'
```

---

## 📋 触发配置

### Hook配置

```json
{
  "description": "自动检测错误模式并记录到error-log.md",
  "enabled": true,
  "trigger": {
    "events": ["post_tool_use"],
    "tool_filters": ["Write", "Edit", "Bash", "Skill"],
    "condition": "检测到错误模式或用户负面反馈"
  },
  "action": {
    "type": "command"
  },
  "config": {
    "error_log_path": "development/active/tracking/error-log.md",
    "auto_stop_on_error": true,
    "require_acknowledgment": true
  }
}
```

---

## ⚙️ 配置选项

### 在settings.json中配置

```json
{
  "PostToolUse": [
    {
      "matcher": "*",
      "hooks": [
        {
          "type": "command",
          "command": "python d:/Claude/.claude/hooks/post-tool-use/error-auto-recorder.py"
        }
      ]
    }
  ]
}
```

### 配置说明

```yaml
enabled:
  - true: 启用自动错误检测
  - false: 禁用错误检测

error_log_path:
  - 错误日志文件路径
  - 默认: development/active/tracking/error-log.md

auto_stop_on_error:
  - true: 检测到错误时自动停止当前任务
  - false: 仅记录错误，不停止任务

require_acknowledgment:
  - true: 需要用户确认错误记录
  - false: 自动记录，无需确认
```

---

## 📊 输出格式

### 未检测到错误

```json
{
  "trigger": "none"
}
```

### 检测到错误

```json
{
  "trigger": "error_detected",
  "error_type": "skill_not_found",
  "message": "错误已自动记录到error-log.md"
}
```

### 记录失败

```json
{
  "trigger": "error",
  "error_type": "skill_not_found",
  "message": "记录错误失败"
}
```

---

## 📝 错误记录格式

Hook会按照以下格式自动记录到error-log.md：

```markdown
#### [ERR-20260112-07] - 使用未安装的skill

**发现时间**: 2026-01-12 18:30
**发现方式**: 自动检测
**错误类型**: skill_not_found
**严重程度**: 🔴严重

**问题描述**:
- 尝试使用未安装的skill: frontend-ui-ux

**根本原因分析**:
- 需要进一步分析

**解决方案**:
- 待分析

**预防措施**:
- 待确定

**状态**: ⏳待检测和分析
```

---

## 🔗 与其他Hook的配合

### PreToolUse Hook (文档Skill检测)

```yaml
配合流程:
  1. PreToolUse检测到未调用docs skill
  2. 阻止Write/Edit操作
  3. 如果强行执行 → error-auto-recorder记录错误
```

### PermissionRequest Hook

```yaml
配合流程:
  1. PermissionRequest自动批准请求
  2. 如果Hook未生效需要手动批准
  3. error-auto-recorder检测并记录Hook问题
```

---

## ✅ 核心价值

### 改进前

```yaml
手动错误记录:
  1. 发现错误
  2. 可能忘记记录
  3. 记录格式不统一
  4. 缺少ID管理

问题:
  - 容易遗漏错误
  - 难以追踪重复错误
  - 无法持续改进
```

### 改进后

```yaml
自动错误记录:
  1. 检测到错误
  2. 自动生成ID
  3. 统一格式记录
  4. 持续追踪优化

优势:
  - 不会遗漏错误
  - 智能ID递增
  - 统一记录格式
  - 支持持续改进
```

---

## 🛠️ 依赖文件

- **Python脚本**: error-auto-recorder.py
- **错误日志**: development/active/tracking/error-log.md
- **Hook配置**: error-auto-recorder-hook.json

---

## 📚 相关文档

- [错误日志文件](../../development/active/tracking/error-log.md)
- [Hook集成指南](../agents/hook-integration-guide.md)
- [使用指南](error-auto-recorder-guide.md)

---

**创建时间**: 2025-01-12
**版本**: v1.1
**状态**: ✅ Hook已完善(P0/P1问题已修复)
**下一步**: 在新会话中测试Hook功能
