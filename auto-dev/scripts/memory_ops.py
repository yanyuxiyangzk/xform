#!/usr/bin/env python3
"""
Memory Operations - 记忆读写脚本
支持存储、搜索、列表、统计

用法:
  python memory_ops.py store <category> <title> <content> [--tags TAG] [--importance N]
  python memory_ops.py search <query> [--limit N]
  python memory_ops.py list [--category CATEGORY] [--limit N]
  python memory_ops.py stats
  python memory_ops.py daily-log <type> <entry>

示例:
  python memory_ops.py store "longterm/projects" "Liquor编译功能" "实现了Java源码动态编译" --tags "liquor,compiler" --importance 8
  python memory_ops.py search "liquor" --limit 5
  python memory_ops.py daily-log "done" "完成Liquor热替换功能"
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
import re

# 配置
MEMORY_BASE = Path(__file__).parent.parent / "memory"
ENTITIES_DIR = MEMORY_BASE / "entities"

# 层级目录
LAYERS = {
    "episodic": MEMORY_BASE / "episodic",
    "working": MEMORY_BASE / "working",
    "longterm": MEMORY_BASE / "longterm"
}

# 重要性默认值
DEFAULT_IMPORTANCE = 5


class MemoryOps:
    def __init__(self):
        self.memory_base = MEMORY_BASE
        self.ensure_dirs()

    def ensure_dirs(self):
        """确保目录存在"""
        for layer_dir in LAYERS.values():
            layer_dir.mkdir(parents=True, exist_ok=True)

        # episodic子目录
        (LAYERS["episodic"] / "daily-logs").mkdir(exist_ok=True)
        (LAYERS["episodic"] / "inbox").mkdir(exist_ok=True)
        (LAYERS["episodic"] / "captures").mkdir(exist_ok=True)

        # working子目录
        (LAYERS["working"] / "sessions").mkdir(exist_ok=True)
        (LAYERS["working"] / "tasks").mkdir(exist_ok=True)
        (LAYERS["working"] / "decisions").mkdir(exist_ok=True)

        # longterm子目录
        (LAYERS["longterm"] / "knowledge").mkdir(exist_ok=True)
        (LAYERS["longterm"] / "knowledge" / "tech").mkdir(exist_ok=True)
        (LAYERS["longterm"] / "knowledge" / "domain").mkdir(exist_ok=True)
        (LAYERS["longterm"] / "projects").mkdir(exist_ok=True)
        (LAYERS["longterm"] / "reference").mkdir(exist_ok=True)

        # entities
        ENTITIES_DIR.mkdir(parents=True, exist_ok=True)

    def generate_id(self, category: str) -> str:
        """生成记忆ID"""
        date = datetime.now().strftime("%Y%m%d")
        count = len(list(self.memory_base.rglob("*.md"))) + 1
        return f"MEM-{date}-{count:03d}"

    def store(
        self,
        category: str,
        title: str,
        content: str,
        tags: Optional[List[str]] = None,
        importance: int = DEFAULT_IMPORTANCE,
        subcategory: Optional[str] = None
    ) -> str:
        """存储记忆"""
        memory_id = self.generate_id(category)

        # 解析category路径
        parts = category.split("/")
        layer = parts[0] if len(parts) > 0 else "episodic"
        subcat = parts[1] if len(parts) > 1 else ""

        # 确定存储目录
        if layer == "episodic":
            if "daily-logs" in category:
                storage_dir = LAYERS["episodic"] / "daily-logs"
            elif "inbox" in category:
                storage_dir = LAYERS["episodic"] / "inbox"
            elif "captures" in category:
                storage_dir = LAYERS["episodic"] / "captures"
            else:
                storage_dir = LAYERS["episodic"] / "inbox"
        elif layer == "working":
            if "sessions" in category:
                storage_dir = LAYERS["working"] / "sessions"
            elif "tasks" in category:
                storage_dir = LAYERS["working"] / "tasks"
            elif "decisions" in category:
                storage_dir = LAYERS["working"] / "decisions"
            else:
                storage_dir = LAYERS["working"] / "tasks"
        elif layer == "longterm":
            if "knowledge" in category:
                storage_dir = LAYERS["longterm"] / "knowledge" / "tech"
            elif "projects" in category:
                storage_dir = LAYERS["longterm"] / "projects"
            elif "reference" in category:
                storage_dir = LAYERS["longterm"] / "reference"
            else:
                storage_dir = LAYERS["longterm"] / "knowledge"
        else:
            storage_dir = LAYERS["episodic"] / "inbox"

        storage_dir.mkdir(parents=True, exist_ok=True)

        # 生成文件名
        safe_title = re.sub(r'[^\w\s-]', '', title)[:30]
        safe_title = re.sub(r'\s+', '-', safe_title)
        filename = f"{memory_id}-{safe_title}.md"
        filepath = storage_dir / filename

        # 构建记忆内容
        tags_str = ", ".join(tags) if tags else ""
        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        memory_content = f"""# {title}

> 记忆ID: {memory_id}
> 分类: {category}
> 重要性: {importance}
> 创建时间: {now}
> 访问次数: 0

---

## 内容

{content}

---

## 元信息

| 属性 | 值 |
|------|-----|
| ID | {memory_id} |
| Category | {category} |
| Tags | {tags_str} |
| Importance | {importance} |
| Created | {now} |
| Access Count | 0 |

---

## 关联

- Related:
- Derived:
- Supersedes:

"""

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(memory_content)

        print(f"✅ 记忆已存储: {memory_id}")
        print(f"   文件: {filepath}")
        return memory_id

    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """搜索记忆"""
        results = []
        query_lower = query.lower()

        for md_file in self.memory_base.rglob("*.md"):
            if md_file.name == "README.md" or md_file.name.startswith("INDEX"):
                continue

            try:
                with open(md_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # 简单匹配
                if query_lower in content.lower():
                    # 提取标题
                    lines = content.split("\n")
                    title = lines[2] if len(lines) > 2 else md_file.stem
                    if title.startswith("# "):
                        title = title[2:]

                    # 提取摘要
                    summary = content[:200].replace("#", "").strip()

                    results.append({
                        "id": md_file.stem.split("-")[0] if "-" in md_file.stem else md_file.stem,
                        "title": title,
                        "file": str(md_file.relative_to(self.memory_base)),
                        "summary": summary[:100] + "..."
                    })

                    if len(results) >= limit * 2:  # 预取更多结果
                        break
            except Exception:
                continue

        # 去重并限制数量
        seen = set()
        unique_results = []
        for r in results:
            if r["id"] not in seen:
                seen.add(r["id"])
                unique_results.append(r)

        return unique_results[:limit]

    def list_memories(self, category: Optional[str] = None, limit: int = 20) -> List[Dict]:
        """列出记忆"""
        results = []

        search_dir = self.memory_base
        if category:
            for layer_name, layer_dir in LAYERS.items():
                if layer_name in category:
                    search_dir = layer_dir
                    break

        for md_file in search_dir.rglob("*.md"):
            if md_file.name == "README.md" or md_file.name.startswith("INDEX"):
                continue

            try:
                with open(md_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # 提取标题
                lines = content.split("\n")
                title = "Untitled"
                for line in lines:
                    if line.startswith("# "):
                        title = line[2:].strip()
                        break

                # 提取ID
                memory_id = md_file.stem.split("-")[0] if "-" in md_file.stem else md_file.stem
                if len(memory_id) > 15:
                    memory_id = memory_id[:15]

                results.append({
                    "id": memory_id,
                    "title": title,
                    "file": str(md_file.relative_to(self.memory_base))
                })
            except Exception:
                continue

        return results[:limit]

    def stats(self) -> Dict:
        """获取记忆统计"""
        stats = {
            "total": 0,
            "by_layer": {},
            "by_category": {}
        }

        for md_file in self.memory_base.rglob("*.md"):
            if md_file.name == "README.md" or md_file.name.startswith("INDEX"):
                continue

            stats["total"] += 1

            # 按层级统计
            for layer_name, layer_dir in LAYERS.items():
                if layer_dir in md_file.parts or str(layer_dir) in str(md_file):
                    stats["by_layer"][layer_name] = stats["by_layer"].get(layer_name, 0) + 1

        return stats

    def daily_log(self, log_type: str, entry: str) -> str:
        """添加每日日志"""
        today = datetime.now().strftime("%Y-%m-%d")
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M")

        log_dir = LAYERS["episodic"] / "daily-logs"
        log_file = log_dir / f"{today}.md"

        # 判断是否新建
        is_new = not log_file.exists()

        # 准备内容
        if is_new:
            header = f"""# 每日日志 {today}

## 今日完成

## 明日计划

## 决策记录

## 问题与解决

"""
        else:
            with open(log_file, "r", encoding="utf-8") as f:
                header = f.read()

        # 追加条目
        emoji_map = {
            "done": "✅",
            "todo": "📋",
            "decision": "📌",
            "idea": "💡",
            "meeting": "📅",
            "note": "📝"
        }
        emoji = emoji_map.get(log_type, "📝")

        new_entry = f"- [{emoji}] {entry} ({date_str})\n"

        # 根据类型追加到对应位置
        type_sections = {
            "done": "## 今日完成",
            "todo": "## 明日计划",
            "decision": "## 决策记录",
            "idea": "## 想法",
            "meeting": "## 会议",
            "note": "## 备注"
        }

        section_header = type_sections.get(log_type, "## 备注")

        if section_header in header:
            # 插入到对应section
            lines = header.split("\n")
            for i, line in enumerate(lines):
                if line == section_header:
                    lines.insert(i + 1, new_entry)
                    break
            content = "\n".join(lines)
        else:
            content = header + f"\n{section_header}\n{new_entry}"

        with open(log_file, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"✅ 日志已添加: {today}")
        print(f"   类型: {log_type}")
        print(f"   内容: {entry}")

        return today


def main():
    parser = argparse.ArgumentParser(description="Memory Operations - 记忆读写工具")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # store命令
    store_parser = subparsers.add_parser("store", help="存储记忆")
    store_parser.add_argument("category", help="分类，如: longterm/projects")
    store_parser.add_argument("title", help="标题")
    store_parser.add_argument("content", help="内容")
    store_parser.add_argument("--tags", nargs="+", help="标签")
    store_parser.add_argument("--importance", type=int, default=5, help="重要性(1-10)")

    # search命令
    search_parser = subparsers.add_parser("search", help="搜索记忆")
    search_parser.add_argument("query", help="搜索关键词")
    search_parser.add_argument("--limit", type=int, default=5, help="结果数量")

    # list命令
    list_parser = subparsers.add_parser("list", help="列出记忆")
    list_parser.add_argument("--category", help="分类筛选")
    list_parser.add_argument("--limit", type=int, default=20, help="结果数量")

    # stats命令
    subparsers.add_parser("stats", help="记忆统计")

    # daily-log命令
    daily_parser = subparsers.add_parser("daily-log", help="添加每日日志")
    daily_parser.add_argument("type", choices=["done", "todo", "decision", "idea", "meeting", "note"], help="日志类型")
    daily_parser.add_argument("entry", help="日志内容")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    ops = MemoryOps()

    if args.command == "store":
        ops.store(args.category, args.title, args.content, args.tags, args.importance)

    elif args.command == "search":
        results = ops.search(args.query, args.limit)
        if results:
            print(f"\n🔍 搜索结果: \"{args.query}\"")
            print("=" * 60)
            for i, r in enumerate(results, 1):
                print(f"\n{i}. {r['title']}")
                print(f"   ID: {r['id']}")
                print(f"   路径: {r['file']}")
                print(f"   摘要: {r['summary']}")
        else:
            print(f"未找到匹配 \"{args.query}\" 的记忆")

    elif args.command == "list":
        results = ops.list_memories(args.category, args.limit)
        if results:
            print(f"\n📚 记忆列表 (共 {len(results)} 条)")
            print("=" * 60)
            for r in results:
                print(f"- {r['id']}: {r['title']}")
                print(f"  路径: {r['file']}")
        else:
            print("暂无记忆")

    elif args.command == "stats":
        stats = ops.stats()
        print("\n📊 记忆统计")
        print("=" * 60)
        print(f"总记忆数: {stats['total']}")
        if stats['by_layer']:
            print("\n按层级:")
            for layer, count in stats['by_layer'].items():
                print(f"  - {layer}: {count}")

    elif args.command == "daily-log":
        ops.daily_log(args.type, args.entry)


if __name__ == "__main__":
    main()
