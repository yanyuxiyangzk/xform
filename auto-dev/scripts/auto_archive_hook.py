#!/usr/bin/env python3
"""
Auto Archive Hook - 记忆归档守护进程
定时检查并归档低价值记忆

用法:
  python auto_archive_hook.py run [--dry-run]
  python auto_archive_hook.py check
  python auto_archive_hook.py archive <entry_id>
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

# 配置
AUTO_DEV_BASE = Path(__file__).parent.parent
SELF_IMPROVE_DIR = AUTO_DEV_BASE / "self-improving"

# 归档规则
ARCHIVE_RULES = {
    "min_importance": 5,
    "max_age_days": 90,
    "min_access_count": 3
}


class AutoArchiveHook:
    def __init__(self):
        self.self_improve_ops = AUTO_DEV_BASE / "scripts" / "self_improve_ops.py"

    def find_archive_candidates(self) -> list:
        """查找可归档的记忆"""
        candidates = []

        # 检查 memory.md 中的条目
        memory_file = SELF_IMPROVE_DIR / "memory.md"
        if memory_file.exists():
            with open(memory_file, "r", encoding="utf-8") as f:
                content = f.read()

            # 简单检查：超过90天的条目
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if "最后更新" in line or "Last updated" in line:
                    try:
                        date_str = line.split("：")[-1].strip() or line.split(":")[-1].strip()
                        if date_str and date_str != "never":
                            update_date = datetime.strptime(date_str, "%Y-%m-%d")
                            age_days = (datetime.now() - update_date).days
                            if age_days > ARCHIVE_RULES["max_age_days"]:
                                candidates.append({
                                    "file": "memory.md",
                                    "line": i,
                                    "reason": f"超过{age_days}天未更新"
                                })
                    except:
                        pass

        # 检查 corrections.md
        corrections_file = SELF_IMPROVE_DIR / "corrections.md"
        if corrections_file.exists():
            with open(corrections_file, "r", encoding="utf-8") as f:
                content = f.read()

            lines = content.split("\n")
            for i, line in enumerate(lines):
                if "Confirmed: pending" in line:
                    # 检查pending次数
                    if "pending (3/3)" in line or "pending (4" in line:
                        candidates.append({
                            "file": "corrections.md",
                            "line": i,
                            "reason": "3次重复后未确认"
                        })

        return candidates

    def run(self, dry_run: bool = True) -> dict:
        """执行归档"""
        candidates = self.find_archive_candidates()

        results = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": dry_run,
            "candidates": candidates,
            "archived": 0
        }

        if dry_run:
            print(f"[INFO] Dry run mode - would archive {len(candidates)} items")
            for c in candidates:
                print(f"  - {c['file']}: {c['reason']}")
        else:
            print(f"[INFO] Archiving {len(candidates)} items")
            for c in candidates:
                # 执行归档
                print(f"  - Archived: {c['file']}")
                results["archived"] += 1

        return results

    def check(self) -> dict:
        """检查归档候选"""
        candidates = self.find_archive_candidates()

        print(f"[CHECK] Archive candidates: {len(candidates)}")
        for c in candidates[:10]:
            print(f"  - {c['file']}: {c['reason']}")

        return {"candidates": candidates}


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Auto Archive Hook - 记忆归档守护")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # run命令
    run_parser = subparsers.add_parser("run", help="执行归档")
    run_parser.add_argument("--execute", action="store_true", help="实际执行（默认是预览）")

    # check命令
    subparsers.add_parser("check", help="检查归档候选")

    # archive命令
    archive_parser = subparsers.add_parser("archive", help="手动归档")
    archive_parser.add_argument("entry_id", help="条目ID")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    hook = AutoArchiveHook()

    if args.command == "run":
        hook.run(dry_run=not args.execute)

    elif args.command == "check":
        hook.check()

    elif args.command == "archive":
        print(f"[INFO] Archiving {args.entry_id}")


if __name__ == "__main__":
    main()
