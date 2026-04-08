#!/usr/bin/env python3
"""
Task Operations - 任务分析与管理脚本
支持任务分解、状态跟踪、优先级排序

用法:
  python task_ops.py create <title> <description> [--priority N] [--type TYPE]
  python task_ops.py list [--status STATUS] [--limit N]
  python task_ops.py update <task_id> --status STATUS
  python task_ops.py analyze <task_description>
  python task_ops.py breakdown <task_id>

示例:
  python task_ops.py create "完成用户模块" "实现用户CRUD功能" --priority 8 --type feature
  python task_ops.py list --status pending --limit 10
  python task_ops.py update TASK-20260403-001 --status in_progress
  python task_ops.py analyze "需要实现一个用户登录功能"
  python task_ops.py breakdown TASK-20260403-001
"""

import os
import sys
import json
import argparse
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

# 配置
AUTO_DEV_BASE = Path(__file__).parent.parent
TASKS_DIR = AUTO_DEV_BASE / "tasks"
MEMORY_OPS = AUTO_DEV_BASE / "scripts" / "memory_ops.py"

# 任务状态
STATUS_OPTIONS = ["pending", "in_progress", "completed", "blocked", "cancelled"]

# 任务类型
TYPE_OPTIONS = ["feature", "bugfix", "optimization", "refactor", "docs", "test"]

# 优先级
PRIORITY_MAP = {"P0": 10, "P1": 8, "P2": 5, "P3": 3}


class TaskOps:
    def __init__(self):
        self.tasks_dir = TASKS_DIR
        self.tasks_dir.mkdir(exist_ok=True)
        (self.tasks_dir / "backlog").mkdir(exist_ok=True)
        (self.tasks_dir / "in_progress").mkdir(exist_ok=True)
        (self.tasks_dir / "completed").mkdir(exist_ok=True)
        (self.tasks_dir / "templates").mkdir(exist_ok=True)

    def generate_id(self, prefix: str = "TASK") -> str:
        """生成任务ID"""
        date = datetime.now().strftime("%Y%m%d")
        count = len(list(self.tasks_dir.rglob("*.md"))) + 1
        return f"{prefix}-{date}-{count:03d}"

    def create(
        self,
        title: str,
        description: str,
        priority: int = 5,
        task_type: str = "feature",
        owner: Optional[str] = None
    ) -> str:
        """创建任务"""
        task_id = self.generate_id()

        # 确定状态目录
        status = "backlog"
        status_dir = self.tasks_dir / status

        safe_title = re.sub(r'[^\w\s-]', '', title)[:30]
        safe_title = re.sub(r'\s+', '-', safe_title)
        filename = f"{task_id}-{safe_title}.md"
        filepath = status_dir / filename

        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        # 判断优先级标签
        if priority >= 9:
            priority_label = "P0"
        elif priority >= 7:
            priority_label = "P1"
        elif priority >= 5:
            priority_label = "P2"
        else:
            priority_label = "P3"

        content = f"""# Task: {title}

- ID: {task_id}
- Type: {task_type}
- Priority: {priority_label} ({priority})
- Status: pending
- Owner: {owner or "unassigned"}
- Created: {now}
- Updated: {now}

## 描述

{description}

## 验收标准

- [ ] 标准1
- [ ] 标准2

## 分解子任务

<!-- 子任务列表 -->

## 关联

- Parent:
- Children:
- Related:

## 备注

"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"[OK] 任务已创建: {task_id}")
        print(f"   标题: {title}")
        print(f"   优先级: {priority_label}")
        print(f"   状态: pending")
        print(f"   文件: {filepath}")

        return task_id

    def list_tasks(self, status: Optional[str] = None, limit: int = 20) -> List[Dict]:
        """列出任务"""
        results = []

        search_dirs = [self.tasks_dir]
        if status:
            status_dir = self.tasks_dir / status
            if status_dir.exists():
                search_dirs = [status_dir]

        for task_file in self.tasks_dir.rglob("*.md"):
            if task_file.name == "README.md":
                continue

            try:
                with open(task_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # 提取信息
                task_id = ""
                title = task_file.stem
                priority = 5
                task_status = "unknown"
                task_type = "feature"

                for line in content.split("\n"):
                    if line.startswith("- ID:"):
                        task_id = line.split(":", 1)[1].strip()
                    elif line.startswith("## Task:"):
                        title = line.split(":", 1)[1].strip()
                    elif line.startswith("- Priority:"):
                        priority_str = line.split(":", 1)[1].strip()
                        if "(" in priority_str:
                            priority = int(priority_str.split("(")[1].split(")")[0])
                    elif line.startswith("- Status:"):
                        task_status = line.split(":", 1)[1].strip()
                    elif line.startswith("- Type:"):
                        task_type = line.split(":", 1)[1].strip()

                # 判断状态目录
                file_status = "backlog"
                for s in ["in_progress", "completed", "blocked"]:
                    if s.replace("_", "-") in str(task_file).replace("_", "-"):
                        file_status = s
                        break

                results.append({
                    "id": task_id,
                    "title": title,
                    "priority": priority,
                    "status": task_status,
                    "type": task_type,
                    "file": str(task_file.relative_to(self.tasks_dir))
                })
            except Exception:
                continue

        # 排序：按优先级降序
        results.sort(key=lambda x: x["priority"], reverse=True)

        return results[:limit]

    def update_status(self, task_id: str, new_status: str) -> bool:
        """更新任务状态"""
        if new_status not in STATUS_OPTIONS:
            print(f"❌ 无效状态: {new_status}")
            print(f"   可用状态: {', '.join(STATUS_OPTIONS)}")
            return False

        # 查找任务文件
        task_file = None
        for f in self.tasks_dir.rglob("*.md"):
            if task_id in f.stem and f.name != "README.md":
                task_file = f
                break

        if not task_file:
            print(f"❌ 未找到任务: {task_id}")
            return False

        # 读取内容
        with open(task_file, "r", encoding="utf-8") as f:
            content = f.read()

        # 更新状态
        lines = content.split("\n")
        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        for i, line in enumerate(lines):
            if line.startswith("- Status:"):
                lines[i] = f"- Status: {new_status}"
            elif line.startswith("- Updated:"):
                lines[i] = f"- Updated: {now}"

        new_content = "\n".join(lines)

        # 如果状态变更涉及目录移动
        old_status = "backlog"
        for s in ["in_progress", "completed", "blocked"]:
            if s in str(task_file):
                old_status = s

        if old_status != new_status.replace("_", "-"):
            # 移动文件
            new_status_dir = self.tasks_dir / new_status.replace("_", "-")
            new_status_dir.mkdir(exist_ok=True)
            new_filename = task_file.name
            new_filepath = new_status_dir / new_filename

            with open(new_filepath, "w", encoding="utf-8") as f:
                f.write(new_content)

            task_file.unlink()

            print(f"[OK] 任务状态已更新: {task_id} → {new_status}")
            print(f"   文件已移动: {new_filepath}")
        else:
            with open(task_file, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"[OK] 任务状态已更新: {task_id} → {new_status}")

        return True

    def analyze(self, task_description: str) -> Dict:
        """分析任务，返回分解建议"""
        analysis = {
            "original": task_description,
            "estimated_complexity": "medium",
            "suggested_priority": 5,
            "suggested_type": "feature",
            "subtasks": [],
            "skills_needed": [],
            "risks": []
        }

        desc_lower = task_description.lower()

        # 判断复杂度
        complexity_keywords = {
            "high": ["微服务", "分布式", "集群", "事务", "分布式锁", "重构"],
            "low": ["单表", "简单", "增删改查", "basic", "simple"]
        }

        for kw in complexity_keywords["high"]:
            if kw in desc_lower:
                analysis["estimated_complexity"] = "high"
                analysis["suggested_priority"] = min(analysis["suggested_priority"] + 2, 10)
                break

        for kw in complexity_keywords["low"]:
            if kw in desc_lower:
                analysis["estimated_complexity"] = "low"
                analysis["suggested_priority"] = max(analysis["suggested_priority"] - 2, 1)
                break

        # 判断类型
        type_keywords = {
            "bugfix": ["bug", "修复", "错误", "异常", "问题"],
            "optimization": ["优化", "性能", "提升", "改善"],
            "docs": ["文档", "注释", "说明"],
            "test": ["测试", "用例"]
        }

        for t, kws in type_keywords.items():
            if any(kw in desc_lower for kw in kws):
                analysis["suggested_type"] = t
                break

        # 生成子任务建议
        if analysis["suggested_type"] == "feature":
            analysis["subtasks"] = [
                "需求确认",
                "技术方案设计",
                "数据库设计",
                "接口定义",
                "后端实现",
                "前端实现",
                "联调测试",
                "文档更新"
            ]
        elif analysis["suggested_type"] == "bugfix":
            analysis["subtasks"] = [
                "复现问题",
                "定位根因",
                "修复代码",
                "验证修复",
                "回归测试"
            ]

        # 技能建议
        skill_keywords = {
            "java": ["java", "spring", "后端"],
            "vue": ["vue", "前端", "页面"],
            "python": ["python", "脚本", "自动化"],
            "database": ["数据库", "sql", "表设计"],
            "devops": ["部署", "ci", "cd", "docker"]
        }

        for skill, kws in skill_keywords.items():
            if any(kw in desc_lower for kw in kws):
                analysis["skills_needed"].append(skill)

        return analysis

    def breakdown(self, task_id: str) -> List[str]:
        """分解任务为子任务"""
        # 查找任务
        task_file = None
        for f in self.tasks_dir.rglob("*.md"):
            if task_id in f.stem and f.name != "README.md":
                task_file = f
                break

        if not task_file:
            print(f"❌ 未找到任务: {task_id}")
            return []

        with open(task_file, "r", encoding="utf-8") as f:
            content = f.read()

        # 提取任务类型和描述
        task_type = "feature"
        title = task_file.stem

        for line in content.split("\n"):
            if line.startswith("- Type:"):
                task_type = line.split(":", 1)[1].strip()
            elif line.startswith("# Task:"):
                title = line.split(":", 1)[1].strip()

        # 根据类型生成子任务
        templates = {
            "feature": [
                "需求澄清与确认",
                "技术方案设计",
                "数据库/接口设计",
                "代码实现",
                "单元测试",
                "联调测试",
                "功能验证",
                "文档更新"
            ],
            "bugfix": [
                "问题复现",
                "根因分析",
                "修复方案设计",
                "代码修复",
                "验证修复",
                "回归测试"
            ],
            "optimization": [
                "性能分析",
                "瓶颈定位",
                "优化方案设计",
                "代码优化",
                "性能对比测试"
            ]
        }

        subtasks = templates.get(task_type, templates["feature"])

        # 创建子任务
        parent_id = task_id
        created_subtasks = []

        for i, subtask_title in enumerate(subtasks, 1):
            sub_id = f"{parent_id}-SUB{i:02d}"
            full_title = f"{title} - {subtask_title}"

            sub_priority = 5 if i < len(subtasks) else 8  # 最后的验证任务优先级高

            sub_task_id = self.create(
                title=full_title,
                description=f"[子任务] {subtask_title}",
                priority=sub_priority,
                task_type="feature"
            )
            created_subtasks.append(sub_task_id)

        print(f"[OK] 任务已分解: {parent_id}")
        print(f"   生成 {len(created_subtasks)} 个子任务")

        return created_subtasks


def main():
    parser = argparse.ArgumentParser(description="Task Operations - 任务分析与管理")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # create命令
    create_parser = subparsers.add_parser("create", help="创建任务")
    create_parser.add_argument("title", help="任务标题")
    create_parser.add_argument("description", help="任务描述")
    create_parser.add_argument("--priority", type=int, default=5, help="优先级1-10")
    create_parser.add_argument("--type", default="feature", choices=TYPE_OPTIONS, help="任务类型")
    create_parser.add_argument("--owner", help="负责人")

    # list命令
    list_parser = subparsers.add_parser("list", help="列出任务")
    list_parser.add_argument("--status", choices=STATUS_OPTIONS, help="状态筛选")
    list_parser.add_argument("--limit", type=int, default=20, help="数量限制")

    # update命令
    update_parser = subparsers.add_parser("update", help="更新任务")
    update_parser.add_argument("task_id", help="任务ID")
    update_parser.add_argument("--status", required=True, choices=STATUS_OPTIONS, help="新状态")

    # analyze命令
    analyze_parser = subparsers.add_parser("analyze", help="分析任务")
    analyze_parser.add_argument("description", help="任务描述")

    # breakdown命令
    breakdown_parser = subparsers.add_parser("breakdown", help="分解任务")
    breakdown_parser.add_argument("task_id", help="任务ID")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    ops = TaskOps()

    if args.command == "create":
        ops.create(args.title, args.description, args.priority, args.type, args.owner)

    elif args.command == "list":
        results = ops.list_tasks(args.status, args.limit)
        if results:
            print(f"\n📋 任务列表 (共 {len(results)} 条)")
            print("=" * 80)
            for r in results:
                priority_icon = "[HIGH]" if r["priority"] >= 8 else "[MED]" if r["priority"] >= 5 else "[LOW]"
                print(f"{priority_icon} {r['id']} | {r['title'][:40]}")
                print(f"   类型: {r['type']} | 状态: {r['status']} | 优先级: {r['priority']}")
        else:
            print("暂无任务")

    elif args.command == "update":
        ops.update_status(args.task_id, args.status)

    elif args.command == "analyze":
        result = ops.analyze(args.description)
        print(f"\n[ANALYSIS] 任务分析: {result['original']}")
        print("=" * 60)
        print(f"复杂度: {result['estimated_complexity']}")
        print(f"建议优先级: P{result['suggested_priority']}")
        print(f"建议类型: {result['suggested_type']}")
        print(f"所需技能: {', '.join(result['skills_needed']) if result['skills_needed'] else '无'}")
        print(f"\n建议子任务:")
        for i, subtask in enumerate(result['subtasks'], 1):
            print(f"  {i}. {subtask}")

    elif args.command == "breakdown":
        ops.breakdown(args.task_id)


if __name__ == "__main__":
    main()
