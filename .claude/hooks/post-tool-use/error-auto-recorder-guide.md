# 错误自动记录系统使用指南

**版本**: v1.0
**创建时间**: 2025-01-12
**状态**: ✅ 已部署

---

## 📋 系统概述

错误自动记录系统是一个**PostToolUse Hook**，能够在我（Claude）执行操作后自动检测错误模式并记录到`development/active/tracking/error-log.md`。

---

## 🎯 核心功能

### 自动检测的错误类型

1. **技能相关错误**
   - 尝试使用未安装的skill（Unknown skill）
   - 应该先调用skill但直接执行任务

2. **文档路径错误**
   - 应该写入`.active/`但写到了development/根目录
   - 创建重复文档而非更新现有文档

3. **用户负面反馈**
   - 检测关键词："又犯错误"、"又错了"、"你没理解"
   - 检测关键词："应该先"、"你没做"、"还是不行"

---

## 🔧 部署状态

### 已创建的文件

✅ **Hook配置**:
- `.claude/hooks/post-tool-use/error-auto-recorder-hook.json`

✅ **Python脚本**:
- `.claude/hooks/post-tool-use/error-auto-recorder.py`

✅ **已注册到settings.json**:
```json
{
  "matcher": "*",
  "hooks": [
    {
      "type": "command",
      "command": "python d:/Claude/.claude/hooks/post-tool-use/error-auto-recorder.py"
    }
  ]
}
```

---

## 🚀 使用方式

### 自动触发（推荐）

Hook会在每次工具调用后**自动运行**：
- 检测错误模式
- 自动记录到error-log.md
- 无需手动干预

### 手动触发

如果你发现我犯了错误，可以明确告诉我：

**示例1: 技能错误**
```
"你应该先用docs-write skill，而不是直接用Write工具"
```
→ Hook会检测到"应该先"关键词，记录为技能错误

**示例2: 路径错误**
```
"这个文档应该放在development/active/而不是development/"
```
→ Hook会检测到路径模式，记录为路径错误

**示例3: 负面反馈**
```
"你又犯错误了，应该先确认再执行"
```
→ Hook会检测到"又犯错误"，自动记录

---

## 📊 错误记录格式

Hook会按照以下格式自动记录：

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

## ⚙️ 工作原理

### 检测流程

```
我执行工具调用 (Write/Read/Skill等)
    ↓
PostToolUse Hook触发
    ↓
error-auto-recorder.py运行
    ↓
检测错误模式:
  ├─ Skill工具返回"Unknown skill"
  ├─ 文档路径不符合规范
  └─ 用户负面反馈关键词
    ↓
发现错误?
  ├─ 是 → 自动记录到error-log.md
  └─ 否 → 返回 {trigger: "none"}
```

### 检测规则

**1. 技能检测**
```python
if tool_name == 'Skill' and 'Unknown skill' in result:
    记录错误: "使用未安装的skill"
```

**2. 路径检测**
```python
if tool_name in ['Write', 'Edit']:
    if 'development/' in path and '.active/' not in path:
        if path.endswith('.md'):
            记录错误: "文档路径错误"
```

**3. 反馈检测**
```python
negative_keywords = [
    '又犯错误', '又错了', '你没理解',
    '应该先', '你没做', '还是不行'
]

if 最近的对话包含这些关键词:
    记录错误: "用户负面反馈"
```

---

## 🔍 验证Hook是否生效

### 测试方法

**测试1: 手动触发记录**
```
你: "你又犯错误了，应该先检查文档"
```
→ 应该自动记录到error-log.md

**测试2: 检查Hook是否运行**
```
查看最近的工具调用是否有Hook执行记录
```

**测试3: 查看error-log.md**
```
检查是否有新的错误条目自动添加
```

### 当前限制

⚠️ **重要**: Hook需要在**新会话**中才能生效
- 当前会话：Hook可能不生效
- 新会话：Hook自动工作

**解决方案**: 重启Claude Code

---

## 📈 未来改进方向

### 短期（v1.1）
- [ ] 检测更多错误模式（重复错误、理解偏差）
- [ ] 自动分析根本原因
- [ ] 提供修复建议

### 中期（v1.2）
- [ ] 集成到daily-summary-agent
- [ ] 生成每周错误趋势报告
- [ ] 自动识别高频错误模式

### 长期（v2.0）
- [ ] 机器学习错误预测
- [ ] 自动预防常见错误
- [ ] 错误知识库系统

---

## 🛠️ 维护和调试

### 查看Hook日志

```bash
# 测试Hook是否能正常运行
python .claude/hooks/post-tool-use/error-auto-recorder.py
```

### 更新检测规则

编辑`.claude/hooks/post-tool-use/error-auto-recorder.py`：

```python
# 添加新的错误模式
def detect_error_patterns(context):
    # ... 现有代码

    # 新增：检测重复错误
    if is_repeated_error(context):
        errors.append({
            'type': 'repeated_error',
            'severity': 'high',
            'description': '重复发生已知错误'
        })

    return errors
```

### 禁用Hook

如果需要临时禁用，编辑`.claude/settings.json`：

```json
{
  "PostToolUse": [
    {
      "matcher": "*",
      "hooks": [
        {
          "type": "command",
          "command": "python d:/Claude/.claude/hooks/post-tool-use/error-auto-recorder.py",
          "enabled": false  // ← 添加这行
        }
      ]
    }
  ]
}
```

---

## 📚 相关文档

- [错误日志文件](../../development/active/tracking/error-log.md)
- [Hook集成指南](../agents/hook-integration-guide.md)
- [PostToolUse Hook文档](../../.claude/hooks/post-tool-use/)

---

**文档维护者**: Claude (AI)
**最后更新**: 2025-01-12
**状态**: ✅ 已部署，待新会话验证
