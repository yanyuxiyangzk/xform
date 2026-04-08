#!/usr/bin/env python3
"""
Model Escalation - 模型升级模块

实现Haiku→Sonnet自动升级机制

功能:
- 监控错误次数触发升级
- 检测stuck状态触发升级
- 任务超时触发升级
- 支持自定义阈值

用法:
  python model_escalation.py should-escalate <task_id>   # 检查是否应升级
  python model_escalation.py escalate <task_id>         # 执行升级
  python model_escalation.py status <task_id>           # 查看任务模型状态
  python model_escalation.py reset <task_id>            # 重置任务状态
"""

import os
import sys
import json
import argparse
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Tuple

# 配置
AUTO_DEV_BASE = Path(__file__).parent.parent
STATE_DIR = AUTO_DEV_BASE / "self-improving"
STATE_FILE = STATE_DIR / "model-escalation-state.json"

# 模型定义
MODELS = {
    "haiku": "claude-3-haiku-4-20250514",
    "sonnet": "claude-3-5-sonnet-4-20250514",
    "opus": "claude-opus-4-6-20250514"
}

# 默认配置
DEFAULT_ESCALATION_THRESHOLD_ERRORS = 3
DEFAULT_ESCALATION_THRESHOLD_STUCK = 1
DEFAULT_ESCALATION_THRESHOLD_HOURS = 4


class ModelEscalation:
    """模型升级控制器"""

    def __init__(self,
                 error_threshold: int = DEFAULT_ESCALATION_THRESHOLD_ERRORS,
                 stuck_threshold: int = DEFAULT_ESCALATION_THRESHOLD_STUCK,
                 timeout_hours: int = DEFAULT_ESCALATION_THRESHOLD_HOURS):
        self.error_threshold = error_threshold
        self.stuck_threshold = stuck_threshold
        self.timeout_hours = timeout_hours

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

        return {"tasks": {}, "default_model": "haiku"}

    def _save_state(self):
        """保存状态"""
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    def _now(self) -> str:
        return datetime.now().isoformat()

    def _get_task_state(self, task_id: str) -> Dict:
        """获取任务状态"""
        if task_id not in self.state["tasks"]:
            self.state["tasks"][task_id] = {
                "task_id": task_id,
                "current_model": self.state.get("default_model", "haiku"),
                "error_count": 0,
                "is_stuck": False,
                "start_time": self._now(),
                "last_error_time": None,
                "escalated_at": None,
                "escalation_reason": None
            }
        return self.state["tasks"][task_id]

    def record_error(self, task_id: str, error_msg: str = None) -> Tuple[bool, str]:
        """
        记录错误

        Returns:
            (should_escalate: bool, reason: str)
        """
        task_state = self._get_task_state(task_id)
        task_state["error_count"] += 1
        task_state["last_error_time"] = self._now()

        # 检查是否应升级
        if task_state["error_count"] >= self.error_threshold:
            if self.state["tasks"][task_id]["current_model"] == "haiku":
                return True, f"Error count ({task_state['error_count']}) exceeded threshold ({self.error_threshold})"

        return False, ""

    def record_stuck(self, task_id: str) -> Tuple[bool, str]:
        """
        记录卡死状态

        Returns:
            (should_escalate: bool, reason: str)
        """
        task_state = self._get_task_state(task_id)

        if not task_state["is_stuck"]:
            task_state["is_stuck"] = True
            stuck_count = sum(1 for t in self.state["tasks"].values() if t.get("is_stuck"))
            if stuck_count >= self.stuck_threshold:
                if task_state["current_model"] == "haiku":
                    return True, f"Stuck tasks ({stuck_count}) exceeded threshold ({self.stuck_threshold})"

        return False, ""

    def record_timeout(self, task_id: str) -> Tuple[bool, str]:
        """
        记录超时

        Returns:
            (should_escalate: bool, reason: str)
        """
        task_state = self._get_task_state(task_id)
        start_time = datetime.fromisoformat(task_state["start_time"])
        elapsed = datetime.now() - start_time

        if elapsed.total_seconds() / 3600 >= self.timeout_hours:
            if task_state["current_model"] == "haiku":
                return True, f"Task timeout ({elapsed.total_seconds()/3600:.1f}h) exceeded {self.timeout_hours}h"

        return False, ""

    def should_escalate(self, task_id: str) -> Tuple[bool, str]:
        """
        检查是否应升级模型

        Returns:
            (should_escalate: bool, reason: str)
        """
        task_state = self._get_task_state(task_id)

        # 如果已经是最高模型，不再升级
        if task_state["current_model"] not in ["haiku"]:
            return False, ""

        # 检查各种触发条件
        checks = [
            (task_state["error_count"] >= self.error_threshold,
             f"Error count ({task_state['error_count']}) >= threshold ({self.error_threshold})"),
            (task_state["is_stuck"],
             "Task is stuck"),
            (self._check_timeout(task_state),
             f"Task timeout exceeded {self.timeout_hours}h")
        ]

        for condition, reason in checks:
            if condition:
                return True, reason

        return False, ""

    def _check_timeout(self, task_state: Dict) -> bool:
        """检查是否超时"""
        start_time_str = task_state.get("start_time")
        if not start_time_str:
            return False
        try:
            start_time = datetime.fromisoformat(start_time_str)
            elapsed = datetime.now() - start_time
            return elapsed.total_seconds() / 3600 >= self.timeout_hours
        except Exception:
            return False

    def escalate(self, task_id: str) -> Tuple[bool, str]:
        """
        执行模型升级

        Returns:
            (success: bool, message: str)
        """
        task_state = self._get_task_state(task_id)

        current = task_state["current_model"]

        # Haiku -> Sonnet
        if current == "haiku":
            task_state["current_model"] = "sonnet"
            task_state["escalated_at"] = self._now()
            task_state["escalation_reason"] = "error_threshold"
            self._save_state()
            return True, f"Escalated {task_id}: haiku -> sonnet"

        # Sonnet -> Opus (可选)
        elif current == "sonnet":
            task_state["current_model"] = "opus"
            task_state["escalated_at"] = self._now()
            self._save_state()
            return True, f"Escalated {task_id}: sonnet -> opus"

        return False, f"Cannot escalate further: already at {current}"

    def get_current_model(self, task_id: str) -> str:
        """获取当前模型"""
        return self._get_task_state(task_id)["current_model"]

    def get_model_name(self, model_key: str) -> str:
        """获取完整模型名"""
        return MODELS.get(model_key, model_key)

    def get_stats(self) -> Dict:
        """获取统计"""
        haiku_count = sum(1 for t in self.state["tasks"].values() if t.get("current_model") == "haiku")
        sonnet_count = sum(1 for t in self.state["tasks"].values() if t.get("current_model") == "sonnet")
        opus_count = sum(1 for t in self.state["tasks"].values() if t.get("current_model") == "opus")
        stuck_count = sum(1 for t in self.state["tasks"].values() if t.get("is_stuck"))

        return {
            "total_tasks": len(self.state["tasks"]),
            "by_model": {"haiku": haiku_count, "sonnet": sonnet_count, "opus": opus_count},
            "stuck_tasks": stuck_count,
            "default_model": self.state.get("default_model", "haiku")
        }

    def reset_task(self, task_id: str):
        """重置任务状态"""
        if task_id in self.state["tasks"]:
            del self.state["tasks"][task_id]
            self._save_state()
            print(f"[OK] Reset model state for {task_id}")

    def reset_all(self):
        """重置所有状态"""
        self.state = {"tasks": {}, "default_model": "haiku"}
        self._save_state()
        print("[OK] Reset all model escalation state")


def main():
    parser = argparse.ArgumentParser(description="Model Escalation - 模型升级控制")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # should-escalate命令
    check_parser = subparsers.add_parser("should-escalate", help="检查是否应升级")
    check_parser.add_argument("task_id", help="任务ID")

    # escalate命令
    esc_parser = subparsers.add_parser("escalate", help="执行升级")
    esc_parser.add_argument("task_id", help="任务ID")

    # status命令
    status_parser = subparsers.add_parser("status", help="查看任务状态")
    status_parser.add_argument("task_id", nargs="?", help="任务ID（不指定则查看全部）")

    # reset命令
    reset_parser = subparsers.add_parser("reset", help="重置状态")
    reset_parser.add_argument("task_id", nargs="?", help="任务ID（不指定则重置所有）")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    controller = ModelEscalation()

    if args.command == "should-escalate":
        should, reason = controller.should_escalate(args.task_id)
        if should:
            print(f"[ESCALATE] Yes: {reason}")
        else:
            print(f"[OK] No: {reason or 'No escalation needed'}")
        sys.exit(1 if should else 0)

    elif args.command == "escalate":
        success, msg = controller.escalate(args.task_id)
        print(f"[{'OK' if success else 'FAIL'}] {msg}")
        sys.exit(0 if success else 1)

    elif args.command == "status":
        if args.task_id:
            state = controller._get_task_state(args.task_id)
            print(f"\n[MODEL STATUS] {args.task_id}")
            print("=" * 50)
            print(f"Current model:    {state['current_model']}")
            print(f"Full model name:   {controller.get_model_name(state['current_model'])}")
            print(f"Error count:       {state['error_count']}")
            print(f"Is stuck:          {state['is_stuck']}")
            print(f"Start time:        {state['start_time']}")
            print(f"Escalated at:      {state.get('escalated_at') or 'not escalated'}")
            print(f"Escalation reason: {state.get('escalation_reason') or 'N/A'}")
        else:
            stats = controller.get_stats()
            print(f"\n[MODEL ESCALATION STATS]")
            print("=" * 50)
            print(f"Total tasks: {stats['total_tasks']}")
            print(f"By model: haiku={stats['by_model']['haiku']}, "
                  f"sonnet={stats['by_model']['sonnet']}, "
                  f"opus={stats['by_model']['opus']}")
            print(f"Stuck tasks: {stats['stuck_tasks']}")
            print(f"Default model: {stats['default_model']}")

    elif args.command == "reset":
        if args.task_id:
            controller.reset_task(args.task_id)
        else:
            controller.reset_all()


if __name__ == "__main__":
    main()
