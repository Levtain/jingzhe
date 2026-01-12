---
name: error-detection
description: "自动检测常见错误的Hook。在特定事件触发时自动检查，发现错误时自动记录到错误日志。"
---

# 错误检测 Hook

## 概述

错误检测Hook在特定事件触发时自动运行，检测常见错误模式，发现问题时自动记录到错误日志。

## 触发时机

1. **文件写入后** - Write/Edit工具执行后
2. **代码执行后** - Bash工具执行后
3. **任务完成后** - 任何工具执行完成后
4. **用户反馈错误时** - 用户指出错误时

## 检测规则

### Markdown格式检测

#### 标题加粗检测
```python
pattern = r'^#{1,6}\s+\*\*.+?\*\*'
# 检测: ### **标题**
# 应该: ### 标题
```

#### 表格格式检测
```python
# 检测代码块中包含表格内容
if line.startswith('```') and '|' in next_lines:
    # 可能是表格误用代码块
```

#### 列表格式检测
```python
# 检测不规范的列表格式
if re.match(r'^\s*\d+、\s', line):  # 中文顿号
    # 应该使用: 1. 而不是 1、
```

### 代码执行检测

#### 错误输出检测
```python
if 'Error' in output or 'error' in output:
    # 记录错误
```

#### 异常退出检测
```python
if exit_code != 0:
    # 记录失败
```

### 文档一致性检测

#### 标点符号检测
```python
# 检测中英文标点混用
if re.search(r'[a-zA-Z]，[a-zA-Z]', text):  # 英文间用中文逗号
    # 提示统一
```

### 常见错误模式

#### 未使用的变量/导入
```python
# 检测未使用的import
```

#### 硬编码路径
```python
# 检测应该用变量的路径
```

## 自动修复

对于简单错误，自动提供修复方案:

### 标题加粗修复
```python
# 自动移除标题中的**
content = re.sub(r'^(#{1,6})\s+\*\*(.+?)\*\*', r'\1 \2', content)
```

### 标点符号修复
```python
# 统一为中文标点
content = re.sub(r',', '，', content)
```

## 错误记录格式

检测到错误时，自动调用error-tracker skill记录:

```markdown
#### [ERR-自动检测-YYYYMMDD-NN] - 错误标题

**发现时间**: 自动
**发现方式**: error-detection-hook
**错误类型**: 格式问题
**严重程度**: 🟢轻微

**问题描述**:
- [检测到的问题]

**建议修复**:
- [自动生成的修复建议]

**相关文件**:
- [文件路径]

**状态**: ⏳待确认
```

## 工作流程

1. **检测事件** - 监听触发事件
2. **运行检测规则** - 执行检测脚本
3. **判断是否错误** - 根据规则判断
4. **记录错误** - 调用error-tracker
5. **提供修复建议** - 自动生成建议
6. **更新统计** - 更新错误计数

## 配置选项

### 检测级别

```yaml
detection_level:
  strict:  # 严格模式 - 所有错误都记录
  normal:  # 正常模式 - 只记录中高严重度
  minimal:  # 最小模式 - 只记录严重错误
```

### 自动修复

```yaml
auto_fix:
  enabled: true  # 是否自动修复
  confirm: true  # 修复前是否确认
```

### 提醒频率

```yaml
reminder:
  on_error: true  # 发现错误时立即提醒
  batch: 5        # 累积5个错误后提醒
  daily: true     # 每日总结时提醒
```

## 示例场景

### 场景1: 文件写入后检测

```python
# 用户执行 Write 工具
Write("file.md", content)

# Hook自动触发
error_detection_hook.on_write("file.md", content)

# 检测标题格式
if has_bold_in_headers(content):
    record_error("标题中使用不必要的加粗标记")
    suggest_fix("移除标题中的**标记")
```

### 场景2: 用户反馈错误

```python
# 用户说"这里错了"
user_message = "表格格式不对"

# Hook检测关键词
if contains_error_keywords(user_message):
    auto_record_error(
        title="用户反馈表格格式错误",
        severity="medium",
        description=user_message
    )
```

### 场景3: 代码执行失败

```python
# Bash执行失败
result = Bash("python script.py")

# Hook检测
if result.exit_code != 0:
    record_error(
        title="脚本执行失败",
        severity="high",
        description=f"命令: python script.py\n错误: {result.stderr}"
    )
```

## 集成方式

### 与其他工具集成

1. **error-tracker skill** - 检测到错误后调用记录
2. **daily-review agent** - 每日汇总检测到的错误
3. **文档转换工具** - 转换前检测格式

### 手动调用

```python
# 用户可以主动调用
用户: 检查一下这个文件的格式
Agent: [运行error-detection-hook检查文件]
```

## 检测规则扩展

添加新的检测规则:

```python
def detect_custom_issue(content):
    """自定义检测规则"""
    if pattern_match(content):
        return {
            'title': '自定义错误',
            'severity': 'medium',
            'suggestion': '修复建议'
        }
    return None
```

## 相关资源

- [错误日志](d:\Claude\development\tracking\error-log.md)
- [error-tracker skill](../skills/error-tracker/SKILL.md)
- [每日回顾Agent](../agents/daily-review-agent/AGENT.md)
