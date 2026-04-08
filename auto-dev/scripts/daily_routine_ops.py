#!/usr/bin/env python3
"""
Daily Routine Operations - 日常自动化脚本
支持早间简报、任务管理、晚间复盘、周回顾

用法:
  python daily_routine_ops.py morning-brief
  python daily_routine_ops.py add-task <title> [--priority N] [--project NAME]
  python daily_routine_ops.py list-tasks [--status STATUS]
  python daily_routine_ops.py complete-task <task_id>
  python daily_routine_ops.py evening-review
  python daily_routine_ops.py weekly-review
"""

import os
import sys
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict

# 配置
AUTO_DEV_BASE = Path(__file__).parent.parent
MEMORY_BASE = AUTO_DEV_BASE / "memory"
TASKS_DIR = AUTO_DEV_BASE / "tasks"

# 层级
LAYERS = {
    "episodic": MEMORY_BASE / "episodic",
    "working": MEMORY_BASE / "working",
    "longterm": MEMORY_BASE / "longterm"
}


class DailyRoutineOps:
    def __init__(self):
        self.memory_base = MEMORY_BASE

    def get_recent_logs(self, days: int = 1) -> List[Dict]:
        """获取最近的日志"""
        logs = []
        daily_logs_dir = LAYERS["episodic"] / "daily-logs"

        if not daily_logs_dir.exists():
            return logs

        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            log_file = daily_logs_dir / f"{date}.md"

            if log_file.exists():
                with open(log_file, "r", encoding="utf-8") as f:
                    content = f.read()

                logs.append({
                    "date": date,
                    "content": content,
                    "done": self._extract_section(content, "今日完成"),
                    "todo": self._extract_section(content, "明日计划"),
                    "decisions": self._extract_section(content, "决策记录")
                })

        return logs

    def _extract_section(self, content: str, section_name: str) -> List[str]:
        """提取日志段落"""
        lines = content.split("\n")
        section_lines = []
        in_section = False

        for line in lines:
            if line.startswith("## ") and section_name in line:
                in_section = True
            elif in_section and line.startswith("## "):
                break
            elif in_section and line.strip().startswith("- ["):
                section_lines.append(line.strip())

        return section_lines

    def get_tasks(self, status: str = None) -> List[Dict]:
        """获取任务列表"""
        tasks = []
        tasks_dir = LAYERS["working"] / "tasks"

        if not tasks_dir.exists():
            return tasks

        for task_file in tasks_dir.rglob("*.md"):
            if task_file.name == "README.md":
                continue

            try:
                with open(task_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # 提取任务信息
                task = {
                    "id": task_file.stem[:15],
                    "title": self._extract_title(content),
                    "status": self._extract_field(content, "Status"),
                    "priority": self._extract_priority(content),
                    "file": str(task_file.relative_to(self.memory_base))
                }

                if status and task["status"] != status:
                    continue

                tasks.append(task)
            except:
                continue

        # 按优先级排序
        tasks.sort(key=lambda x: x["priority"], reverse=True)
        return tasks

    def _extract_title(self, content: str) -> str:
        """提取标题"""
        for line in content.split("\n"):
            if line.startswith("# Task:") or line.startswith("## Task:"):
                return line.split(":", 1)[1].strip()
        return "Untitled"

    def _extract_field(self, content: str, field: str) -> str:
        """提取字段"""
        for line in content.split("\n"):
            if line.startswith(f"- {field}:"):
                return line.split(":", 1)[1].strip()
        return "unknown"

    def _extract_priority(self, content: str) -> int:
        """提取优先级"""
        for line in content.split("\n"):
            if line.startswith("- Priority:"):
                try:
                    prio_str = line.split("(")[1].split(")")[0]
                    return int(prio_str)
                except:
                    pass
        return 5

    def morning_brief(self) -> str:
        """生成早间简报"""
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday_logs = self.get_recent_logs(1)
        tasks = self.get_tasks()

        # 分类任务
        pending = [t for t in tasks if t["status"] in ["pending", "in_progress"]]
        high_priority = [t for t in pending if t["priority"] >= 8]
        medium_priority = [t for t in pending if 5 <= t["priority"] < 8]
        low_priority = [t for t in pending if t["priority"] < 5]

        lines = [f"## 🌅 早间简报 {today}", ""]

        # 昨日完成
        lines.append("### 昨日完成")
        if yesterday_logs and yesterday_logs[0].get("done"):
            for item in yesterday_logs[0]["done"]:
                lines.append(f"- {item}")
        else:
            lines.append("- 无记录")
        lines.append("")

        # 今日待办
        lines.append("### 今日待办")
        if high_priority:
            lines.append("🔴 高优先级")
            for t in high_priority[:5]:
                lines.append(f"- [ ] {t['title']}")
        if medium_priority:
            lines.append("🟡 中优先级")
            for t in medium_priority[:5]:
                lines.append(f"- [ ] {t['title']}")
        if low_priority:
            lines.append("🟢 低优先级")
            for t in low_priority[:5]:
                lines.append(f"- [ ] {t['title']}")

        if not pending:
            lines.append("- 无待办任务")

        lines.append("")
        lines.append(f"---")
        lines.append(f"*生成时间: {datetime.now().strftime('%H:%M')}*")

        return "\n".join(lines)

    def add_task(self, title: str, priority: int = 5, project: str = None) -> str:
        """添加任务"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        date = datetime.now().strftime("%Y%m%d")

        # 生成ID
        tasks_dir = LAYERS["working"] / "tasks"
        tasks_dir.mkdir(exist_ok=True)

        existing = len(list(tasks_dir.glob("*.md")))
        task_id = f"TASK-{date}-{existing + 1:03d}"

        # 优先级标签
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
- Type: feature
- Priority: {priority_label} ({priority})
- Status: pending
- Owner: unassigned
- Created: {now}
- Updated: {now}

## 描述

{title}

## 验收标准

- [ ] 标准1
- [ ] 标准2

## 关联

- Project: {project or "未分类"}
- Parent:
- Children:
- Related:
"""
        filepath = tasks_dir / f"{task_id}.md"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        return task_id

    def complete_task(self, task_id: str) -> bool:
        """完成任务"""
        tasks_dir = LAYERS["working"] / "tasks"

        task_file = None
        for f in tasks_dir.rglob("*.md"):
            if task_id in f.stem:
                task_file = f
                break

        if not task_file:
            print(f"❌ 未找到任务: {task_id}")
            return False

        with open(task_file, "r", encoding="utf-8") as f:
            content = f.read()

        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        lines = content.split("\n")

        for i, line in enumerate(lines):
            if line.startswith("- Status:"):
                lines[i] = f"- Status: completed"
            elif line.startswith("- Updated:"):
                lines[i] = f"- Updated: {now}"

        new_content = "\n".join(lines)

        # 移动到completed子目录
        completed_dir = tasks_dir / "completed"
        completed_dir.mkdir(exist_ok=True)

        new_path = completed_dir / task_file.name
        with open(new_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        task_file.unlink()

        print(f"✅ 任务已完成: {task_id}")
        return True

    def evening_review(self) -> str:
        """生成晚间复盘"""
        today = datetime.now().strftime("%Y-%m-%d")
        today_logs = self.get_recent_logs(1)
        pending_tasks = self.get_tasks("pending")

        lines = [f"## 🌙 晚间复盘 {today}", ""]

        # 今日完成
        lines.append("### 今日完成")
        if today_logs and today_logs[0].get("done"):
            for item in today_logs[0]["done"]:
                lines.append(f"- {item}")
        else:
            lines.append("- 无记录")
        lines.append("")

        # 明日计划
        lines.append("### 明日待办")
        if today_logs and today_logs[0].get("todo"):
            for item in today_logs[0]["todo"]:
                lines.append(f"- {item}")
        else:
            # 从pending任务中结转
            if pending_tasks:
                lines.append("(从待办任务结转)")
                for t in pending_tasks[:5]:
                    lines.append(f"- [ ] {t['title']}")

        lines.append("")
        lines.append(f"---")
        lines.append(f"*生成时间: {datetime.now().strftime('%H:%M')}*")

        return "\n".join(lines)

    def weekly_review(self) -> str:
        """生成周回顾"""
        week_num = datetime.now().isocalendar()[1]
        week_start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

        week_logs = self.get_recent_logs(7)
        completed_tasks = self.get_tasks("completed")

        lines = [f"## 📅 周回顾 第{week_num}周", ""]
        lines.append(f"**周期**: {week_start} ~ {datetime.now().strftime('%Y-%m-%d')}")
        lines.append("")

        # 本周完成
        lines.append("### 本周完成")
        done_count = 0
        for log in week_logs:
            if log.get("done"):
                done_count += len(log["done"])
                for item in log["done"]:
                    lines.append(f"- {item}")

        if done_count == 0:
            lines.append("- 无完成记录")

        lines.append("")

        # 决策记录
        lines.append("### 本周决策")
        decisions = []
        for log in week_logs:
            decisions.extend(log.get("decisions", []))

        if decisions:
            for d in decisions:
                lines.append(f"- {d}")
        else:
            lines.append("- 无决策记录")

        lines.append("")

        # 下周计划
        lines.append("### 下周计划")
        lines.append("1. 优先事项1")
        lines.append("2. 优先事项2")
        lines.append("3. 优先事项3")

        lines.append("")
        lines.append(f"---")
        lines.append(f"*生成时间: {datetime.now().strftime('%H:%M')}*")

        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Daily Routine Operations - 日常自动化")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # morning-brief
    subparsers.add_parser("morning-brief", help="早间简报")

    # add-task
    add_parser = subparsers.add_parser("add-task", help="添加任务")
    add_parser.add_argument("title", help="任务标题")
    add_parser.add_argument("--priority", "-p", type=int, default=5, help="优先级1-10")
    add_parser.add_argument("--project", help="所属项目")

    # list-tasks
    list_parser = subparsers.add_parser("list-tasks", help="列出任务")
    list_parser.add_argument("--status", "-s", help="状态筛选")

    # complete-task
    complete_parser = subparsers.add_parser("complete-task", help="完成任务")
    complete_parser.add_argument("task_id", help="任务ID")

    # evening-review
    subparsers.add_parser("evening-review", help="晚间复盘")

    # weekly-review
    subparsers.add_parser("weekly-review", help="周回顾")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    ops = DailyRoutineOps()

    if args.command == "morning-brief":
        print(ops.morning_brief())

    elif args.command == "add-task":
        task_id = ops.add_task(args.title, args.priority, args.project)
        print(f"✅ 任务已添加: {task_id}")

    elif args.command == "list-tasks":
        tasks = ops.get_tasks(args.status)
        if tasks:
            print(f"\n📋 任务列表 (共 {len(tasks)} 条)")
            print("=" * 70)
            for t in tasks:
                prio_icon = "🔴" if t["priority"] >= 8 else "🟡" if t["priority"] >= 5 else "🟢"
                print(f"{prio_icon} {t['id']} | {t['title'][:40]}")
                print(f"   状态: {t['status']} | 优先级: P{t['priority']}")
        else:
            print("暂无任务")

    elif args.command == "complete-task":
        ops.complete_task(args.task_id)

    elif args.command == "evening-review":
        print(ops.evening_review())

    elif args.command == "weekly-review":
        print(ops.weekly_review())


if __name__ == "__main__":
    main()
