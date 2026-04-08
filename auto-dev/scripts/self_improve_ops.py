#!/usr/bin/env python3
"""
Self-Improving Operations - 自我改进记忆系统
支持学习、反思、修正、永久改进

用法:
  python self_improve_ops.py learn "<correction>" --type TYPE --context CONTEXT
  python self_improve_ops.py reflect "<context>" "<reflection>" "<lesson>"
  python self_improve_ops.py stats
  python self_improve_ops.py search <query>
  python self_improve_ops.py promote <entry_id>
  python self_improve_ops.py archive <entry_id>
  python self_improve_ops.py heartbeat
  python self_improve_ops.py show [--tier HOT|WARM|COLD]

自我改进层级:
  HOT (memory.md) - ≤100行，始终加载
  WARM (projects/, domains/) - ≤200行，按需加载
  COLD (archive/) - 归档，长期保留
"""

import os
import sys
import re
import shutil
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

# 配置
AUTO_DEV_BASE = Path(__file__).parent.parent
SELF_IMPROVE_DIR = AUTO_DEV_BASE / "self-improving"

# 层级目录
TIERS = {
    "HOT": SELF_IMPROVE_DIR / "memory.md",
    "WARM": SELF_IMPROVE_DIR,
    "COLD": SELF_IMPROVE_DIR / "archive"
}

# 模式类型
PATTERN_TYPES = ["format", "technical", "communication", "project", "workflow"]


class SelfImproveOps:
    def __init__(self):
        self.base_dir = SELF_IMPROVE_DIR
        self.memory_file = self.base_dir / "memory.md"
        self.corrections_file = self.base_dir / "corrections.md"
        self.index_file = self.base_dir / "index.md"
        self.heartbeat_file = self.base_dir / "heartbeat-state.md"
        self.ensure_dirs()

    def ensure_dirs(self):
        """确保目录存在"""
        self.base_dir.mkdir(exist_ok=True)
        (self.base_dir / "projects").mkdir(exist_ok=True)
        (self.base_dir / "domains").mkdir(exist_ok=True)
        (self.base_dir / "archive").mkdir(exist_ok=True)

    def generate_id(self, prefix: str = "SELF") -> str:
        """生成条目ID"""
        now = datetime.now()
        date_str = now.strftime("%Y%m%d")
        time_str = now.strftime("%H%M")
        return f"{prefix}-{date_str}-{time_str}"

    def learn(self, correction: str, pattern_type: str = "technical", context: str = "", project: str = None) -> str:
        """记录学习（修正）"""
        entry_id = self.generate_id("CORR")

        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        # 解析修正内容
        if "→" in correction:
            parts = correction.split("→")
            wrong = parts[0].strip()
            right = parts[1].strip() if len(parts) > 1 else ""
            lesson = f"不要{wrong}，应该{right}"
        else:
            lesson = correction

        # 确定存储文件
        if project:
            target_file = self.base_dir / "projects" / f"{project}.md"
        elif pattern_type in ["technical", "workflow"]:
            target_file = self.base_dir / "domains" / "code.md"
        elif pattern_type == "communication":
            target_file = self.base_dir / "domains" / "comms.md"
        else:
            target_file = self.memory_file

        # 创建或追加内容
        entry_content = f"""
## {entry_id} — {now}

**修正:** {correction}
**类型:** {pattern_type}
**上下文:** {context or "全局"}
**状态:** pending (1/3)
"""
        if target_file.exists():
            with open(target_file, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            content = f"# {'项目' if project else '域名'}记忆\n\n"

        content += entry_content

        with open(target_file, "w", encoding="utf-8") as f:
            f.write(content)

        # 同时记录到corrections.md
        self._append_correction(entry_id, now, correction, pattern_type, context)

        # 更新索引
        self._refresh_index()

        print(f"[OK] 学习记录已保存: {entry_id}")
        print(f"   修正: {correction}")
        print(f"   类型: {pattern_type}")
        print(f"   状态: pending (1/3)")
        if project:
            print(f"   项目: {project}")

        return entry_id

    def _append_correction(self, entry_id: str, timestamp: str, correction: str, ptype: str, context: str):
        """追加到corrections.md"""
        if self.corrections_file.exists():
            with open(self.corrections_file, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            content = "# Corrections Log\n\n"

        entry = f"""
## {timestamp.split()[0]}

- [{timestamp.split()[1]}] {entry_id}: {correction}
  Type: {ptype}
  Context: {context or "全局"}
  Confirmed: pending (1/3)
"""
        content += entry

        with open(self.corrections_file, "w", encoding="utf-8") as f:
            f.write(content)

    def reflect(self, context: str, reflection: str, lesson: str) -> str:
        """自我反思"""
        entry_id = self.generate_id("REFL")

        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        # 追加到memory.md
        if self.memory_file.exists():
            with open(self.memory_file, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            content = "# Self-Improving Memory (HOT Tier)\n\n"

        entry = f"""
## {entry_id} — {now}

**Context:** {context}
**Reflection:** {reflection}
**Lesson:** {lesson}
**Status:** candidate
"""
        content += entry

        with open(self.memory_file, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"[OK] 自我反思已保存: {entry_id}")
        print(f"   Context: {context}")
        print(f"   Reflection: {reflection}")
        print(f"   Lesson: {lesson}")

        return entry_id

    def stats(self) -> Dict:
        """获取统计信息"""
        stats = {
            "HOT": {"file": "memory.md", "lines": 0, "entries": 0},
            "WARM": {"projects": 0, "domains": 0, "lines": 0},
            "COLD": {"files": 0, "lines": 0}
        }

        # HOT
        if self.memory_file.exists():
            with open(self.memory_file, "r", encoding="utf-8") as f:
                content = f.read()
            lines = content.split("\n")
            stats["HOT"]["lines"] = len(lines)
            stats["HOT"]["entries"] = len([l for l in lines if l.startswith("## ")])

        # WARM
        projects_dir = self.base_dir / "projects"
        domains_dir = self.base_dir / "domains"

        if projects_dir.exists():
            for f in projects_dir.glob("*.md"):
                with open(f, "r", encoding="utf-8") as file:
                    stats["WARM"]["lines"] += len(file.read().split("\n"))
                stats["WARM"]["projects"] += 1

        if domains_dir.exists():
            for f in domains_dir.glob("*.md"):
                with open(f, "r", encoding="utf-8") as file:
                    stats["WARM"]["lines"] += len(file.read().split("\n"))
                stats["WARM"]["domains"] += 1

        # COLD
        archive_dir = self.base_dir / "archive"
        if archive_dir.exists():
            for f in archive_dir.glob("*.md"):
                with open(f, "r", encoding="utf-8") as file:
                    stats["COLD"]["lines"] += len(file.read().split("\n"))
                stats["COLD"]["files"] += 1

        return stats

    def search(self, query: str) -> List[Dict]:
        """搜索记忆"""
        results = []
        query_lower = query.lower()

        # 搜索所有层级
        search_files = [self.memory_file]
        search_files.extend(self.base_dir.glob("projects/*.md"))
        search_files.extend(self.base_dir.glob("domains/*.md"))
        search_files.extend(self.base_dir.glob("archive/*.md"))

        for file in search_files:
            if not file.exists():
                continue

            with open(file, "r", encoding="utf-8") as f:
                content = f.read()

            if query_lower in content.lower():
                tier = "HOT" if file == self.memory_file else "WARM" if "projects" in str(file) else "COLD"
                lines = content.split("\n")

                # 提取匹配行
                matches = [l.strip() for l in lines if query_lower in l.lower()][:3]

                results.append({
                    "file": file.name,
                    "tier": tier,
                    "matches": matches
                })

        return results

    def promote(self, entry_id: str, target_tier: str = "HOT") -> bool:
        """提升条目到更高层级"""
        # 简化实现：在目标层级追加标记
        now = datetime.now().strftime("%Y-%m-%d")

        note = f"\n<!-- Promoted: {entry_id} on {now} -->\n"

        if target_tier == "HOT":
            target = self.memory_file
        elif target_tier == "WARM":
            print("[WARN] 请指定目标: projects/xxx.md 或 domains/xxx.md")
            return False
        else:
            print("[ERROR] 不能提升到COLD")
            return False

        with open(target, "a", encoding="utf-8") as f:
            f.write(note)

        print(f"[OK] 已提升 {entry_id} 到 {target_tier}")
        return True

    def archive_entry(self, entry_id: str) -> bool:
        """归档条目"""
        archive_dir = self.base_dir / "archive"
        archive_dir.mkdir(exist_ok=True)

        # 简化：从memory.md移到archive
        if self.memory_file.exists():
            with open(self.memory_file, "r", encoding="utf-8") as f:
                content = f.read()

            # 查找并移除条目
            lines = content.split("\n")
            new_lines = []
            skip_entry = False

            for line in lines:
                if entry_id in line:
                    skip_entry = True
                elif skip_entry and line.startswith("## "):
                    skip_entry = False

                if not skip_entry:
                    new_lines.append(line)

            with open(self.memory_file, "w", encoding="utf-8") as f:
                f.write("\n".join(new_lines))

        # 写入archive
        archive_file = archive_dir / f"{entry_id}.md"
        with open(archive_file, "w", encoding="utf-8") as f:
            f.write(f"# {entry_id}\n\nArchived on {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

        self._refresh_index()

        print(f"[OK] 已归档 {entry_id}")
        return True

    def heartbeat(self) -> str:
        """心跳检查"""
        now = datetime.now().isoformat()

        # 更新心跳状态
        if self.heartbeat_file.exists():
            with open(self.heartbeat_file, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            content = ""

        # 检查是否有变更
        has_changes = False
        for file in [self.memory_file, self.corrections_file]:
            if file.exists():
                # 简化：检查文件修改时间
                mtime = datetime.fromtimestamp(file.stat().st_mtime).isoformat()
                if mtime > now:
                    has_changes = True
                    break

        # 更新状态
        lines = content.split("\n") if content else []
        new_lines = []
        for line in lines:
            if line.startswith("last_heartbeat_started_at:"):
                new_lines.append(f"last_heartbeat_started_at: {now}")
            elif line.startswith("last_heartbeat_result:"):
                new_lines.append(f"last_heartbeat_result: {'CHANGES_DETECTED' if has_changes else 'HEARTBEAT_OK'}")
            else:
                new_lines.append(line)

        if not new_lines:
            new_lines = [
                "# Self-Improving Heartbeat State",
                f"last_heartbeat_started_at: {now}",
                f"last_reviewed_change_at: {now}",
                f"last_heartbeat_result: {'CHANGES_DETECTED' if has_changes else 'HEARTBEAT_OK'}",
                "## Last actions",
                "- none yet"
            ]

        with open(self.heartbeat_file, "w", encoding="utf-8") as f:
            f.write("\n".join(new_lines))

        if has_changes:
            return "CHANGES_DETECTED"
        else:
            return "HEARTBEAT_OK"

    def _refresh_index(self):
        """刷新索引"""
        lines = [
            "# Memory Index",
            "",
            "## HOT (always loaded)"
        ]

        if self.memory_file.exists():
            with open(self.memory_file, "r", encoding="utf-8") as f:
                content = f.read()
            line_count = len(content.split("\n"))
            entries = len([l for l in content.split("\n") if l.startswith("## ")])
            lines.append(f"- memory.md: {line_count} lines, {entries} entries")
        else:
            lines.append("- memory.md: 0 lines")

        lines.extend(["", "## WARM (load on demand)"])

        projects_dir = self.base_dir / "projects"
        if projects_dir.exists():
            files = list(projects_dir.glob("*.md"))
            if files:
                for f in files:
                    lines.append(f"- projects/{f.name}")
            else:
                lines.append("- projects/: 0 files")

        domains_dir = self.base_dir / "domains"
        if domains_dir.exists():
            files = list(domains_dir.glob("*.md"))
            if files:
                for f in files:
                    lines.append(f"- domains/{f.name}")
            else:
                lines.append("- domains/: 0 files")

        lines.extend(["", "## COLD (archived)"])

        archive_dir = self.base_dir / "archive"
        if archive_dir.exists():
            files = list(archive_dir.glob("*.md"))
            lines.append(f"- archive/: {len(files)} files")

        lines.append("")
        lines.append(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

        with open(self.index_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def show(self, tier: str = None):
        """显示记忆"""
        if tier == "HOT" or tier is None:
            print("\n[HOT] HOT (memory.md)")
            print("=" * 50)
            if self.memory_file.exists():
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    print(f.read())
            else:
                print("(empty)")

        if tier == "WARM" or tier is None:
            print("\n[WARM] WARM (projects/ + domains/)")
            print("=" * 50)

            for subdir in ["projects", "domains"]:
                dir_path = self.base_dir / subdir
                if dir_path.exists():
                    files = list(dir_path.glob("*.md"))
                    if files:
                        for f in files:
                            print(f"\n### {subdir}/{f.name}")
                            with open(f, "r", encoding="utf-8") as file:
                                print(file.read()[:500])
                    else:
                        print(f"{subdir}/: (empty)")

        if tier == "COLD" or tier is None:
            print("\n[COLD] COLD (archive/)")
            print("=" * 50)
            archive_dir = self.base_dir / "archive"
            if archive_dir.exists():
                files = list(archive_dir.glob("*.md"))
                if files:
                    for f in files[:10]:
                        print(f"- {f.name}")
                else:
                    print("(empty)")


def main():
    parser = argparse.ArgumentParser(description="Self-Improving Operations - 自我改进系统")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # learn命令
    learn_parser = subparsers.add_parser("learn", help="记录学习")
    learn_parser.add_argument("correction", help="修正内容")
    learn_parser.add_argument("--type", "-t", default="technical", choices=PATTERN_TYPES, help="类型")
    learn_parser.add_argument("--context", "-c", default="", help="上下文")
    learn_parser.add_argument("--project", "-p", help="项目名")

    # reflect命令
    reflect_parser = subparsers.add_parser("reflect", help="自我反思")
    reflect_parser.add_argument("context", help="上下文/任务类型")
    reflect_parser.add_argument("reflection", help="反思内容")
    reflect_parser.add_argument("lesson", help="教训/改进点")

    # stats命令
    subparsers.add_parser("stats", help="统计")

    # search命令
    search_parser = subparsers.add_parser("search", help="搜索")
    search_parser.add_argument("query", help="搜索关键词")

    # promote命令
    promote_parser = subparsers.add_parser("promote", help="提升层级")
    promote_parser.add_argument("entry_id", help="条目ID")
    promote_parser.add_argument("--tier", "-t", default="HOT", choices=["HOT", "WARM"], help="目标层级")

    # archive命令
    archive_parser = subparsers.add_parser("archive", help="归档")
    archive_parser.add_argument("entry_id", help="条目ID")

    # heartbeat命令
    subparsers.add_parser("heartbeat", help="心跳检查")

    # show命令
    show_parser = subparsers.add_parser("show", help="显示记忆")
    show_parser.add_argument("--tier", "-t", choices=["HOT", "WARM", "COLD"], help="层级")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    ops = SelfImproveOps()

    if args.command == "learn":
        ops.learn(args.correction, args.type, args.context, args.project)

    elif args.command == "reflect":
        ops.reflect(args.context, args.reflection, args.lesson)

    elif args.command == "stats":
        stats = ops.stats()
        print("\n[SELF-IMPROVING MEMORY STATS]")
        print("=" * 50)
        print(f"\n[HOT] memory.md (always loaded):")
        print(f"   lines: {stats['HOT']['lines']}, entries: {stats['HOT']['entries']}")
        print(f"\n[WARM] projects/ + domains/ (load on demand):")
        print(f"   projects/: {stats['WARM']['projects']} files")
        print(f"   domains/: {stats['WARM']['domains']} files")
        print(f"   Total lines: {stats['WARM']['lines']}")
        print(f"\n[COLD] archive/ (archived):")
        print(f"   files: {stats['COLD']['files']}")

    elif args.command == "search":
        results = ops.search(args.query)
        if results:
            print(f"\n[SEARCH] 搜索结果: \"{args.query}\"")
            print("=" * 50)
            for r in results:
                print(f"\n📁 {r['file']} [{r['tier']}]")
                for match in r['matches']:
                    print(f"   - {match[:80]}")
        else:
            print(f"未找到匹配 \"{args.query}\" 的记忆")

    elif args.command == "promote":
        ops.promote(args.entry_id, args.tier)

    elif args.command == "archive":
        ops.archive_entry(args.entry_id)

    elif args.command == "heartbeat":
        result = ops.heartbeat()
        print(f"[HEARTBEAT] Status: {result}")

    elif args.command == "show":
        ops.show(args.tier)


if __name__ == "__main__":
    main()
