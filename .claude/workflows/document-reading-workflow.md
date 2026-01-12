# Claude工作流程规范

> **版本**: v1.0
> **创建日期**: 2026-01-11
> **目的**: 避免重复错误，提高工作效率
> **触发**: ERR-20260111-03（读取过期文档导致的严重错误）

---

## 🚨 核心原则

### 1. 文档时效性验证 ⭐⭐⭐

**在读取任何文档前，必须执行**：

```python
# 伪代码
def read_document(file_path):
    # Step 1: 检查文件名是否包含日期
    if has_date_in_filename(file_path):
        date = extract_date(file_path)
        if is_older_than(date, days=7):
            warn(f"文档可能已过期: {file_path}")

    # Step 2: 检查文件内容头部是否有版本信息
    content = read_first_lines(file_path, 10)
    if has_version_info(content):
        version = extract_version(content)
        date = extract_update_date(content)
        log(f"文档版本: {version}, 更新日期: {date}")

    # Step 3: 验证是否有更新的版本
    latest_version = find_latest_version(file_path)
    if latest_version != file_path:
        warn(f"发现更新版本: {latest_version}")
        ask_user("是否读取最新版本？")

    return read_file(file_path)
```

**检查清单**：
- ✅ 文件名是否包含日期？（如`_2025-01-06.md`）
- ✅ 文档头部是否有版本信息？
- ✅ 文档头部是否有"最后更新"日期？
- ✅ 是否存在同名但更新版本的文档？
- ✅ 是否存在archive目录下的更新版本？

---

### 2. 文档优先级规则

**读取优先级**（从高到低）：

```
1. 🟢 实际状态文档 > 🟡 设计文档 > 🔴 总结文档

优先级示例：
✅ gamejam-planning-lecture-discussion.md (实际讨论状态)
✅ 评分维度详细指南_v1.0.md (设计文档)
❌ 未讨论问题总结_2025-01-06.md (过期总结)
```

**规则**：
- ✅ 优先读取带`discussion`、`status`、`tracking`的文档
- ✅ 优先读取版本号最高的文档（v2.0 > v1.0 > v0.9）
- ✅ 优先读取更新日期最新的文档
- ❌ 避免读取`summary`、`总结`、`未讨论`等关键词的文档（除非确认最新）

---

### 3. 上下文感知机制

**在执行命令前，检查当前对话历史**：

```python
# 伪代码
def execute_command(command):
    # Step 1: 检查是否是context相关命令
    if command in ['/discuss', '/check-progress', '/sync']:

        # Step 2: 检查当前对话历史
        recent_messages = get_recent_messages(count=50)

        # Step 3: 查找相关文档提及
        mentioned_docs = extract_document_paths(recent_messages)

        # Step 4: 优先使用最近提及的文档
        if mentioned_docs:
            docs = sort_by_recency(mentioned_docs)
            log(f"使用最近提及的文档: {docs[0]}")
            return process_with_docs(docs[0])

        # Step 5: 否则查找工作目录下的最新文档
        latest_doc = find_latest_document_in_cwd()
        if latest_doc:
            log(f"使用最新文档: {latest_doc}")
            return process_with_docs(latest_doc)

    return execute(command)
```

---

### 4. 问题确认流程

**在提出任何问题前**：

```
Step 1: 验证问题状态
├─ 检查相关设计文档
│  └─ 文档头部是否有"✅ 已确认"标记？
├─ 检查问题追踪清单
│  └─ 该问题是否标记为"已完成"？
└─ 检查实际状态文档
   └─ 该问题的实施状态是否为"已完成"？

Step 2: 如果问题已完成
├─ 标记为"已确认"
├─ 记录确认文档路径
└─ 跳过该问题

Step 3: 如果问题未确认
├─ 准备问题背景
├─ 查阅相关设计文档
└─ 提出问题
```

---

## 📋 具体工作流程

### 场景1: 用户说"回到XX项目"

**错误做法** ❌：
```
1. 读取名为"XX项目-待确认问题.md"的文档
2. 列出所有问题
3. 向用户提出
```

**正确做法** ✅：
```
1. 检查最近对话历史中提到的XX项目文档
2. 查找"XX项目-问题追踪清单.md"（最新版）
3. 查找"XX项目-实际状态.md"（如discussion文档）
4. 对比多个文档，确认最新状态
5. 只提出真正未确认的问题
```

---

### 场景2: 用户执行`/discuss`命令

**错误做法** ❌：
```
1. 读取固定的"未讨论问题总结.md"
2. 显示下一个待讨论问题
```

**正确做法** ✅：
```
1. 检查当前对话历史，确定讨论的项目
2. 读取"{项目名}-discussion.md"（实际讨论状态）
3. 检查文档头部：
   - 已确认问题数量 (38/38)
   - 待讨论问题数量 (0/38)
   - 当前状态 (讨论完成/进行中)
4. 根据实际状态给出反馈
```

---

### 场景3: 需要检查项目进度

**错误做法** ❌：
```
1. 读取"项目计划.md"
2. 列出所有计划中的任务
```

**正确做法** ✅：
```
1. 读取"{项目名}-问题追踪清单.md"
2. 检查"✅ 已完成"部分
3. 检查"🟡 待确认"部分
4. 生成准确的进度报告
```

---

## 🔍 文档验证Checklist

在读取任何文档前，问自己：

- [ ] 文档名称是否包含日期？如果是，日期是否过期？
- [ ] 文档头部是否有版本信息？如果是，是否是最新版本？
- [ ] 是否存在同名但版本号更高的文档？
- [ ] 是否存在实际状态文档（discussion/tracking）？
- [ ] 文档内容中是否有"已过期"、"已废弃"等标记？
- [ ] 该文档是设计文档、总结文档，还是状态文档？

---

## 🛡️ 防御性编程

### 文档读取函数模板

```python
def safe_read_document(file_path, purpose="读取"):
    """
    安全读取文档，包含时效性验证
    """
    # 1. 检查文件是否存在
    if not file_exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")

    # 2. 检查文件名中的日期
    filename_date = extract_date_from_filename(file_path)
    if filename_date and is_older_than(filename_date, days=7):
        logger.warning(f"⚠️ 文档可能已过期（文件名日期: {filename_date}）")

    # 3. 读取文档头部（前10行）
    header = read_first_lines(file_path, 10)

    # 4. 检查版本信息
    version_info = extract_version_info(header)
    if version_info:
        logger.info(f"📄 文档版本: {version_info.get('version')}, 更新日期: {version_info.get('date')}")

        # 5. 检查是否有更新版本
        if version_info.get('status') == '已废弃':
            raise ValueError(f"文档已废弃: {file_path}")

    # 6. 检查是否是总结文档
    if is_summary_document(file_path) and purpose == "确认状态":
        logger.warning(f"⚠️ 正在读取总结文档，建议优先读取实际状态文档")

        # 尝试查找对应的状态文档
        status_doc = find_status_document(file_path)
        if status_doc:
            logger.info(f"💡 找到状态文档: {status_doc}")
            if ask_user("是否读取状态文档？"):
                file_path = status_doc

    # 7. 读取并返回
    content = read_file(file_path)
    return content
```

---

## 📚 相关资源

- [错误日志](error-log.md)
- [惊蛰计划问题追踪清单](惊蛰计划问题追踪清单.md)
- [文档归档规范](../docs/archiving.md)

---

## 🔄 版本历史

- **v1.0** (2026-01-11): 初始版本，响应ERR-20260111-03

---

**最后更新**: 2026-01-11
**维护者**: Claude (Assistant)
**状态**: ✅ 活跃
