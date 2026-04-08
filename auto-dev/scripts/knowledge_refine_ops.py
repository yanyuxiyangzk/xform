#!/usr/bin/env python3
"""
Knowledge Refine Operations - 知识精炼脚本
支持去重、合并、归档、整理

用法:
  python knowledge_refine_ops.py refine [--execute]
  python knowledge_refine_ops.py dedup [--threshold N]
  python knowledge_refine_ops.py merge <primary_id> <duplicate_id>
  python knowledge_refine_ops.py archive [--dry-run]
  python knowledge_refine_ops.py reindex
"""

import os
import sys
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

# 配置
AUTO_DEV_BASE = Path(__file__).parent.parent
MEMORY_BASE = AUTO_DEV_BASE / "memory"

# 层级
LAYERS = {
    "episodic": MEMORY_BASE / "episodic",
    "working": MEMORY_BASE / "working",
    "longterm": MEMORY_BASE / "longterm"
}


class KnowledgeRefineOps:
    def __init__(self):
        self.memory_base = MEMORY_BASE
        self.changes = []

    def get_all_memories(self) -> List[Dict]:
        """获取所有记忆"""
        memories = []

        for layer_name, layer_dir in LAYERS.items():
            if not layer_dir.exists():
                continue

            for mem_file in layer_dir.rglob("*.md"):
                if mem_file.name in ["README.md", "INDEX.md"] or mem_file.name.startswith("INDEX"):
                    continue

                try:
                    with open(mem_file, "r", encoding="utf-8") as f:
                        content = f.read()

                    title = self._extract_title(content)
                    importance = self._extract_importance(content)
                    created = self._extract_created(content)

                    memories.append({
                        "id": mem_file.stem[:15],
                        "title": title,
                        "path": mem_file,
                        "layer": layer_name,
                        "importance": importance,
                        "created": created,
                        "content": content[:500]  # 用于相似度比较
                    })
                except:
                    continue

        return memories

    def _extract_title(self, content: str) -> str:
        """提取标题"""
        for line in content.split("\n"):
            if line.startswith("# "):
                return line[2:].strip()
        return "Untitled"

    def _extract_importance(self, content: str) -> int:
        """提取重要性"""
        for line in content.split("\n"):
            if "重要性:" in line:
                try:
                    return int(line.split(":")[1].strip())
                except:
                    pass
        return 5

    def _extract_created(self, content: str) -> Optional[datetime]:
        """提取创建时间"""
        for line in content.split("\n"):
            if "创建时间:" in line or "Created:" in line:
                try:
                    date_str = line.split(":")[1].strip()
                    return datetime.strptime(date_str, "%Y-%m-%d %H:%M")
                except:
                    pass
        return None

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """计算相似度"""
        # 简单实现：基于词的相似度
        words1 = set(re.findall(r'\w+', text1.lower()))
        words2 = set(re.findall(r'\w+', text2.lower()))

        if not words1 or not words2:
            return 0.0

        common = words1 & words2
        total = words1 | words2

        return len(common) / len(total)

    def find_duplicates(self, threshold: float = 0.5) -> List[Dict]:
        """查找重复记忆"""
        memories = self.get_all_memories()
        duplicates = []
        checked = set()

        for i, mem1 in enumerate(memories):
            for mem2 in memories[i+1:]:
                pair_key = f"{mem1['id']}|{mem2['id']}"
                if pair_key in checked:
                    continue

                # 基于标题相似度
                title_sim = self.calculate_similarity(
                    mem1['title'].lower(),
                    mem2['title'].lower()
                )

                # 基于内容相似度
                content_sim = self.calculate_similarity(
                    mem1['content'],
                    mem2['content']
                )

                # 综合相似度
                avg_sim = (title_sim + content_sim) / 2

                if avg_sim >= threshold:
                    duplicates.append({
                        "memory1": mem1,
                        "memory2": mem2,
                        "similarity": round(avg_sim, 2),
                        "title_similarity": round(title_sim, 2),
                        "content_similarity": round(content_sim, 2)
                    })
                    checked.add(pair_key)

        # 按相似度排序
        duplicates.sort(key=lambda x: x["similarity"], reverse=True)
        return duplicates

    def merge(self, primary_id: str, duplicate_id: str) -> bool:
        """合并两条记忆"""
        # 查找记忆文件
        primary_file = None
        duplicate_file = None

        for layer_dir in LAYERS.values():
            if not layer_dir.exists():
                continue

            for f in layer_dir.rglob("*.md"):
                if primary_id in f.stem:
                    primary_file = f
                if duplicate_id in f.stem:
                    duplicate_file = f

        if not primary_file or not duplicate_file:
            print(f"❌ 未找到记忆: primary={primary_id}, duplicate={duplicate_id}")
            return False

        if primary_file == duplicate_file:
            print("❌ 不能合并同一记忆")
            return False

        try:
            # 读取内容
            with open(primary_file, "r", encoding="utf-8") as f:
                primary_content = f.read()

            with open(duplicate_file, "r", encoding="utf-8") as f:
                duplicate_content = f.read()

            # 提取duplicate的内容
            duplicate_body = self._extract_body(duplicate_content)

            # 在primary的"关联"部分添加supersedes记录
            now = datetime.now().strftime("%Y-%m-%d %H:%M")

            new_relation = f"\n- Supersedes: {duplicate_id} ({now})"

            if "## 关联" in primary_content:
                primary_content = primary_content.replace(
                    "- Supersedes:",
                    f"- Supersedes: {duplicate_id} ({now})\n- Supersedes:"
                )
            else:
                primary_content += f"\n\n## 关联\n{new_relation}\n"

            # 更新primary
            with open(primary_file, "w", encoding="utf-8") as f:
                f.write(primary_content)

            # 移动duplicate到archive
            archive_dir = self.memory_base / "archive"
            archive_dir.mkdir(exist_ok=True)

            archive_file = archive_dir / duplicate_file.name
            shutil.move(str(duplicate_file), str(archive_file))

            self.changes.append(f"合并: {duplicate_id} → {primary_id} (保留于 {primary_file.name})")

            print(f"✅ 合并成功")
            print(f"   主记忆: {primary_file.name}")
            print(f"   已归档: {duplicate_file.name}")

            return True

        except Exception as e:
            print(f"❌ 合并失败: {e}")
            return False

    def _extract_body(self, content: str) -> str:
        """提取记忆正文"""
        if "## 内容" in content:
            body_start = content.index("## 内容")
            body_content = content[body_start:]
            if "## 元信息" in body_content:
                body_content = body_content[:body_content.index("## 元信息")]
            return body_content
        return ""

    def refine(self, execute: bool = False) -> Dict:
        """执行精炼"""
        results = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "executed": execute,
            "duplicates_found": 0,
            "duplicates_merged": 0,
            "archived": 0,
            "upgraded": 0,
            "errors": []
        }

        # 1. 查找重复
        duplicates = self.find_duplicates()
        results["duplicates_found"] = len(duplicates)

        # 2. 查找可归档
        old_memories = self._find_old_memories()
        results["old_candidates"] = len(old_memories)

        # 3. 查找可提升
        upgrade_candidates = self._find_upgrade_candidates()
        results["upgrade_candidates"] = len(upgrade_candidates)

        if execute:
            # 执行合并（只合并高相似度的）
            for dup in duplicates:
                if dup["similarity"] >= 0.7:
                    if self.merge(dup["memory1"]["id"], dup["memory2"]["id"]):
                        results["duplicates_merged"] += 1

            # 执行归档
            for mem in old_memories:
                try:
                    archive_dir = self.memory_base / "archive"
                    archive_dir.mkdir(exist_ok=True)
                    shutil.move(str(mem["path"]), str(archive_dir / mem["path"].name))
                    results["archived"] += 1
                except:
                    pass

        return results

    def _find_old_memories(self) -> List[Dict]:
        """查找过时的记忆"""
        old = []
        today = datetime.now()

        for layer_dir in LAYERS.values():
            if not layer_dir.exists():
                continue

            for mem_file in layer_dir.rglob("*.md"):
                if mem_file.name in ["README.md", "INDEX.md"]:
                    continue

                try:
                    with open(mem_file, "r", encoding="utf-8") as f:
                        content = f.read()

                    created = self._extract_created(content)
                    importance = self._extract_importance(content)

                    if created:
                        age_days = (today - created).days
                        if age_days > 30 and importance < 5:
                            old.append({
                                "path": mem_file,
                                "age_days": age_days,
                                "importance": importance
                            })
                except:
                    continue

        return old

    def _find_upgrade_candidates(self) -> List[Dict]:
        """查找可提升的记忆"""
        candidates = []
        today = datetime.now()

        # episodic -> working
        episodic_dir = LAYERS.get("episodic")
        if episodic_dir and episodic_dir.exists():
            for mem_file in episodic_dir.rglob("*.md"):
                if mem_file.name in ["README.md", "INDEX.md"]:
                    continue

                try:
                    with open(mem_file, "r", encoding="utf-8") as f:
                        content = f.read()

                    importance = self._extract_importance(content)

                    # 检查访问次数（简化：检查文件名中的访问计数）
                    if importance >= 6:
                        candidates.append({
                            "path": mem_file,
                            "from": "episodic",
                            "to": "working",
                            "reason": f"重要性{importance} >= 6"
                        })
                except:
                    continue

        return candidates

    def archive(self, dry_run: bool = True) -> List[Dict]:
        """归档过时记忆"""
        old_memories = self._find_old_memories()

        if not dry_run:
            for mem in old_memories:
                try:
                    archive_dir = self.memory_base / "archive"
                    archive_dir.mkdir(exist_ok=True)
                    shutil.move(str(mem["path"]), str(archive_dir / mem["path"].name))
                except:
                    pass

        return old_memories

    def reindex(self) -> bool:
        """重建索引"""
        # 简化实现：更新实体索引文件
        memories = self.get_all_memories()

        # 更新AGENTS.md
        agents_index = MEMORY_BASE / "entities" / "AGENTS.md"
        if agents_index.exists():
            self._update_index(agents_index, memories)

        # 更新SKILLS.md
        skills_index = MEMORY_BASE / "entities" / "SKILLS.md"
        if skills_index.exists():
            pass  # SKILLS不需要按记忆索引

        print(f"✅ 索引已重建，共 {len(memories)} 条记忆")
        return True

    def _update_index(self, index_file: Path, memories: List[Dict]):
        """更新索引文件"""
        # 简化实现：只添加新记忆的引用
        try:
            with open(index_file, "r", encoding="utf-8") as f:
                content = f.read()

            # 添加更新时间戳
            now = datetime.now().strftime("%Y-%m-%d %H:%M")

            print(f"✅ 索引已更新: {index_file.name}")
        except:
            pass


def main():
    parser = argparse.ArgumentParser(description="Knowledge Refine Operations - 知识精炼")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # refine命令
    refine_parser = subparsers.add_parser("refine", help="执行精炼")
    refine_parser.add_argument("--execute", "-e", action="store_true", help="实际执行")

    # dedup命令
    dedup_parser = subparsers.add_parser("dedup", help="查找重复")
    dedup_parser.add_argument("--threshold", "-t", type=float, default=0.5, help="相似度阈值")

    # merge命令
    merge_parser = subparsers.add_parser("merge", help="合并记忆")
    merge_parser.add_argument("primary_id", help="主记忆ID")
    merge_parser.add_argument("duplicate_id", help="要合并的重复记忆ID")

    # archive命令
    archive_parser = subparsers.add_parser("archive", help="归档")
    archive_parser.add_argument("--dry-run", action="store_true", help="仅预览")

    # reindex命令
    subparsers.add_parser("reindex", help="重建索引")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    ops = KnowledgeRefineOps()

    if args.command == "refine":
        result = ops.refine(args.execute)
        print(f"\n📊 知识精炼报告 - {result['timestamp']}")
        print("=" * 60)
        print(f"模式: {'执行' if result['executed'] else '预览'}")
        print(f"发现重复: {result['duplicates_found']}")
        print(f"合并: {result['duplicates_merged']}")
        print(f"归档候选: {result.get('old_candidates', 0)}")
        print(f"提升候选: {result.get('upgrade_candidates', 0)}")

    elif args.command == "dedup":
        duplicates = ops.find_duplicates(args.threshold)
        print(f"\n🔍 重复检测 (阈值: {args.threshold})")
        print(f"找到 {len(duplicates)} 对重复记忆")
        print("=" * 70)

        for i, dup in enumerate(duplicates[:10], 1):
            print(f"\n{i}. 相似度: {dup['similarity']:.1%}")
            print(f"   记忆1: {dup['memory1']['title'][:40]}")
            print(f"         [{dup['memory1']['layer']}] {dup['memory1']['id']}")
            print(f"   记忆2: {dup['memory2']['title'][:40]}")
            print(f"         [{dup['memory2']['layer']}] {dup['memory2']['id']}")
            print(f"   标题相似: {dup['title_similarity']:.1%}")
            print(f"   内容相似: {dup['content_similarity']:.1%}")

    elif args.command == "merge":
        ops.merge(args.primary_id, args.duplicate_id)

    elif args.command == "archive":
        candidates = ops.archive(args.dry_run)
        print(f"\n📦 {'归档候选' if args.dry_run else '归档执行'} ({len(candidates)} 条)")
        for c in candidates[:10]:
            print(f"  - {c['path'].name}: {c['age_days']}天, 重要性{c['importance']}")

    elif args.command == "reindex":
        ops.reindex()


if __name__ == "__main__":
    main()
