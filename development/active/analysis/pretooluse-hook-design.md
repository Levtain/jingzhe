# PreToolUse Hook - 自动Skill调用检查

> **在Write/Edit工具执行前自动检查是否需要调用docs skill**
> **创建时间**: 2025-01-11
> **类型**: PreToolUse Hook
> **触发时机**: 每次使用Write/Edit工具之前

---

## 🎯 工作原理

```
用户请求: Write/Edit工具
    ↓
PreToolUse Hook触发
    ↓
检查: 目标文件是否为.md文档？
    ↓
是.md → 检查是否已调用docs skill？
    ↓
未调用 → ❌ 阻止执行，要求先调用skill
已调用 → ✅ 允许执行
    ↓
不是.md → ✅ 允许执行
```

---

## 📋 Hook配置

### 位置

`.claude/settings.json`

### 配置

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "检查即将执行的操作:\n\n操作: $TOOL_NAME\n文件: $FILE_PATH\n\n判断:\n1. 这是.md文档任务吗？\n   - 如果是 → 必须使用 docs-write 或 docs-review skill\n   - 如果不是 → 可以直接执行\n\n2. 如果是.md文档，你是否已经调用了对应的docs skill？\n   - 如果已调用 → 继续执行\n   - 如果未调用 → 必须先调用skill，不能直接使用Write/Edit\n\n如果是.md文档且未调用skill，请返回错误并要求先调用docs skill。",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

---

## 🔍 检查逻辑

### 判断1: 文件类型检查

```
文件路径: $FILE_PATH
    ↓
检查: 文件扩展名是否为.md？
    ↓
是.md → 进入判断2
否.md → 允许执行
```

### 判断2: Skill调用检查

```
如果是.md文档
    ↓
检查: AI是否已调用docs-write或docs-review？
    ↓
已调用 → 允许执行Write/Edit
未调用 → 阻止执行，返回错误
```

---

## 💡 使用场景

### 场景1: 直接使用Write工具（错误）

```
用户: 创建一个README文档
我: [准备使用Write工具]

PreToolUse Hook触发:
  检查: README.md是.md文档吗？→ 是
  检查: 是否调用了docs skill？→ 否

  ❌ 错误：必须先调用docs-write skill！

  正确做法：
  1. 调用 docs-write skill
  2. Skill会使用Write工具创建文档
```

### 场景2: 通过docs-write skill（正确）

```
用户: 创建一个README文档
我: [调用 docs-write skill]

PreToolUse Hook触发:
  检查: README.md是.md文档吗？→ 是
  检查: 是否调用了docs skill？→ 是（通过skill调用）

  ✅ 允许执行
```

### 场景3: 编辑代码文件（允许）

```
用户: 修改Python代码
我: [使用Edit工具]

PreToolUse Hook触发:
  检查: .py文件是.md文档吗？→ 否

  ✅ 允许执行
```

---

## 🚨 错误提示

### 当Hook阻止执行时

**AI会看到**：

```
❌ 错误：检测到.md文档操作，但未调用docs skill

操作: Write
文件: README.md

问题：你不能直接使用Write/Edit工具创建.md文档

正确做法：
1. 调用 docs-write skill
2. Skill会使用Write工具创建文档
3. 文档会按照规范格式撰写

请先调用docs-write skill，然后重试。
```

---

## 📊 效果对比

### 没有PreToolUse Hook（之前）

```
用户: 写一个README
我: [直接用Write工具]
❌ 错误：没有使用docs skill
❌ 文档可能不符合规范
```

### 有PreToolUse Hook（现在）

```
用户: 写一个README
我: [准备用Write工具]
   [PreToolUse Hook触发]
   ❌ 阻止：必须先调用docs skill

我: [调用 docs-write skill]
   [Skill使用Write工具]
✅ 正确：文档符合规范
```

---

## 🎯 核心优势

### 优势1: 完全自动化

**不需要**：
- ❌ AI手动检查
- ❌ 用户提醒
- ❌ 记忆力依赖

**自动**：
- ✅ Hook自动触发
- ✅ 自动检查
- ✅ 自动阻止

### 优势2: 强制执行

**无法绕过**：
- ✅ Hook在工具执行前触发
- ✅ 必须通过检查才能执行
- ✅ 不通过就不允许执行

### 优势3: 及时反馈

**立即告知**：
- ✅ 在执行前就阻止
- ✅ 明确告知正确做法
- ✅ 避免浪费操作

---

## 🔄 与其他机制配合

### 与SessionStart Hook配合

```
SessionStart: 加载Skill使用规则
PreToolUse: 执行前强制检查
两者结合: 确保Skill使用
```

### 与docs skill配合

```
PreToolUse Hook检查 →
要求调用docs skill →
docs skill执行操作 →
符合规范的结果
```

---

## 📋 测试验证

### 测试1: 尝试直接写文档

```
操作: 尝试Write创建README.md

预期: PreToolUse Hook阻止执行
实际: ❌ 错误，要求先调用docs skill

结果: ✅ 通过
```

### 测试2: 通过skill写文档

```
操作: 通过docs-write skill创建README.md

预期: PreToolUse Hook允许执行
实际: ✅ 文档创建成功

结果: ✅ 通过
```

### 测试3: 编辑代码文件

```
操作: Edit修改Python代码

预期: PreToolUse Hook允许执行
实际: ✅ 代码修改成功

结果: ✅ 通过
```

---

## 💡 设计思路

### 为什么用PreToolUse而不是PostToolUse？

**PreToolUse的优势**：
- ✅ 在执行前阻止，避免错误操作
- ✅ 强制正确流程
- ✅ 即时反馈

**PostToolUse的不足**：
- ❌ 执行后才发现错误
- ❌ 可能已经产生不规范文档
- ❌ 需要重新操作

### 为什么不用SessionStart提示？

**SessionStart的不足**：
- ❌ 依赖AI记忆
- ❌ 容易忘记
- ❌ 无法实时检查

**PreToolUse的优势**：
- ✅ 每次操作都检查
- ✅ 不依赖记忆
- ✅ 强制执行

---

## 🎉 总结

通过PreToolUse Hook：

1. ✅ **完全自动化** - 不需要AI记忆
2. ✅ **强制执行** - 无法绕过检查
3. ✅ **及时反馈** - 执行前就阻止
4. ✅ **配合skill** - 确保文档规范

这是比"被动检查"更优雅、更可靠的解决方案！

---

**版本**: v1.0
**创建时间**: 2025-01-11
**类型**: PreToolUse Hook
**状态**: ✅ 已配置
