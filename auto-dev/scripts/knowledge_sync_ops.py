#!/usr/bin/env python3
"""
Knowledge Sync Operations - 知识同步脚本
支持层级提升、归档、同步状态检查

用法:
  python knowledge_sync_ops.py sync [--dry-run]
  python knowledge_sync_ops.py upgrade [--by IMPORTANCE] [--by-access COUNT]
  python knowledge_sync_ops.py archive [--older-than DAYS] [--dry-run]
  python knowledge_sync_ops.py stats
  python knowledge_sync_ops.py health
"""

import os
import sys
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict

# 配置
AUTO_DEV_BASE = Path(__file__).parent.parent
MEMORY_BASE = AUTO_DEV_BASE / "memory"

# 层级目录
LAYERS = {
    "episodic": MEMORY_BASE / "episodic",
    "working": MEMORY_BASE / "working",
    "longterm": MEMORY_BASE / "longterm"
}

# 升级规则
UPGRADE_RULES = {
    ("episodic", "working"): {
        "min_access_count": 5,
        "min_age_days": 7
    },
    ("working", "longterm"): {
        "min_importance": 7,
        "min_access_count": 10
    }
}


class KnowledgeSyncOps:
    def __init__(self):
        self.memory_base = MEMORY_BASE
        self.changes = []

    def get_memory_files(self, layer: str = None) -> List[Path]:
        """获取记忆文件列表"""
        if layer and layer in LAYERS:
            search_dir = LAYERS[layer]
        else:
            search_dir = self.memory_base

        return [f for f in search_dir.rglob("*.md")
                if f.name not in ["README.md", "INDEX.md"] and not f.name.startswith("INDEX")]

    def parse_memory_meta(self, filepath: Path) -> Dict:
        """解析记忆元信息"""
        meta = {
            "path": filepath,
            "layer": self._get_layer(filepath),
            "importance": 5,
            "access_count": 0,
            "created": None,
            "age_days": 0
        }

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            for line in content.split("\n"):
                if "重要性:" in line:
                    try:
                        meta["importance"] = int(line.split(":")[1].strip())
                    except:
                        pass
                elif "访问次数:" in line or "Access Count:" in line:
                    try:
                        count_str = line.split(":")[1].strip()
                        meta["access_count"] = int(count_str)
                    except:
                        pass
                elif "创建时间:" in line or "Created:" in line:
                    try:
                        date_str = line.split(":")[1].strip()
                        meta["created"] = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
                        meta["age_days"] = (datetime.now() - meta["created"]).days
                    except:
                        pass
        except:
            pass

        return meta

    def _get_layer(self, filepath: Path) -> str:
        """获取记忆所属层级"""
        path_str = str(filepath)
        for layer_name in LAYERS.keys():
            if layer_name in path_str:
                return layer_name
        return "unknown"

    def sync(self, dry_run: bool = True) -> Dict:
        """执行同步"""
        results = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "dry_run": dry_run,
            "upgrades": [],
            "archives": [],
            "merges": [],
            "errors": []
        }

        # 1. 检查层级提升
        upgrade_candidates = self._find_upgrade_candidates()
        results["upgrades"] = upgrade_candidates

        # 2. 检查需要归档的
        archive_candidates = self._find_archive_candidates()
        results["archives"] = archive_candidates

        # 3. 检查重复
        duplicates = self._find_duplicates()
        results["merges"] = duplicates

        # 如果不是dry_run，执行变更
        if not dry_run:
            for candidate in upgrade_candidates:
                if self._execute_upgrade(candidate):
                    self.changes.append(f"提升: {candidate['path'].name} → {candidate['target_layer']}")

        return results

    def _find_upgrade_candidates(self) -> List[Dict]:
        """查找可以提升层级的记忆"""
        candidates = []

        for layer_from, rules in UPGRADE_RULES.items():
            search_dir = LAYERS.get(layer_from[0])
            if not search_dir or not search_dir.exists():
                continue

            for mem_file in self.get_memory_files(layer_from[0]):
                meta = self.parse_memory_meta(mem_file)

                # 检查是否满足升级条件
                if layer_from == ("episodic", "working"):
                    if (meta["access_count"] >= rules["min_access_count"] and
                            meta["age_days"] >= rules["min_age_days"]):
                        candidates.append({
                            "path": mem_file,
                            "from_layer": "episodic",
                            "target_layer": "working",
                            "reason": f"访问次数({meta['access_count']}) >= {rules['min_access_count']} 且 年龄({meta['age_days']}天) >= {rules['min_age_days']}天",
                            "importance": meta["importance"]
                        })
                elif layer_from == ("working", "longterm"):
                    if (meta["importance"] >= rules["min_importance"] or
                            meta["access_count"] >= rules["min_access_count"]):
                        candidates.append({
                            "path": mem_file,
                            "from_layer": "working",
                            "target_layer": "longterm",
                            "reason": f"重要性({meta['importance']}) >= {rules['min_importance']} 或 访问次数({meta['access_count']}) >= {rules['min_access_count']}",
                            "importance": meta["importance"]
                        })

        return candidates

    def _find_archive_candidates(self) -> List[Dict]:
        """查找可以归档的记忆"""
        candidates = []

        for layer_name, layer_dir in LAYERS.items():
            if not layer_dir.exists():
                continue

            # episodic层超过30天
            if layer_name == "episodic":
                for mem_file in self.get_memory_files(layer_name):
                    meta = self.parse_memory_meta(mem_file)
                    if meta["age_days"] > 30 and meta["importance"] < 5:
                        candidates.append({
                            "path": mem_file,
                            "layer": layer_name,
                            "age_days": meta["age_days"],
                            "importance": meta["importance"],
                            "reason": f"年龄{meta['age_days']}天 > 30天 且 重要性{importance} < 5"
                        })

        return candidates

    def _find_duplicates(self) -> List[Dict]:
        """查找重复记忆"""
        # 简化实现：只检查同层级的相似标题
        duplicates = []
        files = self.get_memory_files()

        for i, file1 in enumerate(files):
            title1 = file1.stem.lower()
            for file2 in files[i+1:]:
                title2 = file2.stem.lower()
                # 简单相似度：共同词数
                words1 = set(title1.replace("-", " ").split())
                words2 = set(title2.replace("-", " ").split())
                common = words1 & words2
                if len(common) >= 3:  # 3个以上共同词
                    duplicates.append({
                        "file1": str(file1.relative_to(self.memory_base)),
                        "file2": str(file2.relative_to(self.memory_base)),
                        "common_words": list(common)
                    })

        return duplicates

    def _execute_upgrade(self, candidate: Dict) -> bool:
        """执行层级提升"""
        try:
            source = candidate["path"]
            target_layer = candidate["target_layer"]
            target_dir = LAYERS[target_layer]

            # 创建目标子目录
            relative = source.relative_to(LAYERS[candidate["from_layer"]])
            target_path = target_dir / relative

            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(target_path))

            return True
        except Exception as e:
            return False

    def upgrade(self, by_importance: int = None, by_access: int = None) -> List[Dict]:
        """手动触发层级提升"""
        candidates = self._find_upgrade_candidates()

        if by_importance:
            candidates = [c for c in candidates if c.get("importance", 0) >= by_importance]

        if by_access:
            candidates = [c for c in candidates if c.get("access_count", 0) >= by_access]

        return candidates

    def archive(self, older_than: int = 30, dry_run: bool = True) -> List[Dict]:
        """归档过期记忆"""
        candidates = self._find_archive_candidates()
        candidates = [c for c in candidates if c.get("age_days", 0) > older_than]

        if not dry_run:
            for candidate in candidates:
                source = candidate["path"]
                archive_dir = self.memory_base / "archive"
                archive_dir.mkdir(exist_ok=True)

                target = archive_dir / source.name
                try:
                    shutil.move(str(source), str(target))
                except Exception:
                    pass

        return candidates

    def get_stats(self) -> Dict:
        """获取统计信息"""
        stats = {
            "total": 0,
            "by_layer": {},
            "by_category": {},
            "avg_importance": 0,
            "total_access": 0
        }

        importance_sum = 0
        total_access = 0

        for mem_file in self.get_memory_files():
            stats["total"] += 1

            layer = self._get_layer(mem_file)
            stats["by_layer"][layer] = stats["by_layer"].get(layer, 0) + 1

            # 统计子目录
            category = str(mem_file.parent.relative_to(self.memory_base))
            stats["by_category"][category] = stats["by_category"].get(category, 0) + 1

            meta = self.parse_memory_meta(mem_file)
            importance_sum += meta["importance"]
            total_access += meta["access_count"]

        if stats["total"] > 0:
            stats["avg_importance"] = importance_sum / stats["total"]
            stats["total_access"] = total_access

        return stats

    def health_check(self) -> Dict:
        """健康检查"""
        health = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "healthy",
            "issues": [],
            "metrics": {}
        }

        stats = self.get_stats()
        health["metrics"] = {
            "total_memories": stats["total"],
            "by_layer": stats["by_layer"],
            "avg_importance": round(stats["avg_importance"], 2),
            "total_access": stats["total_access"]
        }

        # 检查问题
        if stats["total"] == 0:
            health["issues"].append("ℹ️ 记忆库为空")

        if stats["avg_importance"] < 5:
            health["issues"].append("⚠️ 平均重要性偏低")

        # 检查层级分布
        layer_counts = stats.get("by_layer", {})
        if layer_counts.get("episodic", 0) > layer_counts.get("longterm", 0) * 2:
            health["issues"].append("⚠️ 情节记忆过多，建议提升重要记忆到长期")

        return health


def main():
    parser = argparse.ArgumentParser(description="Knowledge Sync Operations - 知识同步")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # sync命令
    sync_parser = subparsers.add_parser("sync", help="执行同步")
    sync_parser.add_argument("--dry-run", action="store_true", help="仅预览")

    # upgrade命令
    upgrade_parser = subparsers.add_parser("upgrade", help="层级提升")
    upgrade_parser.add_argument("--by-importance", type=int, help="按重要性筛选")
    upgrade_parser.add_argument("--by-access", type=int, help="按访问次数筛选")

    # archive命令
    archive_parser = subparsers.add_parser("archive", help="归档")
    archive_parser.add_argument("--older-than", type=int, default=30, help="超过多少天")
    archive_parser.add_argument("--dry-run", action="store_true", help="仅预览")

    # stats命令
    subparsers.add_parser("stats", help="统计")

    # health命令
    subparsers.add_parser("health", help="健康检查")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    ops = KnowledgeSyncOps()

    if args.command == "sync":
        result = ops.sync(args.dry_run)
        print(f"\n📊 知识同步报告 - {result['timestamp']}")
        print("=" * 60)
        print(f"模式: {'预览' if result['dry_run'] else '执行'}")
        print(f"\n层级提升候选: {len(result['upgrades'])}")
        for c in result['upgrades']:
            print(f"  - {c['path'].name}: {c['from_layer']} → {c['target_layer']}")
            print(f"    原因: {c['reason']}")

        print(f"\n归档候选: {len(result['archives'])}")
        for c in result['archives'][:5]:
            print(f"  - {c['path'].name}: {c['age_days']}天")

        print(f"\n重复记忆: {len(result['merges'])}")
        for d in result['merges'][:3]:
            print(f"  - {d['file1']} ≈ {d['file2']}")

    elif args.command == "upgrade":
        candidates = ops.upgrade(args.by_importance, args.by_access)
        print(f"\n📤 层级提升候选 ({len(candidates)} 条)")
        for c in candidates:
            print(f"  - {c['path'].name}")
            print(f"    {c['reason']}")

    elif args.command == "archive":
        candidates = ops.archive(args.older_than, args.dry_run)
        print(f"\n📦 {'归档候选' if args.dry_run else '归档执行'} ({len(candidates)} 条)")
        for c in candidates:
            print(f"  - {c['path'].name}: {c['age_days']}天")

    elif args.command == "stats":
        stats = ops.get_stats()
        print(f"\n📊 记忆统计")
        print("=" * 50)
        print(f"总记忆数: {stats['total']}")
        print(f"平均重要性: {stats['avg_importance']}")
        print(f"总访问次数: {stats['total_access']}")
        print("\n按层级:")
        for layer, count in stats['by_layer'].items():
            print(f"  - {layer}: {count}")
        print("\n按分类:")
        for cat, count in list(stats['by_category'].items())[:10]:
            print(f"  - {cat}: {count}")

    elif args.command == "health":
        result = ops.health_check()
        print(f"\n🏥 知识系统健康检查 - {result['timestamp']}")
        print("=" * 50)
        print(f"状态: {result['status'].upper()}")
        print("\n指标:")
        for key, value in result['metrics'].items():
            print(f"  - {key}: {value}")
        if result['issues']:
            print("\n问题:")
            for issue in result['issues']:
                print(f"  {issue}")


if __name__ == "__main__":
    main()
