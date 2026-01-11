# 文档质量自动监控Hook

> **Hook名称**: doc-quality-monitor-hook
> **版本**: v1.0
> **创建时间**: 2025-01-11
> **目的**: 自动监控文档质量,发现问题立即提示

---

## 🎯 核心功能

### 1. 文档变更检测

**触发时机**:
```yaml
触发事件:
  - 文档保存时
  - 文档提交前
  - 定期扫描(可选)

监控范围:
  - development/issues/*.md
  - development/analysis/*.md
  - docs/design/*.md
  - .claude/agents/*.md
  - .claude/commands/*.md
```

### 2. 质量检查项

**必查项 (P0)**:
```yaml
1. 格式检查
   - Markdown语法正确
   - 标题层级规范
   - 列表格式正确

2. 内容完整性
   - 必需章节齐全
   - 关键信息完整
   - 无明显遗漏

3. 交叉引用
   - 链接有效
   - 引用路径正确
   - 无失效链接

4. 版本号一致性
   - 版本号格式统一
   - 版本号同步
   - 更新日期一致
```

**检查项 (P1)**:
```yaml
5. 命名规范
   - 文件名符合规范
   - 标题格式一致
   - 术语统一

6. 代码示例
   - 代码块语法高亮
   - 代码示例完整
   - 逻辑正确

7. 图表引用
   - 图表编号连续
   - 图表说明清晰
   - 引用正确
```

**优化项 (P2)**:
```yaml
8. 可读性
   - 语言简洁
   - 逻辑清晰
   - 结构合理

9. 一致性
   - 风格统一
   - 用词一致
   - 格式一致
```

### 3. 问题报告

**报告级别**:
```yaml
级别1: 错误 (Error)
  - 阻塞性问题
  - 必须修复
  - 示例: 失效链接、语法错误

级别2: 警告 (Warning)
  - 建议修复
  - 不影响使用
  - 示例: 版本号不一致、格式不统一

级别3: 建议 (Suggestion)
  - 优化建议
  - 提升质量
  - 示例: 可读性改进、结构优化
```

---

## 🔧 核心函数

### check_document_quality(file_path)

```python
def check_document_quality(file_path):
    """
    检查文档质量
    """
    content = read_file(file_path)

    quality_report = {
        "file": file_path,
        "timestamp": datetime.now().isoformat(),
        "errors": [],
        "warnings": [],
        "suggestions": [],
        "score": 100
    }

    # 必查项 (P0)
    quality_report["errors"].extend(check_format(content))
    quality_report["errors"].extend(check_completeness(content))
    quality_report["errors"].extend(check_cross_references(content, file_path))
    quality_report["errors"].extend(check_version_consistency(content))

    # 检查项 (P1)
    quality_report["warnings"].extend(check_naming_convention(file_path, content))
    quality_report["warnings"].extend(check_code_blocks(content))
    quality_report["warnings"].extend(check_figure_references(content))

    # 优化项 (P2)
    quality_report["suggestions"].extend(check_readability(content))
    quality_report["suggestions"].extend(check_consistency(content))

    # 计算得分
    quality_report["score"] = calculate_quality_score(quality_report)

    return quality_report
```

### check_format(content)

```python
def check_format(content):
    """
    检查Markdown格式
    """
    errors = []

    # 检查标题层级
    lines = content.split("\n")
    for i, line in enumerate(lines, 1):
        if line.startswith("#"):
            level = line.count("#")
            if level > 6:
                errors.append({
                    "line": i,
                    "type": "format",
                    "message": f"标题层级超过6级: {line}",
                    "severity": "error"
                })

    # 检查列表格式
    if re.search(r"^\s*[-*+]\s[^-\s]", content, re.MULTILINE):
        # 无序列表格式正确
        pass
    else:
        errors.append({
            "type": "format",
            "message": "列表格式可能不规范",
            "severity": "warning"
        })

    return errors
```

### check_cross_references(content, file_path)

```python
def check_cross_references(content, file_path):
    """
    检查交叉引用
    """
    errors = []

    # 提取所有链接
    links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content)

    for text, url in links:
        # 检查相对路径链接
        if url.startswith("../") or url.startswith("./"):
            target_path = os.path.normpath(
                os.path.join(os.path.dirname(file_path), url)
            )

            if not os.path.exists(target_path):
                errors.append({
                    "type": "cross_reference",
                    "message": f"失效链接: [{text}]({url})",
                    "severity": "error",
                    "link": url
                })

        # 检查锚点链接
        if url.startswith("#"):
            anchor = url[1:]
            if not re.search(rf"#{re.escape(anchor)}\b", content):
                errors.append({
                    "type": "cross_reference",
                    "message": f"失效锚点: #{anchor}",
                    "severity": "error",
                    "anchor": anchor
                })

    return errors
```

### check_version_consistency(content)

```python
def check_version_consistency(content):
    """
    检查版本号一致性
    """
    errors = []

    # 提取所有版本号
    versions = re.findall(r"v(\d+\.\d+(\.\d+)?)", content)

    if versions:
        # 检查是否有多个不同的版本号
        unique_versions = set([v[0] for v in versions])

        if len(unique_versions) > 1:
            errors.append({
                "type": "version_consistency",
                "message": f"发现多个版本号: {', '.join(unique_versions)}",
                "severity": "warning",
                "versions": list(unique_versions)
            })

    return errors
```

### calculate_quality_score(report)

```python
def calculate_quality_score(report):
    """
    计算质量得分
    """
    score = 100

    # 错误扣分(每个-10分)
    score -= len(report["errors"]) * 10

    # 警告扣分(每个-2分)
    score -= len(report["warnings"]) * 2

    # 建议不扣分,仅作参考

    return max(0, score)
```

---

## 📋 Hook触发配置

### 在文档保存时触发

```yaml
触发位置:
  - Write工具保存文档后
  - Edit工具修改文档后

触发方式:
  - 在Write/Edit工具后端调用
  - 自动执行质量检查

配置:
  auto_check_on_save: true
  show_immediate_feedback: true
```

### 在提交前触发

```yaml
触发位置:
  - git commit前
  - /daily-push执行前

触发方式:
  - Git pre-commit hook
  - 或在push命令中集成

配置:
  check_before_commit: true
  block_on_errors: true
```

### 定期扫描

```yaml
触发时机:
  - 每天定时扫描
  - 或手动触发

触发方式:
  - 定时任务
  - /check-doc-quality命令

配置:
  scheduled_scan: false
  scan_time: "02:00"
```

---

## 📊 输出格式

### 质量检查报告

```markdown
📋 **文档质量检查报告**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**文件**: development/issues/game-submission-questions-v2.md
**检查时间**: 2025-01-11 16:30:00

📊 **质量得分**: 85/100

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ **错误** (3个) - 必须修复:

1. [Line 45] 失效链接
   - 问题: [相关设计](../docs/design/不存在的文件.md)
   - 修复: 更新链接路径

2. [Line 120] 标题层级错误
   - 问题: 标题层级超过6级
   - 修复: 调整标题层级

3. [Line 200] Markdown语法错误
   - 问题: 未闭合的代码块
   - 修复: 添加闭合标记

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ **警告** (5个) - 建议修复:

1. 版本号不一致
   - 问题: 发现v1.0和v1.2两个版本号
   - 建议: 统一版本号

2. 文件命名不规范
   - 问题: 文件名包含空格
   - 建议: 使用连字符替换空格

3. 代码示例缺少语言标记
   - 问题: 第150行代码块未指定语言
   - 建议: 添加 ```python 标记

... (其他警告)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 **建议** (2个) - 可选优化:

1. 可读性改进
   - 建议: 第80-100行段落过长,建议拆分

2. 结构优化
   - 建议: 调整章节顺序,更符合逻辑

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 **修复建议**:

优先级1 (立即修复):
1. 修复失效链接
2. 修正标题层级
3. 闭合代码块

优先级2 (尽快修复):
1. 统一版本号
2. 修正文件命名

优先级3 (择机优化):
1. 改进可读性
2. 优化文档结构

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**检查工具**: doc-quality-monitor-hook
**检查耗时**: 0.5秒
```

### 快速反馈(保存时)

```markdown
⚠️ **文档质量提示**

保存了1个错误和2个警告:

❌ [Line 45] 失效链接: ../docs/design/不存在的文件.md
⚠️ [Line 15] 版本号不一致: v1.0 vs v1.2
⚠️ [Line 80] 代码块缺少语言标记

建议修复后重新保存。
查看详细报告: /check-doc-quality
```

---

## 💡 核心价值

### 改进前

```yaml
手动检查流程:
  1. 编写文档
  2. 手动检查质量
  3. 容易遗漏问题
  4. 发现问题滞后
  5. 质量参差不齐

问题:
  - 失效链接难发现
  - 格式不统一
  - 版本号混乱
  - 交叉引用失效
```

### 改进后

```yaml
自动检查流程:
  1. 编写文档
  2. 自动检查质量
  3. 实时发现问题
  4. 立即提示修复
  5. 质量保持一致

优势:
  - 实时质量监控
  - 问题及时发现
  - 标准统一
  - 质量提升
```

---

## ⚙️ 配置选项

### Hook配置

```json
{
  "hooks": {
    "doc-quality-monitor": {
      "enabled": true,
      "check_on_save": true,
      "check_before_commit": true,
      "scheduled_scan": false,
      "scan_time": "02:00",
      "blocking_on_errors": true,
      "show_immediate_feedback": true,
      "quality_threshold": 80,
      "check_rules": {
        "format": true,
        "completeness": true,
        "cross_references": true,
        "version_consistency": true,
        "naming_convention": true,
        "code_blocks": true,
        "readability": false,
        "consistency": true
      }
    }
  }
}
```

---

## 🔗 与其他Hook的配合

### auto-doc-sync-hook

```yaml
配合流程:
  1. 文档同步前
  2. doc-quality-monitor-hook检查质量
  3. 通过后才执行同步
  4. 确保同步的文档质量合格
```

### daily-push-agent

```yaml
配合流程:
  1. 提交前检查
  2. doc-quality-monitor-hook检查所有改动文件
  3. 发现错误则阻止提交
  4. 确保推送的代码质量
```

---

## ✅ 总结

**核心功能**:
1. 文档变更检测
2. 质量检查(格式/完整性/引用/版本号)
3. 问题报告(错误/警告/建议)
4. 修复建议

**核心价值**:
- 实时质量监控
- 问题及时发现
- 标准统一
- 质量提升

**实施建议**:
- 启用保存时检查
- 启用提交前检查
- 设置质量阈值
- 定期查看报告

---

**创建时间**: 2025-01-11
**版本**: v1.0
**状态**: ✅ Hook已定义
**下一步**: 创建命令文档,集成到工作流