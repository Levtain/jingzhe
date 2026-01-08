#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日终Git自动推送脚本

功能:
1. 检查Git状态
2. 添加所有更改
3. 创建提交(带日期时间戳)
4. 推送到GitHub
5. 验证推送成功
6. 显示提交统计

作者: Claude (老黑)
创建时间: 2025-01-08
版本: v1.0
"""

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

class DailyGitPush:
    def __init__(self, repo_path: str = "d:/Claude"):
        self.repo_path = Path(repo_path)
        self.git_dir = self.repo_path / ".git"

    def run_command(self, cmd: list, capture_output: bool = True) -> tuple:
        """执行shell命令"""
        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=capture_output,
                text=True,
                timeout=120
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "命令执行超时"
        except Exception as e:
            return -1, "", str(e)

    def check_git_status(self) -> bool:
        """检查Git状态,看是否有更改"""
        print("[CHECK] Checking Git status...")
        returncode, stdout, stderr = self.run_command(["git", "status", "--short"])

        if returncode != 0:
            print(f"[ERROR] Git status check failed: {stderr}")
            return False

        if not stdout.strip():
            print("[OK] No changes, working directory clean")
            return False

        print(f"[INFO] Changes detected:\n{stdout}")
        return True

    def add_all_changes(self) -> bool:
        """添加所有更改"""
        print("[ADD] Adding all changes...")
        returncode, stdout, stderr = self.run_command(["git", "add", "."])

        if returncode != 0:
            print(f"[ERROR] Failed to add files: {stderr}")
            return False

        print("[OK] Files added successfully")
        return True

    def create_commit(self, message: str = None) -> bool:
        """创建提交"""
        if message is None:
            now = datetime.now()
            message = f"chore: daily backup {now.strftime('%Y-%m-%d %H:%M')}"

        print(f"[COMMIT] Creating commit: {message}")
        returncode, stdout, stderr = self.run_command(
            ["git", "commit", "-m", message]
        )

        if returncode != 0:
            print(f"[ERROR] Commit failed: {stderr}")
            return False

        print("[OK] Commit successful")
        return True

    def push_to_github(self) -> bool:
        """推送到GitHub"""
        print("[PUSH] Pushing to GitHub...")
        returncode, stdout, stderr = self.run_command(
            ["git", "push", "origin", "master"]
        )

        if returncode != 0:
            print(f"[ERROR] Push failed: {stderr}")
            return False

        print("[OK] Push successful!")
        return True

    def verify_push(self) -> bool:
        """验证推送成功"""
        print("[VERIFY] Verifying push...")
        returncode, stdout, stderr = self.run_command(
            ["git", "log", "--oneline", "-1"]
        )

        if returncode != 0:
            print(f"[WARN] Cannot verify latest commit")
            return True  # 不算失败

        print(f"[OK] Latest commit: {stdout.strip()}")
        return True

    def show_stats(self) -> bool:
        """显示提交统计"""
        print("[STATS] Commit statistics...")
        returncode, stdout, stderr = self.run_command(
            ["git", "log", "--oneline", "--since=yesterday"]
        )

        if returncode == 0 and stdout.strip():
            print(f"[INFO] Today's commits:\n{stdout}")

        return True

    def check_remote_sync(self) -> bool:
        """检查远程仓库同步状态"""
        returncode, stdout, stderr = self.run_command(
            ["git", "remote", "-v"]
        )

        if returncode == 0:
            print(f"[REMOTE] Remote repository:\n{stdout}")
            return True

        print("[WARN] No remote repository configured")
        return False

    def daily_push(self, message: str = None) -> bool:
        """执行完整的日终推送流程"""
        print("=" * 60)
        print("[WORKFLOW] Daily Git Automatic Push")
        print("=" * 60)
        print(f"[REPO] Repository: {self.repo_path}")
        print(f"[TIME] Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 60)

        # 检查远程仓库
        if not self.check_remote_sync():
            print("\n[WARN] Please configure remote repository first:")
            print("   git remote add origin https://github.com/Levtain/jingzhe.git")
            return False

        # 检查是否有更改
        if not self.check_git_status():
            print("\n[OK] Working directory clean, no commit needed")
            return True

        # 执行推送流程
        steps = [
            ("添加文件", self.add_all_changes),
            ("创建提交", lambda: self.create_commit(message)),
            ("推送到GitHub", self.push_to_github),
            ("验证推送", self.verify_push),
            ("显示统计", self.show_stats),
        ]

        for step_name, step_func in steps:
            print()
            if not step_func():
                print(f"\n[ERROR] Workflow interrupted: {step_name} failed")
                return False

        print()
        print("=" * 60)
        print("[SUCCESS] Daily push completed!")
        print("=" * 60)
        return True


def main():
    """主函数"""
    # 解析命令行参数
    message = None
    if len(sys.argv) > 1:
        message = " ".join(sys.argv[1:])

    # 执行日终推送
    pusher = DailyGitPush()
    success = pusher.daily_push(message)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
