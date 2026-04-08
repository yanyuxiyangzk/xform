#!/usr/bin/env python3
"""
Checkpoint Operations - 任务持久化模块

实现断点保存和恢复，支持24/7无人值守运行

功能:
- 定期保存checkpoint状态
- 重启后自动恢复
- 任务状态追踪
- 错误队列管理

用法:
  python checkpoint_ops.py save                    # 保存当前状态
  python checkpoint_ops.py load                    # 加载状态
  python checkpoint_ops.py recover                 # 恢复到checkpoint
  python checkpoint_ops.py status                  # 查看状态
  python checkpoint_ops.py clear                   # 清除checkpoint
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict

# 配置
AUTO_DEV_BASE = Path(__file__).parent.parent
STATE_DIR = AUTO_DEV_BASE / "self-improving"
CHECKPOINT_FILE = STATE_DIR / "checkpoint.json"

# 默认配置
DEFAULT_CHECKPOINT_INTERVAL_MINUTES = 10
DEFAULT_MAX_CHECKPOINT_AGE_HOURS = 24


class CheckpointOps:
    """Checkpoint管理器"""

    def __init__(self, max_checkpoint_age_hours: int = DEFAULT_MAX_CHECKPOINT_AGE_HOURS):
        self.max_checkpoint_age_hours = max_checkpoint_age_hours
        STATE_DIR.mkdir(exist_ok=True)

    def _now(self) -> str:
        return datetime.now().isoformat()

    def _parse_time(self, iso_str: str) -> datetime:
        return datetime.fromisoformat(iso_str)

    def get_default_checkpoint(self) -> Dict:
        """获取默认checkpoint结构"""
        return {
            "version": "1.0",
            "last_heartbeat": None,
            "active_pipelines": [],
            "pipeline_states": {},
            "pending_tasks": [],
            "error_queue": [],
            "stats": {
                "total_runs": 0,
                "total_tasks_completed": 0,
                "total_errors": 0
            }
        }

    def load_checkpoint(self) -> Optional[Dict]:
        """加载checkpoint"""
        if not CHECKPOINT_FILE.exists():
            return None

        try:
            with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"[WARN] Failed to load checkpoint: {e}")
            return None

    def save_checkpoint(self, data: Dict = None):
        """
        保存checkpoint

        Args:
            data: checkpoint数据，如不提供则从当前运行状态构建
        """
        if data is None:
            data = self.build_checkpoint()

        data["last_heartbeat"] = self._now()

        with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"[OK] Checkpoint saved at {data['last_heartbeat']}")

    def build_checkpoint(self) -> Dict:
        """从当前状态构建checkpoint"""
        checkpoint = self.get_default_checkpoint()

        # 读取tasks目录获取活跃pipeline
        tasks_dir = AUTO_DEV_BASE / "tasks"
        pipeline_dir = tasks_dir / "pipeline"

        if pipeline_dir.exists():
            # 获取最新的pipeline
            pipelines = sorted(pipeline_dir.glob("PIPELINE-*"), key=lambda x: x.name, reverse=True)
            if pipelines:
                checkpoint["active_pipelines"] = [p.name for p in pipelines[:5]]

        # 读取in_progress任务
        in_progress_file = tasks_dir / "in_progress.md"
        if in_progress_file.exists():
            try:
                content = in_progress_file.read_text(encoding="utf-8")
                # 简单解析任务列表
                lines = [l.strip() for l in content.split("\n") if l.strip().startswith("- [ ]")]
                checkpoint["pending_tasks"] = [l[4:].strip() for l in lines[:10]]
            except Exception:
                pass

        # 读取pace control状态
        pace_state_file = STATE_DIR / "pace-state.json"
        if pace_state_file.exists():
            try:
                with open(pace_state_file, "r", encoding="utf-8") as f:
                    pace_state = json.load(f)
                    checkpoint["stats"]["total_runs"] = pace_state.get("total_tasks_started", 0)
            except Exception:
                pass

        return checkpoint

    def is_recovery_needed(self) -> bool:
        """检查是否需要恢复"""
        checkpoint = self.load_checkpoint()

        if not checkpoint:
            return False

        # 检查是否有过期checkpoint
        last_heartbeat = checkpoint.get("last_heartbeat")
        if not last_heartbeat:
            return False

        last_time = self._parse_time(last_heartbeat)
        age = datetime.now() - last_time

        if age > timedelta(hours=self.max_checkpoint_age_hours):
            print(f"[INFO] Checkpoint is {age.total_seconds()/3600:.1f} hours old, too old to recover")
            return False

        # 检查是否有活跃pipeline
        active = checkpoint.get("active_pipelines", [])
        pending = checkpoint.get("pending_tasks", [])

        if active or pending:
            print(f"[INFO] Found active state: {len(active)} pipelines, {len(pending)} pending tasks")
            return True

        return False

    def recover_from_checkpoint(self) -> Optional[Dict]:
        """
        从checkpoint恢复

        Returns:
            checkpoint数据，如恢复失败返回None
        """
        checkpoint = self.load_checkpoint()

        if not checkpoint:
            print("[WARN] No checkpoint found to recover from")
            return None

        print("\n[RECOVERY] Restoring from checkpoint...")
        print(f"  Last heartbeat: {checkpoint.get('last_heartbeat', 'unknown')}")
        print(f"  Active pipelines: {len(checkpoint.get('active_pipelines', []))}")
        print(f"  Pending tasks: {len(checkpoint.get('pending_tasks', []))}")

        # 验证checkpoint完整性
        required_fields = ["version", "last_heartbeat"]
        for field in required_fields:
            if field not in checkpoint:
                print(f"[ERROR] Checkpoint missing required field: {field}")
                return None

        # 更新统计
        checkpoint["stats"]["total_errors"] = checkpoint["stats"].get("total_errors", 0) + 1

        return checkpoint

    def get_status(self) -> Dict:
        """获取状态"""
        checkpoint = self.load_checkpoint()

        if not checkpoint:
            return {
                "exists": False,
                "message": "No checkpoint found"
            }

        last_heartbeat = checkpoint.get("last_heartbeat")
        if last_heartbeat:
            last_time = self._parse_time(last_heartbeat)
            age = datetime.now() - last_time
            age_hours = age.total_seconds() / 3600
        else:
            age_hours = None

        return {
            "exists": True,
            "last_heartbeat": last_heartbeat,
            "age_hours": age_hours,
            "active_pipelines": len(checkpoint.get("active_pipelines", [])),
            "pending_tasks": len(checkpoint.get("pending_tasks", [])),
            "error_queue_size": len(checkpoint.get("error_queue", [])),
            "stats": checkpoint.get("stats", {})
        }

    def clear_checkpoint(self):
        """清除checkpoint"""
        if CHECKPOINT_FILE.exists():
            CHECKPOINT_FILE.unlink()
            print("[OK] Checkpoint cleared")
        else:
            print("[WARN] No checkpoint to clear")

    def add_error_to_queue(self, error: Dict):
        """添加错误到队列"""
        checkpoint = self.load_checkpoint() or self.get_default_checkpoint()

        error_entry = {
            "error": error,
            "time": self._now(),
            "handled": False
        }

        checkpoint["error_queue"].append(error_entry)

        # 限制队列长度
        if len(checkpoint["error_queue"]) > 50:
            checkpoint["error_queue"] = checkpoint["error_queue"][-50:]

        checkpoint["stats"]["total_errors"] = checkpoint["stats"].get("total_errors", 0) + 1

        self.save_checkpoint(checkpoint)

    def get_pending_errors(self) -> List[Dict]:
        """获取未处理的错误"""
        checkpoint = self.load_checkpoint()
        if not checkpoint:
            return []

        errors = checkpoint.get("error_queue", [])
        return [e for e in errors if not e.get("handled", False)]


def main():
    parser = argparse.ArgumentParser(description="Checkpoint Operations - 任务持久化")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # save命令
    subparsers.add_parser("save", help="保存checkpoint")

    # load命令
    subparsers.add_parser("load", help="加载checkpoint")

    # recover命令
    subparsers.add_parser("recover", help="从checkpoint恢复")

    # status命令
    subparsers.add_parser("status", help="查看状态")

    # clear命令
    subparsers.add_parser("clear", help="清除checkpoint")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    ops = CheckpointOps()

    if args.command == "save":
        ops.save_checkpoint()

    elif args.command == "load":
        checkpoint = ops.load_checkpoint()
        if checkpoint:
            print("\n[CHECKPOINT]")
            print("=" * 50)
            print(f"Last heartbeat: {checkpoint.get('last_heartbeat', 'unknown')}")
            print(f"Active pipelines: {checkpoint.get('active_pipelines', [])}")
            print(f"Pending tasks: {checkpoint.get('pending_tasks', [])}")
            print(f"Stats: {checkpoint.get('stats', {})}")
        else:
            print("[WARN] No checkpoint found")

    elif args.command == "recover":
        if ops.is_recovery_needed():
            checkpoint = ops.recover_from_checkpoint()
            if checkpoint:
                print("\n[OK] Recovery successful")
                print(f"Active pipelines: {checkpoint.get('active_pipelines', [])}")
        else:
            print("[OK] No recovery needed")

    elif args.command == "status":
        status = ops.get_status()
        print("\n[CHECKPOINT STATUS]")
        print("=" * 50)
        if status["exists"]:
            print(f"Exists:        Yes")
            print(f"Last heartbeat: {status['last_heartbeat']}")
            print(f"Age:           {status['age_hours']:.1f} hours" if status['age_hours'] else "Age:           unknown")
            print(f"Active pipelines: {status['active_pipelines']}")
            print(f"Pending tasks:   {status['pending_tasks']}")
            print(f"Error queue:     {status['error_queue_size']}")
            print(f"Stats: {json.dumps(status['stats'], indent=2)}")
        else:
            print(f"Exists: No")
            print(f"Message: {status['message']}")

    elif args.command == "clear":
        ops.clear_checkpoint()


if __name__ == "__main__":
    main()
