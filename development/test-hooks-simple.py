#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import subprocess
import sys
import os

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def test_hook(script_path, test_input, description):
    """测试单个Hook"""
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"Script: {script_path}")
    print(f"{'='*60}")

    try:
        result = subprocess.run(
            ["python", script_path],
            input=json.dumps(test_input),
            capture_output=True,
            text=True,
            timeout=10,
            encoding='utf-8',
            errors='replace'
        )

        output = result.stdout.strip()
        print(f"Raw Output:\n{output[:200]}...")

        # 解析JSON
        try:
            parsed = json.loads(output)
            print(f"\n✅ JSON Valid: Yes")

            # 检查标准字段
            checks = []
            if "continue" in parsed:
                checks.append("✓ continue")
            if "suppressOutput" in parsed:
                checks.append("✓ suppressOutput")
            if "systemMessage" in parsed:
                checks.append("✓ systemMessage")
            if "trigger" in parsed:
                checks.append(f"✓ trigger={parsed['trigger']}")

            print(f"Fields: {', '.join(checks)}")

            return True, parsed
        except json.JSONDecodeError as e:
            print(f"\n❌ JSON Valid: No - {e}")
            return False, None

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False, None

print("="*60)
print("HOOK OUTPUT FORMAT VERIFICATION")
print("="*60)
print(f"Working Directory: {os.getcwd()}")

results = []

# Test 1: error-auto-recorder
success, output = test_hook(
    ".claude/hooks/post-tool-use/error-auto-recorder.py",
    {},
    "error-auto-recorder (empty input)"
)
results.append(("error-auto-recorder", success))

# Test 2: document_sync
success, output = test_hook(
    ".claude/hooks/document_sync.py",
    {
        "tool_name": "Edit",
        "tool_input": {"file_path": "docs/product/claude.md"},
        "tool_response": {}
    },
    "document_sync"
)
results.append(("document_sync", success))

# Test 3: session_start
success, output = test_hook(
    ".claude/hooks/session_start.py",
    {},
    "session_start"
)
results.append(("session_start", success))

# Summary
print(f"\n{'='*60}")
print("SUMMARY")
print(f"{'='*60}")

passed = sum(1 for _, s in results if s)
failed = len(results) - passed

for name, success in results:
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status}: {name}")

print(f"\nTotal: {len(results)} tests")
print(f"Passed: {passed}")
print(f"Failed: {failed}")

if failed == 0:
    print(f"\n🎉 All hooks output valid JSON format!")
else:
    print(f"\n⚠️  Some hooks need attention")

sys.exit(0 if failed == 0 else 1)
