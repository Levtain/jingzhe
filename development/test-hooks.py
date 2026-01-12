#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hook输出格式验证器
自动测试所有Hook脚本的输出格式是否符合标准
"""
import json
import subprocess
import sys
import os
from pathlib import Path

# 设置stdout编码为UTF-8
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def test_hook_output(script_path, test_input):
    """测试Hook脚本的输出"""
    script_path = os.path.abspath(script_path)

    if not os.path.exists(script_path):
        return None, f"脚本不存在: {script_path}"

    try:
        result = subprocess.run(
            ["python", script_path],
            input=json.dumps(test_input),
            capture_output=True,
            text=True,
            timeout=10,
            cwd=os.getcwd()
        )

        # 尝试解析JSON输出
        try:
            output = result.stdout.strip()
            if output:
                parsed = json.loads(output)
                return parsed, None
            else:
                return None, "无输出"
        except json.JSONDecodeError as e:
            return None, f"JSON解析失败: {e}\n原始输出: {result.stdout[:200]}"

    except subprocess.TimeoutExpired:
        return None, "Hook执行超时（>10秒）"
    except Exception as e:
        return None, f"执行错误: {e}"

def validate_output_format(output, hook_type):
    """验证输出格式是否符合标准"""
    score = 0
    issues = []

    # 检查标准字段
    if "continue" in output:
        score += 1
    else:
        issues.append("缺少 'continue' 字段")

    if "suppressOutput" in output:
        score += 1
    else:
        issues.append("缺少 'suppressOutput' 字段")

    # PostToolUse应该有systemMessage
    if hook_type == "post_tool_use" and "systemMessage" in output:
        score += 1
    elif hook_type == "post_tool_use":
        issues.append("PostToolUse Hook应该有 'systemMessage' 字段")

    return score, issues

# 测试案例
test_cases = [
    {
        "name": "error-auto-recorder",
        "script": ".claude/hooks/post-tool-use/error-auto-recorder.py",
        "type": "post_tool_use",
        "input": {},  # 空输入应该返回 {"trigger": "none"}
        "expected_trigger": "none"
    },
    {
        "name": "document_sync",
        "script": ".claude/hooks/document_sync.py",
        "type": "post_tool_use",
        "input": {
            "tool_name": "Edit",
            "tool_input": {"file_path": "docs/product/claude.md"},
            "tool_response": {}
        }
    },
    {
        "name": "session_start",
        "script": ".claude/hooks/session_start.py",
        "type": "session_start",
        "input": {}
    }
]

print("="*70)
print("🧪 Hook输出格式验证测试")
print("="*70)
print(f"工作目录: {os.getcwd()}")
print(f"测试时间: {subprocess.run(['date'], capture_output=True, text=True).stdout.strip()}")
print("="*70)

results = []

for test in test_cases:
    print(f"\n📋 测试: {test['name']}")
    print(f"   脚本: {test['script']}")
    print(f"   类型: {test['type']}")

    output, error = test_hook_output(test['script'], test['input'])

    if error:
        print(f"   ❌ 执行失败: {error}")
        results.append({
            "name": test['name'],
            "status": "FAIL",
            "error": error
        })
    else:
        score, issues = validate_output_format(output, test['type'])

        # 检查特殊字段
        if "expected_trigger" in test:
            if output.get("trigger") == test['expected_trigger']:
                print(f"   ✅ trigger字段正确: {test['expected_trigger']}")
            else:
                print(f"   ⚠️  trigger字段: {output.get('trigger')} (期望: {test['expected_trigger']})")

        print(f"   📊 标准符合度: {score}/3")

        if issues:
            print(f"   ⚠️  问题:")
            for issue in issues:
                print(f"      - {issue}")
        else:
            print(f"   ✅ 格式完全符合标准")

        print(f"   📄 输出示例: {json.dumps(output, ensure_ascii=False)[:150]}...")

        results.append({
            "name": test['name'],
            "status": "PASS" if score >= 2 else "WARN",
            "score": score,
            "issues": issues
        })

# 汇总报告
print("\n" + "="*70)
print("📊 测试汇总报告")
print("="*70)

passed = sum(1 for r in results if r["status"] == "PASS")
warned = sum(1 for r in results if r["status"] == "WARN")
failed = sum(1 for r in results if r["status"] == "FAIL")

print(f"\n总计: {len(results)} 个Hook")
print(f"✅ 通过: {passed}")
print(f"⚠️  警告: {warned}")
print(f"❌ 失败: {failed}")

if failed == 0 and warned == 0:
    print(f"\n🎉 所有Hook输出格式完全符合标准！")
elif failed == 0:
    print(f"\n✅ 基本通过，但有一些小问题需要注意")
else:
    print(f"\n⚠️  存在需要修复的问题")

# 详细结果
print(f"\n详细结果:")
for r in results:
    status_icon = "✅" if r["status"] == "PASS" else "⚠️" if r["status"] == "WARN" else "❌"
    print(f"  {status_icon} {r['name']}: {r['status']}")
    if "error" in r:
        print(f"      错误: {r['error']}")
    elif "issues" in r and r["issues"]:
        for issue in r["issues"]:
            print(f"      - {issue}")

print("\n" + "="*70)
print("测试完成")
print("="*70)

# 返回退出码
sys.exit(0 if failed == 0 else 1)
