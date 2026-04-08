#!/usr/bin/env python3
"""
Guardian Agent - 规则守护Agent
确保所有开发遵循RULES.md，防止Orchestrator绕过规则

用法:
  python scripts/guardian_agent.py check <dir>        # 检查目录
  python scripts/guardian_agent.py pre-write <dir>   # 写代码前检查
  python scripts/guardian_agent.py status            # 查看守护状态
  python scripts/guardian_agent.py block <reason>    # 手动封锁
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple

# 配置
AUTO_DEV_BASE = Path(__file__).parent.parent
RULES_FILE = AUTO_DEV_BASE / "RULES.md"
MEMORY_FILE = AUTO_DEV_BASE / "self-improving" / "memory.md"


class GuardianAgent:
    def __init__(self):
        self.blocked = False
        self.block_reason = None
        self.blocked_at = None
        self.violations_log = []

    def check_rule_guard(self, project_dir: Path, stage: str = "development") -> Tuple[bool, str, dict]:
        """执行rule_guard检查"""
        rule_guard_path = AUTO_DEV_BASE / "scripts" / "rule_guard.py"

        if not rule_guard_path.exists():
            return True, "rule_guard.py not found, skipping", {}

        cmd = [sys.executable, str(rule_guard_path), "gate", stage, str(project_dir)]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )

            output = result.stdout + result.stderr

            # 解析输出
            violations = {}

            if "P0:" in output:
                p0_match = output.split("P0:")[1].split("\n")[0].strip()
                violations['P0'] = int(p0_match) if p0_match.isdigit() else 0

            if result.returncode == 0:
                return True, "Gate passed", violations
            else:
                return False, f"Gate failed: {output[-500:]}", violations

        except subprocess.TimeoutExpired:
            return False, "Gate check timeout", {}
        except Exception as e:
            return False, f"Gate error: {str(e)}", {}

    def pre_write_check(self, project_dir: Path) -> Tuple[bool, str]:
        """
        写代码前的强制检查
        必须返回 (can_write, message)
        """
        print(f"\n[GUARDIAN] Pre-write check for {project_dir}")
        print("=" * 60)

        # 1. 检查Orchestrator是否在尝试直接写代码
        orchestrator_path = AUTO_DEV_BASE / "skills" / "orchestrator-skill.md"
        if orchestrator_path.exists():
            with open(orchestrator_path, 'r', encoding='utf-8') as f:
                skill_content = f.read()
                if "【严禁】直接写代码" not in skill_content:
                    self._log_violation("ORCHESTRATOR", "orchestrator-skill.md缺少禁令条款")

        # 2. 执行gate检查
        ok, msg, violations = self.check_rule_guard(project_dir, "development")

        print(f"[{'PASS' if ok else 'BLOCK'}] {msg}")

        if violations.get('P0', 0) > 0:
            self.blocked = True
            self.block_reason = f"P0 violations found: {violations['P0']}"
            self.blocked_at = datetime.now().isoformat()
            self._log_violation("P0", f"开发前检查P0违规: {violations['P0']}")
            return False, self.block_reason

        if not ok:
            # 非P0违规，允许开发但记录
            self._log_violation("NON_P0", msg)

        return True, "Pre-write check passed"

    def pre_commit_check(self, project_dir: Path) -> Tuple[bool, str]:
        """
        提交前的强制检查（更严格）
        """
        print(f"\n[GUARDIAN] Pre-commit check for {project_dir}")
        print("=" * 60)

        rule_guard_path = AUTO_DEV_BASE / "scripts" / "rule_guard.py"

        if not rule_guard_path.exists():
            return True, "rule_guard.py not found"

        cmd = [sys.executable, str(rule_guard_path), "pre-commit", str(project_dir)]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600
            )

            output = result.stdout + result.stderr
            print(output)

            if result.returncode == 0:
                print("\n[GUARDIAN] Pre-commit check PASSED")
                return True, "Pre-commit check passed"
            else:
                print("\n[GUARDIAN] Pre-commit check FAILED - blocking commit")
                self._log_violation("PRE_COMMIT", "提交前检查失败")
                return False, "Pre-commit check failed"

        except Exception as e:
            return False, f"Pre-commit check error: {str(e)}"

    def check_team_structure(self) -> Tuple[bool, str]:
        """
        检查团队结构是否正确创建
        """
        print(f"\n[GUARDIAN] Checking team structure...")

        # 检查是否有team config
        teams_dir = Path.home() / ".claude" / "teams"

        if not teams_dir.exists():
            return False, "Teams directory not found - TeamCreate may not have been used"

        # 支持子目录中的config.json
        team_configs = list(teams_dir.glob("*/config.json"))

        if not team_configs:
            return False, "No team configs found - TeamCreate was not used"

        # 检查是否是多角色团队
        for config_path in team_configs:
            try:
                import json
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    members = config.get('members', [])
                    if len(members) < 3:
                        return False, f"Team {config_path.parent.stem} has only {len(members)} members - should be multi-role"
            except:
                pass

        return True, "Team structure OK"

    def _log_violation(self, violation_type: str, message: str):
        """记录违规到内存"""
        self.violations_log.append({
            'type': violation_type,
            'message': message,
            'time': datetime.now().isoformat()
        })

        # 同时追加到memory.md
        memory_dir = MEMORY_FILE.parent
        if memory_dir.exists() and MEMORY_FILE.exists():
            entry = f"\n## GUARDIAN-{datetime.now().strftime('%Y%m%d-%H%M%S')} — {datetime.now()}\n\n"
            entry += f"**违规类型:** {violation_type}\n"
            entry += f"**消息:** {message}\n"
            entry += f"**状态:** BLOCKED\n\n"

            with open(MEMORY_FILE, 'a', encoding='utf-8') as f:
                f.write(entry)

    def block(self, reason: str) -> bool:
        """手动封锁"""
        self.blocked = True
        self.block_reason = reason
        self.blocked_at = datetime.now().isoformat()
        print(f"\n[GUARDIAN] *** SYSTEM BLOCKED ***")
        print(f"[GUARDIAN] Reason: {reason}")
        print(f"[GUARDIAN] Blocked at: {self.blocked_at}")
        return True

    def status(self) -> dict:
        """查看守护状态"""
        return {
            'blocked': self.blocked,
            'reason': self.block_reason,
            'blocked_at': self.blocked_at,
            'violations_log': self.violations_log[-10:]  # 最近10条
        }


def main():
    parser = argparse.ArgumentParser(description="Guardian Agent - 规则守护者")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # check命令
    check_parser = subparsers.add_parser("check", help="检查目录")
    check_parser.add_argument("dir", nargs="?", default=".", help="项目目录")
    check_parser.add_argument("--stage", default="development", help="阶段")

    # pre-write命令
    prewrite_parser = subparsers.add_parser("pre-write", help="写代码前检查")
    prewrite_parser.add_argument("dir", nargs="?", default=".", help="项目目录")

    # pre-commit命令
    commit_parser = subparsers.add_parser("pre-commit", help="提交前检查")
    commit_parser.add_argument("dir", nargs="?", default=".", help="项目目录")

    # status命令
    subparsers.add_parser("status", help="查看守护状态")

    # block命令
    block_parser = subparsers.add_parser("block", help="手动封锁")
    block_parser.add_argument("reason", help="封锁原因")

    # team-check命令
    subparsers.add_parser("team-check", help="检查团队结构")

    args = parser.parse_args()

    guardian = GuardianAgent()

    if not args.command:
        parser.print_help()
        return

    if args.command == "check":
        path = Path(args.dir)
        ok, msg, violations = guardian.check_rule_guard(path, args.stage)
        print(f"\n[{'PASS' if ok else 'FAIL'}] {msg}")
        sys.exit(0 if ok else 1)

    elif args.command == "pre-write":
        path = Path(args.dir)
        ok, msg = guardian.pre_write_check(path)
        print(f"\n[{'WRITE ALLOWED' if ok else 'WRITE BLOCKED'}] {msg}")
        sys.exit(0 if ok else 1)

    elif args.command == "pre-commit":
        path = Path(args.dir)
        ok, msg = guardian.pre_commit_check(path)
        sys.exit(0 if ok else 1)

    elif args.command == "status":
        status = guardian.status()
        print("\n[GUARDIAN STATUS]")
        print(f"  Blocked: {status['blocked']}")
        if status['blocked']:
            print(f"  Reason: {status['reason']}")
            print(f"  Blocked at: {status['blocked_at']}")
        print(f"  Recent violations: {len(status['violations_log'])}")
        for v in status['violations_log']:
            print(f"    - [{v['type']}] {v['message']}")

    elif args.command == "block":
        guardian.block(args.reason)

    elif args.command == "team-check":
        ok, msg = guardian.check_team_structure()
        print(f"\n[{'PASS' if ok else 'FAIL'}] {msg}")
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
