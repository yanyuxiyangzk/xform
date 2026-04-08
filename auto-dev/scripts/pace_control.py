#!/usr/bin/env python3
"""
Pace Control - 速率控制模块

实现5小时滚动窗口任务限制，防止API过度使用

功能:
- 5小时滚动窗口任务数限制
- 任务超时控制
- 30分钟冷却间隔
- 渐进式冷却机制

用法:
  python pace_control.py check <task_id>     # 检查是否可以启动任务
  python pace_control.py start <task_id>     # 记录任务开始
  python pace_control.py end <task_id>      # 记录任务结束
  python pace_control.py stats              # 查看当前状态
  python pace_control.py reset               # 重置所有状态
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Tuple

# 配置
AUTO_DEV_BASE = Path(__file__).parent.parent
STATE_DIR = AUTO_DEV_BASE / "self-improving"
STATE_FILE = STATE_DIR / "pace-state.json"

# 默认配置
DEFAULT_ROLLING_WINDOW_HOURS = 5
DEFAULT_MAX_TASKS_IN_WINDOW = 3
DEFAULT_TASK_TIMEOUT_HOURS = 8
DEFAULT_COOLDOWN_MINUTES = 30


class PaceController:
    """速率控制器"""

    def __init__(self,
                 rolling_window_hours: int = DEFAULT_ROLLING_WINDOW_HOURS,
                 max_tasks_in_window: int = DEFAULT_MAX_TASKS_IN_WINDOW,
                 task_timeout_hours: int = DEFAULT_TASK_TIMEOUT_HOURS,
                 cooldown_minutes: int = DEFAULT_COOLDOWN_MINUTES):
        self.rolling_window_hours = rolling_window_hours
        self.max_tasks_in_window = max_tasks_in_window
        self.task_timeout_hours = task_timeout_hours
        self.cooldown_minutes = cooldown_minutes

        STATE_DIR.mkdir(exist_ok=True)
        self.state = self._load_state()

    def _load_state(self) -> Dict:
        """加载状态"""
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass

        return {
            "active_tasks": {},
            "completed_tasks": [],
            "last_task_end_time": None,
            "total_tasks_started": 0
        }

    def _save_state(self):
        """保存状态"""
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    def _now(self) -> str:
        return datetime.now().isoformat()

    def _parse_time(self, iso_str: str) -> datetime:
        return datetime.fromisoformat(iso_str)

    def _get_window_start(self) -> datetime:
        return datetime.now() - timedelta(hours=self.rolling_window_hours)

    def _cleanup_stale_tasks(self):
        """清理超时任务"""
        now = datetime.now()
        timeout_threshold = timedelta(hours=self.task_timeout_hours)

        stale_tasks = []
        for task_id, info in self.state["active_tasks"].items():
            start_time = self._parse_time(info["start_time"])
            if now - start_time > timeout_threshold:
                stale_tasks.append(task_id)

        for task_id in stale_tasks:
            print(f"[WARN] Task {task_id} timed out, removing from active")
            self.state["active_tasks"].pop(task_id, None)

    def _get_tasks_in_window(self) -> List[Dict]:
        """获取滚动窗口内的任务"""
        window_start = self._get_window_start()
        recent_tasks = []

        for task_info in self.state.get("completed_tasks", []):
            end_time = self._parse_time(task_info["end_time"])
            if end_time > window_start:
                recent_tasks.append(task_info)

        return recent_tasks

    def can_start_task(self, task_id: str) -> Tuple[bool, str]:
        """
        检查是否可以启动新任务

        Returns:
            (can_start: bool, reason: str)
        """
        # 清理超时任务
        self._cleanup_stale_tasks()

        # 检查任务是否已在运行
        if task_id in self.state["active_tasks"]:
            return True, "Task already running"

        # 检查窗口内任务数
        tasks_in_window = self._get_tasks_in_window()
        active_in_window = len([t for t in tasks_in_window if t.get("status") != "failed"])

        if active_in_window >= self.max_tasks_in_window:
            oldest = min(tasks_in_window, key=lambda x: x["end_time"])
            oldest_end = self._parse_time(oldest["end_time"])
            cooldown_until = oldest_end + timedelta(minutes=self.cooldown_minutes)
            return False, f"Max tasks ({self.max_tasks_in_window}) reached in {self.rolling_window_hours}h window. Cooldown until {cooldown_until.strftime('%H:%M')}"

        # 检查冷却期
        if self.state.get("last_task_end_time"):
            last_end = self._parse_time(self.state["last_task_end_time"])
            cooldown_until = last_end + timedelta(minutes=self.cooldown_minutes)
            if datetime.now() < cooldown_until:
                remaining = (cooldown_until - datetime.now()).seconds // 60
                return False, f"In cooldown period. {remaining} minutes remaining"

        return True, "OK"

    def start_task(self, task_id: str, metadata: Dict = None) -> Tuple[bool, str]:
        """
        记录任务开始

        Returns:
            (success: bool, message: str)
        """
        can_start, reason = self.can_start_task(task_id)

        if not can_start:
            return False, reason

        self.state["active_tasks"][task_id] = {
            "task_id": task_id,
            "start_time": self._now(),
            "metadata": metadata or {}
        }
        self.state["total_tasks_started"] += 1
        self._save_state()

        return True, f"Task {task_id} started"

    def end_task(self, task_id: str, status: str = "completed", metadata: Dict = None):
        """
        记录任务结束

        Args:
            task_id: 任务ID
            status: completed / failed / cancelled
            metadata: 额外信息
        """
        if task_id not in self.state["active_tasks"]:
            print(f"[WARN] Task {task_id} not found in active tasks")
            return

        task_info = self.state["active_tasks"].pop(task_id)
        task_info["end_time"] = self._now()
        task_info["status"] = status
        task_info["metadata"] = {**(task_info.get("metadata") or {}), **(metadata or {})}

        # 计算持续时间
        start_time = self._parse_time(task_info["start_time"])
        end_time = self._parse_time(task_info["end_time"])
        task_info["duration_minutes"] = (end_time - start_time).total_seconds() / 60

        # 添加到已完成任务列表
        self.state["completed_tasks"].append(task_info)
        self.state["last_task_end_time"] = task_info["end_time"]

        # 限制历史记录数量（保留最近100条）
        if len(self.state["completed_tasks"]) > 100:
            self.state["completed_tasks"] = self.state["completed_tasks"][-100:]

        self._save_state()

        print(f"[OK] Task {task_id} ended with status: {status}")

    def get_stats(self) -> Dict:
        """获取统计数据"""
        self._cleanup_stale_tasks()

        tasks_in_window = self._get_tasks_in_window()
        window_start = self._get_window_start()

        return {
            "active_tasks": len(self.state["active_tasks"]),
            "tasks_in_window": len(tasks_in_window),
            "max_tasks_in_window": self.max_tasks_in_window,
            "window_start": window_start.isoformat(),
            "total_completed": len(self.state["completed_tasks"]),
            "total_started": self.state.get("total_tasks_started", 0),
            "last_task_end": self.state.get("last_task_end_time"),
            "active_task_ids": list(self.state["active_tasks"].keys()),
            "cooldown_minutes": self.cooldown_minutes
        }

    def reset(self):
        """重置所有状态"""
        self.state = {
            "active_tasks": {},
            "completed_tasks": [],
            "last_task_end_time": None,
            "total_tasks_started": 0
        }
        self._save_state()
        print("[OK] Pace control state reset")


def main():
    parser = argparse.ArgumentParser(description="Pace Control - 速率控制器")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # check命令
    check_parser = subparsers.add_parser("check", help="检查是否可以启动任务")
    check_parser.add_argument("task_id", help="任务ID")

    # start命令
    start_parser = subparsers.add_parser("start", help="记录任务开始")
    start_parser.add_argument("task_id", help="任务ID")

    # end命令
    end_parser = subparsers.add_parser("end", help="记录任务结束")
    end_parser.add_argument("task_id", help="任务ID")
    end_parser.add_argument("--status", "-s", default="completed",
                           choices=["completed", "failed", "cancelled"],
                           help="任务状态")

    # stats命令
    subparsers.add_parser("stats", help="查看当前状态")

    # reset命令
    subparsers.add_parser("reset", help="重置所有状态")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    controller = PaceController()

    if args.command == "check":
        can_start, reason = controller.can_start_task(args.task_id)
        if can_start:
            print(f"[OK] {reason}")
        else:
            print(f"[BLOCKED] {reason}")
        sys.exit(0 if can_start else 1)

    elif args.command == "start":
        success, message = controller.start_task(args.task_id)
        print(f"[{'OK' if success else 'ERROR'}] {message}")
        sys.exit(0 if success else 1)

    elif args.command == "end":
        controller.end_task(args.task_id, args.status)

    elif args.command == "stats":
        stats = controller.get_stats()
        print("\n[PACE CONTROL STATS]")
        print("=" * 50)
        print(f"Active Tasks:     {stats['active_tasks']}")
        print(f"Tasks in Window:  {stats['tasks_in_window']}/{stats['max_tasks_in_window']}")
        print(f"Total Completed: {stats['total_completed']}")
        print(f"Total Started:   {stats['total_started']}")
        print(f"Last Task End:   {stats['last_task_end'] or 'none'}")
        print(f"Cooldown:        {stats['cooldown_minutes']} min")
        print(f"\nActive Task IDs:")
        for tid in stats['active_task_ids']:
            print(f"  - {tid}")
        print(f"\nWindow Start: {stats['window_start']}")

    elif args.command == "reset":
        controller.reset()


if __name__ == "__main__":
    main()
