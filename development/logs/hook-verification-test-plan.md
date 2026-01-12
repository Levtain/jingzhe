# Hook系统验证测试计划

**测试时间**: 重启Claude Code后
**目的**: 验证所有Hook是否正常工作
**测试范围**: settings.json中注册的所有Hook

---

## 📋 测试清单

### 1. PreToolUse Hook

**Hook**: 文档Skill检测
**触发时机**: Write/Edit .md文件前

**测试步骤**:
```
1. 尝试直接编辑一个.md文件（不先调用docs-write skill）
2. 预期: Hook应该阻止操作，提示先调用docs skill
3. 尝试编辑非.md文件（如.py）
   预期: Hook应该允许通过
```

**预期输出**:
```
如果是.md文档且未调用skill，Hook应该返回错误提示
```

---

### 2. PostToolUse Hooks

#### 2.1 error-auto-recorder

**触发时机**: Write, Edit, Bash, Skill操作后

**测试步骤**:
```
测试1: 技能错误检测
- 尝试使用一个不存在的skill（如 /test-unknown-skill）
- 预期: Hook自动记录错误到 error-log.md

测试2: 文档路径错误检测
- 创建一个文档到 development/ 目录（而非 .active/）
- 预期: Hook检测并记录路径错误

测试3: 正常操作（不应触发）
- 正常编辑一个 .active/ 下的文档
- 预期: Hook不记录任何错误
```

**验证方法**:
```bash
# 检查error-log.md是否新增了错误条目
cat development/active/tracking/error-log.md | tail -20
```

---

#### 2.2 document_sync

**触发时机**: Write/Edit重要文档后

**测试步骤**:
```
1. 编辑 docs/product/claude.md
2. 编辑 CHANGELOG.md
3. 编辑 .claude/hooks/ 下的文件

预期: 每次编辑后应该看到文档变更提醒
```

**预期输出**:
```json
{
  "continue": true,
  "suppressOutput": false,
  "systemMessage": "📋 文档变更提醒\n\n📁 文件: ...\n📂 路径: ...\n🔧 操作: ...\n📝 类型: ...\n💡 建议: ..."
}
```

---

#### 2.3 里程碑检测Prompt

**触发时机**: Edit questions.md后

**测试步骤**:
```
1. 编辑 development/active/issues/某个-questions.md
2. 将所有问题标记为 ✅
3. 预期: Hook提示"问题清单100%完成，建议运行 /sync-docs"
```

---

### 3. SessionStart Hook

**触发时机**: Claude Code启动时

**测试步骤**:
```
1. 重启Claude Code
2. 观察启动时的输出

预期: 应该看到惊蛰计划版本信息和当前状态
```

**预期输出**:
```json
{
  "continue": true,
  "suppressOutput": false,
  "systemMessage": "============================================================\n🎯 惊蛰计划 v1.20\n============================================================\n📊 当前状态: ...\n..."
}
```

---

### 4. PermissionRequest Hook

**触发时机**: 需要权限的操作

**测试步骤**:
```
1. 执行一个需要权限的操作（如运行bash命令）
2. 观察：应该自动批准，无需手动点击同意

注意: 这个Hook在新会话中才会生效
```

---

## 🧪 自动测试脚本

创建一个Python脚本来自动测试Hook输出格式：

```python
#!/usr/bin/env python3
"""
Hook输出格式验证器
"""
import json
import subprocess
import sys

def test_hook_output(script_path, test_input):
    """测试Hook脚本的输出"""
    try:
        result = subprocess.run(
            ["python", script_path],
            input=json.dumps(test_input),
            capture_output=True,
            text=True,
            timeout=10
        )

        # 尝试解析JSON输出
        try:
            output = json.loads(result.stdout.strip())
            return output, None
        except json.JSONDecodeError as e:
            return None, f"JSON解析失败: {e}\n输出: {result.stdout}"

    except subprocess.TimeoutExpired:
        return None, "Hook执行超时"
    except Exception as e:
        return None, f"执行错误: {e}"

def validate_output_format(output):
    """验证输出格式是否符合标准"""
    required_fields = []

    # 检查是否包含标准字段
    if "continue" in output:
        required_fields.append("continue")
    if "suppressOutput" in output:
        required_fields.append("suppressOutput")
    if "systemMessage" in output:
        required_fields.append("systemMessage")

    return required_fields

# 测试案例
test_cases = [
    {
        "name": "error-auto-recorder",
        "script": ".claude/hooks/post-tool-use/error-auto-recorder.py",
        "input": {
            "tool_name": "Skill",
            "tool_input": {"skill": "test-unknown"},
            "result": "Unknown skill: test-unknown"
        }
    },
    {
        "name": "document_sync",
        "script": ".claude/hooks/document_sync.py",
        "input": {
            "tool_name": "Edit",
            "tool_input": {"file_path": "docs/product/claude.md"},
            "tool_response": {}
        }
    },
    {
        "name": "session_start",
        "script": ".claude/hooks/session_start.py",
        "input": {}
    }
]

print("="*60)
print("Hook输出格式验证测试")
print("="*60)

for test in test_cases:
    print(f"\n测试 {test['name']}...")
    output, error = test_hook_output(test['script'], test['input'])

    if error:
        print(f"❌ 失败: {error}")
    else:
        fields = validate_output_format(output)
        if fields:
            print(f"✅ 通过 - 包含字段: {', '.join(fields)}")
            print(f"   输出: {json.dumps(output, ensure_ascii=False)[:100]}...")
        else:
            print(f"⚠️  警告 - 输出格式不符合标准")
            print(f"   输出: {json.dumps(output, ensure_ascii=False)}")

print("\n" + "="*60)
print("测试完成")
print("="*60)
```

---

## 📊 验证结果记录表

| Hook名称 | 状态 | 测试结果 | 备注 |
|---------|------|---------|------|
| PreToolUse (文档检测) | ⏳ 待测试 | | |
| PostToolUse (error-auto-recorder) | ⏳ 待测试 | | |
| PostToolUse (document_sync) | ⏳ 待测试 | | |
| PostToolUse (里程碑检测) | ⏳ 待测试 | | |
| SessionStart | ⏳ 待测试 | | |
| PermissionRequest | ⏳ 待测试 | | |

---

## 🔍 故障排查

### 如果Hook没有触发

1. **检查settings.json语法**
   ```bash
   # 验证JSON格式
   cat .claude/settings.json | python -m json.tool
   ```

2. **检查Hook脚本权限**
   ```bash
   # 确保脚本可执行
   ls -la .claude/hooks/**/*.py
   ```

3. **检查Python路径**
   ```bash
   # 确认Python可用
   python --version
   which python
   ```

4. **查看调试日志**
   ```bash
   # 使用调试模式启动
   claude --debug
   ```

### 如果Hook输出格式错误

1. **手动测试Hook脚本**
   ```bash
   echo '{}' | python .claude/hooks/post-tool-use/error-auto-recorder.py
   ```

2. **验证JSON输出**
   ```bash
   echo '{}' | python .claude/hooks/post-tool-use/error-auto-recorder.py | python -m json.tool
   ```

---

## ✅ 成功标准

所有Hook满足以下条件即为成功：

1. ✅ Hook在正确的时机触发
2. ✅ Hook输出标准JSON格式
3. ✅ Hook不影响正常操作
4. ✅ Hook提供有用的反馈

---

**创建时间**: 2025-01-12
**版本**: v1.0
**状态**: 📝 已准备，待重启后测试
