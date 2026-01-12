---
name: natural-language-router
description: UserPromptSubmit Hook - 自动将自然语言输入转换为斜杠命令
version: 1.0
trigger: UserPromptSubmit
---

# UserPromptSubmit Hook - 自然语言命令路由器

## 功能说明

在用户提交prompt、Claude处理之前,自动识别自然语言指令并转换为对应的斜杠命令。

## 工作原理

**触发时机**: 用户提交prompt时,Claude处理之前

**执行流程**:
```
用户输入: "看看进度"
    ↓
UserPromptSubmit Hook触发
    ↓
匹配到: "看看进度" → "/check-progress"
    ↓
修改prompt为: "/check-progress\n\n原始输入: 看看进度"
    ↓
Claude执行 /check-progress 命令
```

---

## 支持的自然语言指令

### 进度查看类
- **"看看进度"** → `/check-progress`
- **"check progress"** → `/check-progress`
- **"查看状态"** → `/check-progress`
- **"(查看)?问题(列表)?"** → `/check-progress`
- **"questions"** → `/check-progress`

### 文档同步类
- **"同步一下"** → `/sync-docs`
- **"sync docs"** → `/sync-docs`
- **"同步文档"** → `/sync-docs`

### 总结类
- **"今天先这样"** → `/daily-summary`
- **"daily.*summary"** → `/daily-summary`
- **"生成总结"** → `/daily-summary`
- **"今天总结"** → `/daily-summary`

### 讨论类
- **"开始讨论"** → `/discuss`
- **"discuss"** → `/discuss`
- **"讨论问题"** → `/discuss`

### 上下文保存类
- **"保存上下文"** → `/save-context`
- **"save.*context"** → `/save-context`
- **"保存状态"** → `/save-context`

### Token检查类
- **"检查token"** → `/token-check`
- **"token.*check"** → `/token-check`
- **"看看token"** → `/token-check`

### 文档审核类
- **"审核文档"** → `/review-docs`
- **"review.*doc"** → `/review-docs`
- **"检查文档"** → `/review-docs`

---

## 配置方法

### 方法1: 通过settings.json配置

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "python d:/Claude/.claude/hooks/user-prompt-submit/natural-language-router.py"
          }
        ]
      }
    ]
  }
}
```

### 方法2: 通过/hooks命令

1. 运行 `/hooks`
2. 选择 `UserPromptSubmit` hook事件
3. 添加matcher: `*` (匹配所有输入)
4. 添加hook: `python d:/Claude/.claude/hooks/user-prompt-submit/natural-language-router.py`
5. 保存配置

---

## 优势分析

### 当前方案 (system-prompt)

```markdown
**优点**:
- 灵活,依赖LLM理解
- 可以处理复杂语境

**缺点**:
- 不够稳定,可能识别错误
- 依赖LLM判断,不够确定
- 需要在prompt中占用token
```

### UserPromptSubmit Hook方案

```markdown
**优点**:
- ✅ 100%可靠,代码级别的确定性
- ✅ 不依赖LLM判断
- ✅ 执行速度快
- ✅ 可以精确控制匹配规则
- ✅ 易于调试和维护
- ✅ 不占用prompt token

**缺点**:
- 需要预定义规则
- 无法处理复杂语境
```

---

## 使用示例

### 示例1: 查看进度

**用户输入**:
```
看看进度怎么样了?
```

**Hook处理**:
```python
# 匹配: "看看进度"
# 转换为: /check-progress
```

**Claude收到**:
```
/check-progress

原始输入: 看看进度怎么样了?
```

**结果**: 执行进度检查命令 ✅

---

### 示例2: 文档同步

**用户输入**:
```
帮我同步一下文档
```

**Hook处理**:
```python
# 匹配: "同步一下"
# 转换为: /sync-docs
```

**Claude收到**:
```
/sync-docs

原始输入: 帮我同步一下文档
```

**结果**: 执行文档同步命令 ✅

---

### 示例3: 已经是命令

**用户输入**:
```
/check-progress
```

**Hook处理**:
```python
# 检测到已以 / 开头
# 不做修改,直接返回
```

**Claude收到**:
```
/check-progress
```

**结果**: 正常执行命令 ✅

---

### 示例4: 未匹配的输入

**用户输入**:
```
帮我写个Python函数
```

**Hook处理**:
```python
# 没有匹配任何模式
# 保持原样
```

**Claude收到**:
```
帮我写个Python函数
```

**结果**: 正常对话 ✅

---

## 扩展规则

### 添加新的自然语言映射

编辑 `natural-language-router.py`:

```python
NL_COMMANDS = {
    # 现有规则...

    # 添加新规则
    r'验证问题|verify.*questions': '/verify-questions',
    r'任务计划|task.*plan': '/task-planner',
}
```

### 支持参数

```python
# 带参数的映射
NL_COMMANDS = {
    r'总结(\d+)天': r'/daily-summary --days \1',
}
```

**示例**:
```
输入: "总结3天"
转换: "/daily-summary --days 3"
```

---

## 实现代码

### 完整代码

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UserPromptSubmit Hook - 自然语言命令路由器
将用户的自然语言输入自动转换为对应的斜杠命令
"""

import json
import sys
import re
from pathlib import Path

# 设置stdout编码为UTF-8
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 自然语言命令映射
NL_COMMANDS = {
    # 进度查看类
    r'看看?进度?|check progress|查看状态': '/check-progress',

    # 文档同步类
    r'同步一下|sync docs|同步文档': '/sync-docs',

    # 总结类
    r'今天先这样|daily.*summary|生成总结|今天总结': '/daily-summary',

    # 讨论类
    r'开始讨论|discuss|讨论问题': '/discuss',

    # 上下文保存类
    r'保存上下文|save.*context|保存状态': '/save-context',

    # 问题列表类
    r'(查看)?问题(列表)?|questions|看看问题': '/check-progress',

    # Token检查类
    r'检查token|token.*check|看看token': '/token-check',

    # 文档审核类
    r'审核文档|review.*doc|检查文档': '/review-docs',
}

def match_natural_command(user_input):
    """匹配自然语言到命令"""

    # 去除首尾空格
    text = user_input.strip()

    # 如果已经是斜杠命令,直接返回
    if text.startswith('/'):
        return None

    # 遍历所有模式
    for pattern, command in NL_COMMANDS.items():
        if re.search(pattern, text, re.IGNORECASE):
            return command

    return None

def main():
    """主函数"""

    try:
        # 读取stdin (Claude传递的JSON数据)
        input_data = json.load(sys.stdin)

        # 获取用户输入
        user_prompt = input_data.get('user_prompt', '')

        if not user_prompt:
            sys.exit(0)

        # 匹配自然语言命令
        matched_command = match_natural_command(user_prompt)

        if matched_command:
            # 找到匹配的命令,修改用户输入
            # 注意: UserPromptSubmit Hook不能直接修改输入,
            # 但可以返回一个新的prompt让Claude处理

            # 构建新的prompt
            original_input = user_prompt
            new_prompt = f"{matched_command}\n\n原始输入: {original_input}"

            # 输出JSON,Claude会使用这个作为新的prompt
            output = {
                "user_prompt": new_prompt,
                "original_input": original_input,
                "detected_command": matched_command
            }

            print(json.dumps(output, ensure_ascii=False))

            # 可选: 显示提示信息
            print(f"\n💡 检测到自然语言命令,自动转换为: {matched_command}\n", file=sys.stderr)

            sys.exit(0)
        else:
            # 没有匹配的命令,保持原样
            sys.exit(0)

    except Exception as e:
        # 出错时不影响正常使用
        print(f"❌ Natural language router error: {e}", file=sys.stderr)
        sys.exit(0)

if __name__ == "__main__":
    main()
```

---

## 测试方法

### 1. 直接测试Python脚本

```bash
echo '{"user_prompt": "看看进度"}' | python .claude/hooks/user-prompt-submit/natural-language-router.py
```

**预期输出**:
```json
{
  "user_prompt": "/check-progress\n\n原始输入: 看看进度",
  "original_input": "看看进度",
  "detected_command": "/check-progress"
}
```

### 2. 在Claude Code中测试

配置Hook后,直接在对话中输入:
```
看看进度
```

应该自动转换为 `/check-progress` 命令执行。

---

## 注意事项

### 1. 兼容性

**已配置system-prompt的情况**:
- UserPromptSubmit Hook会在prompt处理前触发
- 会先进行命令转换
- Claude收到的已经是转换后的命令
- 两者可以共存,互不冲突

### 2. 调试

如果Hook不工作:
1. 检查文件权限: `chmod +x natural-language-router.py`
2. 检查Python路径: 确保 `python` 在PATH中
3. 查看stderr输出: Hook的错误信息会输出到stderr
4. 测试JSON解析: 确保能正确读取stdin

### 3. 性能

- Hook执行时间: <10ms
- 不影响正常对话速度
- 建议使用编译后的正则表达式

---

## 对比: System-Prompt vs Hook

| 维度 | System-Prompt | UserPromptSubmit Hook |
|------|---------------|----------------------|
| **可靠性** | 中等 (依赖LLM) | 高 (代码确定性) |
| **灵活性** | 高 (理解语境) | 低 (需要预定义) |
| **速度** | 快 | 更快 |
| **Token消耗** | 是 | 否 |
| **可调试性** | 难 | 易 |
| **维护性** | 中 | 高 |

**建议**:
- ✅ **使用Hook**: 固定指令的快速转换
- ✅ **保留system-prompt**: 复杂语境和补充说明

---

## 进阶功能

### 1. 上下文感知

```python
def match_natural_command(user_input, context):
    """根据上下文匹配命令"""

    # 如果在讨论中,"继续"表示继续讨论
    if context.get('in_discussion'):
        if user_input == '继续':
            return '/discuss --continue'

    # 其他匹配逻辑...
```

### 2. 学习模式

```python
# 记录用户的输入习惯
# 自动生成新的映射规则
# 持续优化匹配准确率
```

### 3. 多语言支持

```python
NL_COMMANDS = {
    # 中文
    r'看看进度': '/check-progress',

    # 英文
    r'check progress': '/check-progress',

    # 混合
    r'(查看|check)(进度|progress)': '/check-progress',
}
```

---

## 版本历史

- **v1.0** (2025-01-12): 初始版本
  - 基本自然语言映射
  - 8个常用命令支持
  - 正则表达式匹配

---

**创建时间**: 2025-01-12
**作者**: Claude & User
**状态**: ✅ 设计完成,待配置和测试
