#!/usr/bin/env python3
"""
Memory Tier Manager - 三层记忆管理系统
HOT (热) -> WARM (温) -> COLD (冷)

根据访问频率和重要性自动管理记忆层级

用法:
  python memory_tier_manager.py status
  python memory_tier_manager.py promote <memory_id>
  python memory_tier_manager.py demote <memory_id>
  python memory_tier_manager.py cleanup
  python memory_tier_manager.py compact
"""

import os
import sys
import re
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Tuple


class MemoryTierManager:
    """三层记忆管理器"""

    # 层级配置
    HOT_DIR = Path(__file__).parent / "hot"
    WARM_DIR = Path(__file__).parent / "warm"
    COLD_DIR = Path(__file__).parent / "cold"

    # 原有目录（将被整合）
    OLD_MEMORY = Path(__file__).parent.parent / "memory"

    # 层级限制
    HOT_MAX_LINES = 100
    WARM_MAX_LINES = 200

    def __init__(self):
        self.ensure_dirs()
        self.migrate_old_memories()

    def ensure_dirs(self):
        """确保目录存在"""
        self.HOT_DIR.mkdir(parents=True, exist_ok=True)
        self.WARM_DIR.mkdir(parents=True, exist_ok=True)
        self.COLD_DIR.mkdir(parents=True, exist_ok=True)

    def migrate_old_memories(self):
        """迁移旧记忆到新层级"""
        if not self.OLD_MEMORY.exists():
            return

        # 统计迁移数量
        migrated = 0

        # episodic/daily-logs -> cold
        daily_logs = self.OLD_MEMORY / "episodic" / "daily-logs"
        if daily_logs.exists():
            for f in daily_logs.glob("*.md"):
                # 超过30天的归档到 cold
                date_str = f.stem
                try:
                    file_date = datetime.strptime(date_str, "%Y-%m-%d")
                    if datetime.now() - file_date > timedelta(days=30):
                        dest = self.COLD_DIR / "archive" / "daily-logs"
                        dest.mkdir(exist_ok=True)
                        shutil.move(str(f), str(dest / f.name))
                        migrated += 1
                except:
                    pass

        # longterm/projects -> warm
        projects = self.OLD_MEMORY / "longterm" / "projects"
        if projects.exists():
            warm_projects = self.WARM_DIR / "projects"
            warm_projects.mkdir(exist_ok=True)
            for f in projects.glob("*.md"):
                if not (warm_projects / f.name).exists():
                    shutil.copy(str(f), str(warm_projects / f.name))
                    migrated += 1

        if migrated > 0:
            print(f"[MIGRATE] Migrated {migrated} memories to new tier structure")

    def get_memory_tier(self, memory_id: str) -> Optional[str]:
        """获取记忆所属层级"""
        for tier, dir_path in [("hot", self.HOT_DIR), ("warm", self.WARM_DIR), ("cold", self.COLD_DIR)]:
            if list(dir_path.rglob(f"{memory_id}*.md")):
                return tier
        return None

    def promote(self, memory_id: str) -> bool:
        """提升记忆层级 (cold -> warm -> hot)"""
        current_tier = self.get_memory_tier(memory_id)
        if not current_tier:
            print(f"[ERROR] Memory not found: {memory_id}")
            return False

        # 查找源文件
        source_file = None
        for ext in ["", ".md"]:
            for tier_dir in [self.COLD_DIR, self.WARM_DIR, self.HOT_DIR]:
                matches = list(tier_dir.rglob(f"{memory_id}{ext}*"))
                if matches:
                    source_file = matches[0]
                    break
            if source_file:
                break

        if not source_file:
            print(f"[ERROR] Memory file not found: {memory_id}")
            return False

        # 目标层级
        if current_tier == "cold":
            target_dir = self.WARM_DIR
        elif current_tier == "warm":
            target_dir = self.HOT_DIR
        else:
            print(f"[INFO] Memory already in hottest tier: {current_tier}")
            return True

        # 检查目标层级容量
        if target_dir == self.HOT_DIR:
            total_lines = sum(1 for f in target_dir.rglob("*.md") for _ in open(f, encoding="utf-8"))
            source_lines = sum(1 for _ in open(source_file, encoding="utf-8"))
            if total_lines + source_lines > self.HOT_MAX_LINES:
                print(f"[WARN] Hot tier would exceed {self.HOT_MAX_LINES} lines, compacting first")
                self.compact_hot()
                return self.promote(memory_id)  # 重试

        # 移动文件
        dest = target_dir / source_file.name
        shutil.move(str(source_file), str(dest))
        print(f"[PROMOTE] {memory_id}: {current_tier} -> {target_dir.name}")
        return True

    def demote(self, memory_id: str) -> bool:
        """降低记忆层级 (hot -> warm -> cold)"""
        current_tier = self.get_memory_tier(memory_id)
        if not current_tier:
            print(f"[ERROR] Memory not found: {memory_id}")
            return False

        # 查找源文件
        source_file = None
        for tier_dir in [self.HOT_DIR, self.WARM_DIR, self.COLD_DIR]:
            matches = list(tier_dir.rglob(f"{memory_id}*"))
            if matches:
                source_file = matches[0]
                break

        if not source_file:
            print(f"[ERROR] Memory file not found: {memory_id}")
            return False

        # 目标层级
        if current_tier == "hot":
            target_dir = self.WARM_DIR
        elif current_tier == "warm":
            target_dir = self.COLD_DIR
        else:
            print(f"[INFO] Memory already in coldest tier: {current_tier}")
            return True

        # 移动文件
        dest = target_dir / source_file.name
        shutil.move(str(source_file), str(dest))
        print(f"[DEMOTE] {memory_id}: {current_tier} -> {target_dir.name}")
        return True

    def compact_hot(self):
        """整理热层级，确保不超过行数限制"""
        hot_files = list(self.HOT_DIR.glob("*.md"))
        total_lines = sum(1 for f in hot_files for _ in open(f, encoding="utf-8"))

        if total_lines <= self.HOT_MAX_LINES:
            return

        # 按访问频率和重要性排序
        files_with_priority = []
        for f in hot_files:
            content = open(f, encoding="utf-8").read()
            importance = 5
            access_count = 0

            # 提取重要性
            if "Importance:" in content:
                match = re.search(r"Importance:\s*(\d+)", content)
                if match:
                    importance = int(match.group(1))

            # 提取访问次数
            if "Access Count:" in content:
                match = re.search(r"Access Count:\s*(\d+)", content)
                if match:
                    access_count = int(match.group(1))

            priority = importance * 10 + access_count
            files_with_priority.append((f, priority, content))

        # 按优先级排序，保留高优先级
        files_with_priority.sort(key=lambda x: x[1], reverse=True)

        kept_files = []
        kept_lines = 0
        for f, priority, content in files_with_priority:
            file_lines = sum(1 for _ in content.split("\n"))
            if kept_lines + file_lines <= self.HOT_MAX_LINES:
                kept_files.append((f, content))
                kept_lines += file_lines
            else:
                # 移动到 warm 层
                warm_dest = self.WARM_DIR / f.name
                with open(f, "w", encoding="utf-8") as out:
                    out.write(content)
                if f.exists():
                    shutil.move(str(f), str(warm_dest))
                print(f"[COMPACT] Moved {f.name} to warm tier")

    def cleanup(self, days: int = 90):
        """清理冷层级中过期的记忆"""
        cold_files = list(self.COLD_DIR.rglob("*.md"))
        cleaned = 0
        cutoff = datetime.now() - timedelta(days=days)

        for f in cold_files:
            try:
                content = open(f, encoding="utf-8").read()
                # 提取创建时间
                if "Created:" in content:
                    match = re.search(r"Created:\s*(\d{4}-\d{2}-\d{2})", content)
                    if match:
                        created = datetime.strptime(match.group(1), "%Y-%m-%d")
                        if created < cutoff:
                            # 删除或标记
                            archive_dir = self.COLD_DIR / "archive"
                            archive_dir.mkdir(exist_ok=True)
                            shutil.move(str(f), str(archive_dir / f.name))
                            cleaned += 1
            except Exception:
                pass

        print(f"[CLEANUP] Cleaned {cleaned} cold memories older than {days} days")
        return cleaned

    def status(self) -> Dict:
        """获取层级状态"""
        def count_files_and_lines(directory):
            files = list(directory.rglob("*.md"))
            lines = sum(1 for f in files for _ in open(f, encoding="utf-8", errors="ignore"))
            return len(files), lines

        hot_files, hot_lines = count_files_and_lines(self.HOT_DIR)
        warm_files, warm_lines = count_files_and_lines(self.WARM_DIR)
        cold_files, cold_lines = count_files_and_lines(self.COLD_DIR)

        return {
            "hot": {"files": hot_files, "lines": hot_lines, "max_lines": self.HOT_MAX_LINES},
            "warm": {"files": warm_files, "lines": warm_lines, "max_lines": self.WARM_MAX_LINES},
            "cold": {"files": cold_files, "lines": cold_lines}
        }

    def print_status(self):
        """打印层级状态"""
        status = self.status()

        print("\n[Memory Tier Status]")
        print("=" * 60)
        print(f"HOT:  {status['hot']['files']} files, {status['hot']['lines']}/{status['hot']['max_lines']} lines")
        print(f"WARM: {status['warm']['files']} files, {status['warm']['lines']}/{status['warm']['max_lines']} lines")
        print(f"COLD: {status['cold']['files']} files, {status['cold']['lines']} lines")
        print("=" * 60)

        # 警告
        if status['hot']['lines'] > status['hot']['max_lines']:
            print("[WARN] Hot tier exceeds line limit, run 'compact' to optimize")
        if status['warm']['lines'] > status['warm']['max_lines']:
            print("[WARN] Warm tier exceeds line limit")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Memory Tier Manager - 三层记忆管理")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    subparsers.add_parser("status", help="查看层级状态")
    subparsers.add_parser("compact", help="整理热层级")

    promote_parser = subparsers.add_parser("promote", help="提升记忆层级")
    promote_parser.add_argument("memory_id", help="记忆ID")

    demote_parser = subparsers.add_parser("demote", help="降低记忆层级")
    demote_parser.add_argument("memory_id", help="记忆ID")

    cleanup_parser = subparsers.add_parser("cleanup", help="清理过期记忆")
    cleanup_parser.add_argument("--days", type=int, default=90, help="保留天数")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    manager = MemoryTierManager()

    if args.command == "status":
        manager.print_status()

    elif args.command == "compact":
        manager.compact_hot()
        print("[OK] Hot tier compacted")

    elif args.command == "promote":
        manager.promote(args.memory_id)

    elif args.command == "demote":
        manager.demote(args.memory_id)

    elif args.command == "cleanup":
        manager.cleanup(args.days)


if __name__ == "__main__":
    main()
