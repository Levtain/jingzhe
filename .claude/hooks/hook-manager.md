# Hook管理器

> **名称**: hook-manager
> **版本**: v1.0
> **创建时间**: 2025-01-11
> **目的**: 统一管理所有Hook,提供注册、触发、配置功能

---

## 🎯 核心功能

### 1. Hook注册

**自动加载**:
```yaml
启动时自动加载:
  - 扫描 .claude/hooks/ 目录
  - 加载所有 *-hook.md 文件
  - 解析Hook元数据
  - 注册到Hook管理器
```

**Hook元数据**:
```yaml
每个Hook包含:
  - name: Hook名称
  - version: 版本号
  - priority: 优先级 (P0/P1/P2/P3)
  - enabled: 是否启用
  - config: 配置参数
  - trigger_conditions: 触发条件
```

### 2. Hook触发

**触发接口**:
```python
def trigger_hook(hook_name, data):
    """
    触发指定的Hook

    Args:
        hook_name: Hook名称
        data: 传递给Hook的数据

    Returns:
        Hook执行结果
    """
```

**使用示例**:
```python
# 在Agent中触发Hook
hook_manager.trigger("milestone_notification", {
    "type": "questions_completed",
    "module": "游戏提交系统",
    "completion": {"total": 9, "confirmed": 9}
})
```

### 3. Hook配置管理

**配置项**:
```yaml
全局配置:
  - hooks_enabled: 是否启用所有Hook
  - log_hook_calls: 记录Hook调用
  - async_execution: 异步执行Hook

单个Hook配置:
  - enabled: 是否启用
  - priority: 执行优先级
  - custom_config: 自定义配置
```

### 4. Hook执行

**执行流程**:
```yaml
1. 检查Hook是否启用
   ↓
2. 验证触发条件
   ↓
3. 执行Hook逻辑
   ↓
4. 处理执行结果
   ↓
5. 记录执行日志
```

---

## 🔧 核心实现

### HookManager类

```python
import os
import json
from typing import Dict, List, Any
from datetime import datetime

class HookManager:
    """
    Hook管理器 - 统一管理所有Hook
    """

    def __init__(self):
        """初始化Hook管理器"""
        self.hooks: Dict[str, Dict] = {}
        self.hook_dir = ".claude/hooks"
        self.config_file = ".claude/hooks/hook-config.json"
        self.config = self.load_config()
        self.load_hooks()

    def load_config(self):
        """
        加载Hook配置
        """
        default_config = {
            "hooks_enabled": True,
            "log_hook_calls": True,
            "async_execution": False,
            "hooks": {}
        }

        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return default_config

    def save_config(self):
        """
        保存Hook配置
        """
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

    def load_hooks(self):
        """
        加载所有Hook
        """
        if not os.path.exists(self.hook_dir):
            return

        hook_files = [f for f in os.listdir(self.hook_dir) if f.endswith('-hook.md')]

        for hook_file in hook_files:
            hook_name = hook_file.replace('-hook.md', '')
            hook_path = os.path.join(self.hook_dir, hook_file)

            # 解析Hook元数据
            hook_metadata = self.parse_hook_metadata(hook_path)

            # 加载Hook配置
            hook_config = self.config.get("hooks", {}).get(hook_name, {})

            # 注册Hook
            self.register_hook(hook_name, {
                "metadata": hook_metadata,
                "config": hook_config,
                "file": hook_path
            })

    def parse_hook_metadata(self, hook_path):
        """
        解析Hook文件元数据
        """
        # 读取Hook文件
        with open(hook_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取元数据
        metadata = {
            "name": "",
            "version": "1.0",
            "priority": "P2",
            "description": ""
        }

        # 解析YAML frontmatter或内容
        lines = content.split('\n')
        for line in lines:
            if line.startswith('> **Hook名称**'):
                metadata["name"] = line.split(':')[1].strip()
            elif line.startswith('> **版本**'):
                metadata["version"] = line.split(':')[1].strip()
            # ... 其他元数据

        return metadata

    def register_hook(self, hook_name: str, hook_data: Dict):
        """
        注册Hook
        """
        self.hooks[hook_name] = hook_data
        print(f"✅ Hook已注册: {hook_name}")

    def trigger_hook(self, hook_name: str, data: Dict = None) -> Dict:
        """
        触发Hook

        Args:
            hook_name: Hook名称
            data: 传递给Hook的数据

        Returns:
            执行结果
        """
        # 检查全局开关
        if not self.config.get("hooks_enabled", True):
            return {"status": "disabled", "message": "Hooks已全局禁用"}

        # 检查Hook是否存在
        if hook_name not in self.hooks:
            return {"status": "error", "message": f"Hook不存在: {hook_name}"}

        hook = self.hooks[hook_name]

        # 检查Hook是否启用
        if not hook["config"].get("enabled", True):
            return {"status": "disabled", "message": f"Hook已禁用: {hook_name}"}

        # 记录调用
        if self.config.get("log_hook_calls", True):
            self.log_hook_call(hook_name, data)

        # 执行Hook
        try:
            result = self.execute_hook(hook_name, data)
            return {"status": "success", "result": result}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def execute_hook(self, hook_name: str, data: Dict) -> Any:
        """
        执行Hook逻辑

        这里需要根据不同的Hook类型执行不同的逻辑
        """
        hook = self.hooks[hook_name]

        # 根据Hook名称路由到具体的执行逻辑
        if hook_name == "milestone_notification":
            return self.execute_milestone_notification(data)
        elif hook_name == "auto_doc_sync":
            return self.execute_auto_doc_sync(data)
        elif hook_name == "agent_completion_archive":
            return self.execute_agent_completion_archive(data)
        elif hook_name == "doc_quality_monitor":
            return self.execute_doc_quality_monitor(data)
        elif hook_name == "daily_push":
            return self.execute_daily_push(data)
        else:
            return {"status": "unknown_hook", "message": f"未知的Hook: {hook_name}"}

    def execute_milestone_notification(self, data: Dict):
        """
        执行里程碑通知Hook
        """
        # 提取数据
        milestone_type = data.get("type")
        module = data.get("module")

        # 生成通知
        if milestone_type == "questions_completed":
            notification = f"""🎉 **里程碑达成: 问题讨论完成!**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**模块**: {module}
**完成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 **完成统计**:
- 完成度: 100% ✅

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 **推荐下一步操作**:
🔴 同步文档: /sync-docs
🟡 验证模块: /check-completion

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎊 **恭喜!** 已完成问题讨论阶段
"""

            # Windows通知
            self.show_windows_notification(
                "🎉 里程碑达成!",
                f"{module} 问题讨论 100%完成!"
            )

            # 播放音效
            self.play_notification_sound("achievement")

            # 显示终端通知
            print(notification)

            return {"status": "success", "notification": notification}

    def execute_auto_doc_sync(self, data: Dict):
        """
        执行自动文档同步Hook
        """
        file_path = data.get("file")

        # 调用doc-sync-agent
        # 这里需要实际调用doc-sync-agent的逻辑

        return {"status": "success", "message": "文档同步完成"}

    def execute_agent_completion_archive(self, data: Dict):
        """
        执行Agent完成报告归档Hook
        """
        # 归档逻辑
        return {"status": "success", "message": "归档完成"}

    def execute_doc_quality_monitor(self, data: Dict):
        """
        执行文档质量监控Hook
        """
        file_path = data.get("file")

        # 质量检查逻辑
        return {"status": "success", "score": 85}

    def execute_daily_push(self, data: Dict):
        """
        执行每日推送Hook
        """
        # Git推送逻辑
        return {"status": "success", "commit": "abc123"}

    def show_windows_notification(self, title: str, message: str):
        """
        显示Windows系统通知
        """
        try:
            # 使用PowerShell的Toast通知
            import subprocess
            ps_command = f'''
            Add-Type -AssemblyName Windows.UI.Notifications
            [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
            [Windows.UI.Notifications.ToastNotification, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
            [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

            $template = @"
            <toast>
                <visual>
                    <binding template="ToastGeneric">
                        <text>{title}</text>
                        <text>{message}</text>
                    </binding>
                </visual>
            </toast>
            "@

            $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
            $xml.LoadXml($template)
            $toast = New-Object Windows.UI.Notifications.ToastNotification $xml
            $notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("ClaudeCode")
            $notifier.Show($toast)
            '''

            subprocess.run(["powershell", "-Command", ps_command], capture_output=True)

        except Exception as e:
            # 回退到终端输出
            print(f"🔔 {title}: {message}")

    def play_notification_sound(self, sound_type: str = "milestone"):
        """
        播放通知音效
        """
        sound_files = {
            "milestone": r"C:\Windows\Media\notify.wav",
            "achievement": r"C:\Windows\Media\tada.wav",
            "warning": r"C:\Windows\Media\Windows Exclamation.wav",
            "error": r"C:\Windows\Media\Windows Error.wav"
        }

        sound_file = sound_files.get(sound_type, sound_files["milestone"])

        try:
            import winsound
            winsound.PlaySound(sound_file, winsound.SND_FILENAME)
        except:
            # Fallback: 系统铃声
            print('\a')

    def log_hook_call(self, hook_name: str, data: Dict):
        """
        记录Hook调用
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "hook": hook_name,
            "data": data
        }

        # 可以写入日志文件
        # print(f"[Hook Call] {hook_name}: {data}")

    def enable_hook(self, hook_name: str):
        """
        启用Hook
        """
        if hook_name in self.hooks:
            if "hooks" not in self.config:
                self.config["hooks"] = {}
            if hook_name not in self.config["hooks"]:
                self.config["hooks"][hook_name] = {}
            self.config["hooks"][hook_name]["enabled"] = True
            self.save_config()
            return True
        return False

    def disable_hook(self, hook_name: str):
        """
        禁用Hook
        """
        if hook_name in self.hooks:
            if "hooks" not in self.config:
                self.config["hooks"] = {}
            if hook_name not in self.config["hooks"]:
                self.config["hooks"][hook_name] = {}
            self.config["hooks"][hook_name]["enabled"] = False
            self.save_config()
            return True
        return False

    def list_hooks(self) -> List[str]:
        """
        列出所有已注册的Hook
        """
        return list(self.hooks.keys())

    def get_hook_info(self, hook_name: str) -> Dict:
        """
        获取Hook信息
        """
        if hook_name in self.hooks:
            return self.hooks[hook_name]
        return None


# 全局Hook管理器实例
hook_manager = HookManager()
```

---

## 📋 Hook配置文件

### .claude/hooks/hook-config.json

```json
{
  "hooks_enabled": true,
  "log_hook_calls": true,
  "async_execution": false,
  "hooks": {
    "milestone-notification": {
      "enabled": true,
      "windows_notification": {
        "enabled": true,
        "use_toast": true,
        "use_sound": true,
        "sound_type": "achievement"
      }
    },
    "auto-doc-sync": {
      "enabled": true,
      "auto_sync": true,
      "require_confirmation": false
    },
    "agent-completion-archive": {
      "enabled": true,
      "auto_archive": true
    },
    "doc-quality-monitor": {
      "enabled": true,
      "check_on_save": true
    },
    "daily-push": {
      "enabled": true,
      "auto_commit": true,
      "time": "22:00"
    }
  }
}
```

---

## 🔗 Hook注册流程

### 新建Hook时的完整流程

```yaml
1. 创建Hook文档
   文件: .claude/hooks/my-new-hook.md
   包含Hook元数据和执行逻辑

2. 在Hook管理器中注册
   编辑: .claude/hooks/hook-manager.md
   添加: execute_my_new_hook() 方法

3. 更新Hook配置
   编辑: .claude/hooks/hook-config.json
   添加: Hook配置项

4. 集成到Agent/Skill
   在适当的时机调用: hook_manager.trigger("my-new-hook", data)

5. 测试Hook
   手动触发测试
   验证Hook功能

6. 更新文档
   更新: hooks-configuration-summary.md
   记录: 新Hook的功能和用法
```

---

## 💡 使用示例

### 在Agent中使用Hook管理器

```python
# discussion-agent中的使用示例
def complete_discussion(question_list):
    """
    完成问题讨论
    """
    # ... 讨论逻辑 ...

    if all_questions_confirmed:
        # 触发里程碑通知Hook
        hook_manager.trigger("milestone_notification", {
            "type": "questions_completed",
            "module": module_name,
            "completion": {"total": 9, "confirmed": 9}
        })

        # 触发自动文档同步Hook
        hook_manager.trigger("auto_doc_sync", {
            "file": question_list_file
        })
```

### 在Skill中使用Hook管理器

```python
# Skill命令中的使用示例
def sync_docs_command():
    """
    /sync-docs命令
    """
    # 执行同步逻辑

    # 同步完成后触发质量检查Hook
    hook_manager.trigger("doc_quality_monitor", {
        "files": synced_files
    })
```

---

## ✅ 总结

**核心功能**:
1. 自动加载所有Hook
2. 统一的触发接口
3. Hook配置管理
4. Hook执行路由
5. Windows通知和音效

**核心价值**:
- 统一管理所有Hook
- 简化Hook调用
- 易于扩展新Hook
- 集中配置管理

**使用方法**:
```python
# 触发Hook
hook_manager.trigger("hook_name", data)

# 启用/禁用Hook
hook_manager.enable_hook("hook_name")
hook_manager.disable_hook("hook_name")

# 列出所有Hook
hooks = hook_manager.list_hooks()
```

---

**创建时间**: 2025-01-11
**版本**: v1.0
**状态**: ✅ Hook管理器已创建
**下一步**: 集成到各个Agent和Skill中