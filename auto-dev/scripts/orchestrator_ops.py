#!/usr/bin/env python3
"""
Orchestrator Operations - 流水线协调监控脚本
支持状态检查、异常检测、自动触发

用法:
  python orchestrator_ops.py check [--watch]
  python orchestrator_ops.py monitor <pipeline_id>
  python orchestrator_ops.py detect-blocks
  python orchestrator_ops.py auto-trigger <pipeline_id>
  python orchestrator_ops.py health
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
CONFIG_FILE = STATE_DIR / "time-window-config.json"
PIPELINE_DIR = AUTO_DEV_BASE / "tasks" / "pipeline"
MEMORY_DIR = AUTO_DEV_BASE / "memory"

# 阶段超时配置(小时)
STAGE_TIMEOUTS = {
    "requirement": 2,
    "design": 4,
    "development": 8,
    "testing": 4,
    "deployment": 2
}

# 阶段名称
STAGE_NAMES = {
    "requirement": "需求分析",
    "design": "技术设计",
    "development": "开发实现",
    "testing": "测试验证",
    "deployment": "上线部署"
}

# 默认时间窗口配置
DEFAULT_TIME_WINDOW = {
    "enabled": False,
    "work_hours": {
        "start": "09:00",
        "end": "22:00"
    },
    "timezone": "Asia/Shanghai",
    "allow_weekend": True,
    "allow_overnight": False
}


class TimeWindowChecker:
    """时间窗口检查器"""

    def __init__(self):
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """加载配置"""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return DEFAULT_TIME_WINDOW.copy()

    def _save_config(self):
        """保存配置"""
        STATE_DIR.mkdir(exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def is_within_work_hours(self) -> bool:
        """检查当前是否在工作时间内"""
        if not self.config.get("enabled", False):
            return True  # 未启用则总是允许

        now = datetime.now()
        hour = now.hour
        minute = now.minute

        # 解析工作时段
        start_str = self.config.get("work_hours", {}).get("start", "09:00")
        end_str = self.config.get("work_hours", {}).get("end", "22:00")

        try:
            start_hour, start_minute = map(int, start_str.split(":"))
            end_hour, end_minute = map(int, end_str.split(":"))
        except ValueError:
            return True  # 配置错误则允许

        current_minutes = hour * 60 + minute
        start_minutes = start_hour * 60 + start_minute
        end_minutes = end_hour * 60 + end_minute

        within_hours = start_minutes <= current_minutes <= end_minutes

        # 检查周末
        is_weekend = now.weekday() >= 5  # 5=Saturday, 6=Sunday
        if is_weekend and not self.config.get("allow_weekend", True):
            return False

        # 检查深夜
        is_overnight = end_hour == 23 and end_minute == 59
        if is_overnight and self.config.get("allow_overnight", False):
            return True

        return within_hours

    def should_defer_task(self) -> bool:
        """检查是否应延迟任务"""
        if not self.config.get("enabled", False):
            return False

        return not self.is_within_work_hours()

    def get_next_work_time(self) -> Optional[str]:
        """获取下次工作时间"""
        if not self.config.get("enabled", False):
            return None

        now = datetime.now()
        start_str = self.config.get("work_hours", {}).get("start", "09:00")

        try:
            start_hour, start_minute = map(int, start_str.split(":"))
        except ValueError:
            return None

        # 今天的工作开始时间
        today_start = now.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)

        if now < today_start:
            return today_start.strftime("%Y-%m-%d %H:%M")

        # 明天的开始时间
        tomorrow_start = today_start + timedelta(days=1)

        # 跳到下周一如果需要
        if tomorrow_start.weekday() >= 5 and not self.config.get("allow_weekend", True):
            days_until_monday = (7 - tomorrow_start.weekday()) + 1
            tomorrow_start += timedelta(days=days_until_monday)

        return tomorrow_start.strftime("%Y-%m-%d %H:%M")

    def configure(self, enabled: bool = None, start: str = None, end: str = None,
                 allow_weekend: bool = None, allow_overnight: bool = None):
        """配置时间窗口"""
        if enabled is not None:
            self.config["enabled"] = enabled

        if start is not None or end is not None:
            if "work_hours" not in self.config:
                self.config["work_hours"] = {}
            if start is not None:
                self.config["work_hours"]["start"] = start
            if end is not None:
                self.config["work_hours"]["end"] = end

        if allow_weekend is not None:
            self.config["allow_weekend"] = allow_weekend

        if allow_overnight is not None:
            self.config["allow_overnight"] = allow_overnight

        self._save_config()
        print("[OK] Time window configured")
        print(f"  Enabled: {self.config['enabled']}")
        print(f"  Work hours: {self.config['work_hours']['start']} - {self.config['work_hours']['end']}")
        print(f"  Weekend allowed: {self.config.get('allow_weekend', True)}")


class OrchestratorOps:
    def __init__(self):
        self.pipeline_dir = PIPELINE_DIR

    def check_all(self, watch: bool = False) -> Dict:
        """检查所有流水线状态"""
        pipelines = []

        for pipeline_dir in self.pipeline_dir.iterdir():
            if not pipeline_dir.is_dir() or pipeline_dir.name.startswith("."):
                continue

            pipeline_file = pipeline_dir / f"{pipeline_dir.name}.md"
            if not pipeline_file.exists():
                continue

            with open(pipeline_file, "r", encoding="utf-8") as f:
                content = f.read()

            # 解析信息
            info = {
                "id": pipeline_dir.name,
                "title": "",
                "current_stage": "unknown",
                "status": "unknown",
                "start_time": None,
                "issues": []
            }

            for line in content.split("\n"):
                if line.startswith("- 当前阶段:"):
                    info["current_stage"] = line.split(":", 1)[1].strip()
                elif line.startswith("- 状态:"):
                    info["status"] = line.split(":", 1)[1].strip()
                elif line.startswith("### 阶段"):
                    # 检查阶段开始时间
                    for stage_key, stage_name in STAGE_NAMES.items():
                        if stage_key in line.lower():
                            info["start_time"] = self._get_stage_time(content, stage_key, "开始时间")

            # 检测问题
            if info["status"] == "进行中":
                elapsed = self._get_elapsed_hours(info["start_time"])
                timeout = STAGE_TIMEOUTS.get(info["current_stage"], 4)

                if elapsed > timeout:
                    info["issues"].append(f"[WARN] 阶段超时: 已执行{elapsed:.1f}小时，超过{timeout}小时限制")
                elif elapsed > timeout * 0.8:
                    info["issues"].append(f"⏰ 阶段预警: 已执行{elapsed:.1f}小时，接近{timeout}小时限制")

            pipelines.append(info)

        return {
            "check_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "total": len(pipelines),
            "in_progress": len([p for p in pipelines if p["status"] == "进行中"]),
            "completed": len([p for p in pipelines if p["status"] == "已完成"]),
            "pipelines": pipelines
        }

    def _get_stage_time(self, content: str, stage: str, time_type: str) -> Optional[str]:
        """获取阶段时间"""
        lines = content.split("\n")
        capture = False

        for line in lines:
            if stage in line.lower() and "###" in line:
                capture = True
            elif capture and time_type in line:
                time_str = line.split(":", 1)[1].strip()
                if time_str != "-":
                    return time_str
            elif capture and line.startswith("###"):
                break

        return None

    def _get_elapsed_hours(self, start_time_str: Optional[str]) -> float:
        """计算已执行小时数"""
        if not start_time_str or start_time_str == "-":
            return 0

        try:
            start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M")
            elapsed = datetime.now() - start_time
            return elapsed.total_seconds() / 3600
        except:
            return 0

    def monitor(self, pipeline_id: str) -> Dict:
        """监控单个流水线"""
        pipeline_dir = self.pipeline_dir / pipeline_id
        pipeline_file = pipeline_dir / f"{pipeline_id}.md"

        if not pipeline_file.exists():
            return {"error": f"未找到流水线: {pipeline_id}"}

        with open(pipeline_file, "r", encoding="utf-8") as f:
            content = f.read()

        # 解析所有阶段状态
        stages = {}
        current_stage = None

        lines = content.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("### 阶段"):
                for stage_key, stage_name in STAGE_NAMES.items():
                    if stage_key in line.lower():
                        current_stage = stage_key
                        stages[stage_key] = {
                            "name": stage_name,
                            "status": "pending",
                            "start_time": "-",
                            "end_time": "-"
                        }
            elif current_stage and line.startswith("- 状态:"):
                stages[current_stage]["status"] = line.split(":", 1)[1].strip()
            elif current_stage and line.startswith("- 开始时间:"):
                stages[current_stage]["start_time"] = line.split(":", 1)[1].strip()
            elif current_stage and line.startswith("- 完成时间:"):
                stages[current_stage]["end_time"] = line.split(":", 1)[1].strip()

        # 检测阻塞
        blocked = []
        for stage_key, stage_info in stages.items():
            if stage_info["status"] in ["blocked", "failed"]:
                blocked.append({
                    "stage": stage_key,
                    "name": stage_info["name"],
                    "status": stage_info["status"]
                })

        return {
            "id": pipeline_id,
            "stages": stages,
            "blocked": blocked
        }

    def detect_blocks(self) -> List[Dict]:
        """检测所有阻塞任务"""
        blocks = []

        for pipeline_dir in self.pipeline_dir.iterdir():
            if not pipeline_dir.is_dir():
                continue

            pipeline_file = pipeline_dir / f"{pipeline_dir.name}.md"
            if not pipeline_file.exists():
                continue

            with open(pipeline_file, "r", encoding="utf-8") as f:
                content = f.read()

            # 检查阻塞记录
            in_block_section = False
            for line in content.split("\n"):
                if "阻塞记录" in line:
                    in_block_section = True
                elif in_block_section and line.startswith("-"):
                    block_info = line.strip("- ").strip()
                    if block_info and block_info != "无":
                        blocks.append({
                            "pipeline_id": pipeline_dir.name,
                            "issue": block_info
                        })
                elif in_block_section and line.startswith("##"):
                    break

        return blocks

    def auto_trigger_check(self, pipeline_id: str) -> Dict:
        """检查是否可以自动触发下一阶段"""
        result = {
            "pipeline_id": pipeline_id,
            "can_trigger": False,
            "current_stage": None,
            "next_stage": None,
            "reason": ""
        }

        pipeline_dir = self.pipeline_dir / pipeline_id
        pipeline_file = pipeline_dir / f"{pipeline_id}.md"

        if not pipeline_file.exists():
            result["reason"] = "流水线不存在"
            return result

        with open(pipeline_file, "r", encoding="utf-8") as f:
            content = f.read()

        # 解析当前阶段
        current_stage = None
        for line in content.split("\n"):
            if line.startswith("- 当前阶段:"):
                current_stage = line.split(":", 1)[1].strip()
                break

        if not current_stage:
            result["reason"] = "无法确定当前阶段"
            return result

        result["current_stage"] = current_stage

        # 判断下一阶段
        stage_order = ["requirement", "design", "development", "testing", "deployment", "completed"]

        if current_stage == "completed":
            result["reason"] = "流水线已完成"
            return result

        try:
            current_idx = stage_order.index(current_stage)
            next_stage = stage_order[current_idx + 1]
            result["next_stage"] = next_stage
        except ValueError:
            result["reason"] = f"未知阶段: {current_stage}"
            return result

        # 检查交付物是否存在
        deliverables = {
            "requirement": f"{pipeline_id}/01-requirement.md",
            "design": f"{pipeline_id}/02-design.md",
            "development": "代码已提交",
            "testing": f"{pipeline_id}/04-test-report.md",
            "deployment": f"{pipeline_id}/05-deploy-report.md"
        }

        if next_stage in deliverables:
            deliverable = pipeline_dir / deliverables[next_stage].replace(f"{pipeline_id}/", "")

            if next_stage == "development":
                # 检查是否有代码提交
                code_dirs = ["backend", "frontend", "src"]
                has_code = any((pipeline_dir / d).exists() for d in code_dirs)
                if not has_code:
                    result["reason"] = "等待代码提交"
                    return result
            elif not deliverable.exists():
                result["reason"] = f"等待交付物: {deliverables[next_stage]}"
                return result

        result["can_trigger"] = True
        result["reason"] = f"可以从 {STAGE_NAMES.get(current_stage, current_stage)} → {STAGE_NAMES.get(next_stage, next_stage)}"
        return result

    def health_check(self) -> Dict:
        """健康检查"""
        health = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "healthy",
            "issues": [],
            "metrics": {}
        }

        # 检查目录
        if not self.pipeline_dir.exists():
            health["issues"].append("[ERROR] 流水线目录不存在")
            health["status"] = "error"
            return health

        # 检查记忆目录
        memory_ok = MEMORY_DIR.exists()
        if not memory_ok:
            health["issues"].append("[ERROR] 记忆目录不存在")
            health["status"] = "error"

        # 检查流水线状态
        check_result = self.check_all()

        in_progress = check_result["in_progress"]
        blocked_count = len(self.detect_blocks())

        health["metrics"] = {
            "total_pipelines": check_result["total"],
            "in_progress": in_progress,
            "completed": check_result["completed"],
            "blocked": blocked_count
        }

        if blocked_count > 2:
            health["issues"].append(f"[WARN] 阻塞任务过多: {blocked_count}个")
            health["status"] = "warning"

        if in_progress == 0:
            health["issues"].append("[INFO] 无进行中的任务")

        return health


def main():
    parser = argparse.ArgumentParser(description="Orchestrator Operations - 流水线协调监控")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # check命令
    check_parser = subparsers.add_parser("check", help="检查所有流水线")
    check_parser.add_argument("--watch", "-w", action="store_true", help="持续监控")

    # monitor命令
    monitor_parser = subparsers.add_parser("monitor", help="监控单个流水线")
    monitor_parser.add_argument("pipeline_id", help="流水线ID")

    # detect-blocks命令
    subparsers.add_parser("detect-blocks", help="检测阻塞任务")

    # auto-trigger命令
    auto_trigger_parser = subparsers.add_parser("auto-trigger", help="检查自动触发")
    auto_trigger_parser.add_argument("pipeline_id", help="流水线ID")

    # health命令
    subparsers.add_parser("health", help="健康检查")

    # time-window命令
    tw_parser = subparsers.add_parser("time-window", help="时间窗口控制")
    tw_subparsers = tw_parser.add_subparsers(dest="tw_command", help="子命令")
    tw_subparsers.add_parser("status", help="查看状态")
    tw_subparsers.add_parser("enable", help="启用")
    tw_subparsers.add_parser("disable", help="禁用")
    tw_config_parser = tw_subparsers.add_parser("config", help="配置")
    tw_config_parser.add_argument("--start", help="开始时间 (HH:MM)")
    tw_config_parser.add_argument("--end", help="结束时间 (HH:MM)")
    tw_config_parser.add_argument("--weekend", action="store_true", help="允许周末")
    tw_config_parser.add_argument("--no-weekend", action="store_true", help="禁止周末")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    ops = OrchestratorOps()

    if args.command == "check":
        result = ops.check_all(args.watch)
        print(f"\n[STATS] Orchestrator 检查报告 - {result['check_time']}")
        print("=" * 70)
        print(f"总任务数: {result['total']} | 进行中: {result['in_progress']} | 已完成: {result['completed']}")
        print("")

        for p in result["pipelines"]:
            status_icon = "[RUNNING]" if p["status"] == "进行中" else "[OK]"
            print(f"{status_icon} {p['id']} | {p['title'][:40] if p['title'] else 'Untitled'}")
            print(f"   当前阶段: {STAGE_NAMES.get(p['current_stage'], p['current_stage'])}")
            for issue in p.get("issues", []):
                print(f"   {issue}")

    elif args.command == "monitor":
        result = ops.monitor(args.pipeline_id)
        if "error" in result:
            print(f"[ERROR] {result['error']}")
            return

        print(f"\n[STATS] 流水线监控: {result['id']}")
        print("=" * 70)

        for stage_key, stage_info in result["stages"].items():
            status_icon = "[OK]" if stage_info["status"] == "completed" else "[RUNNING]" if stage_info["status"] == "in_progress" else "[PAUSED]"
            print(f"{status_icon} {stage_info['name']}: {stage_info['status']}")

        if result["blocked"]:
            print("\n[WARN] 阻塞阶段:")
            for b in result["blocked"]:
                print(f"  - {b['name']}: {b['status']}")

    elif args.command == "detect-blocks":
        blocks = ops.detect_blocks()
        if blocks:
            print(f"\n[WARN] 检测到 {len(blocks)} 个阻塞任务:")
            for b in blocks:
                print(f"  - {b['pipeline_id']}: {b['issue']}")
        else:
            print("\n[OK] 未检测到阻塞任务")

    elif args.command == "auto-trigger":
        result = ops.auto_trigger_check(args.pipeline_id)
        print(f"\n[SEARCH] 自动触发检查: {result['pipeline_id']}")
        print("=" * 50)
        print(f"当前阶段: {STAGE_NAMES.get(result['current_stage'], result['current_stage'])}")
        print(f"下一阶段: {STAGE_NAMES.get(result['next_stage'], result['next_stage']) if result['next_stage'] else '无'}")
        print(f"可以触发: {'是 [OK]' if result['can_trigger'] else '否 [FAIL]'}")
        print(f"原因: {result['reason']}")

    elif args.command == "health":
        result = ops.health_check()
        print(f"\n[HEALTH] Orchestrator 健康检查 - {result['timestamp']}")
        print("=" * 50)
        print(f"状态: {result['status'].upper()}")

        print("\n指标:")
        for key, value in result["metrics"].items():
            print(f"  - {key}: {value}")

        if result["issues"]:
            print("\n问题:")
            for issue in result["issues"]:
                print(f"  {issue}")

        # 时间窗口检查
        tw_checker = TimeWindowChecker()
        if tw_checker.config.get("enabled", False):
            within = tw_checker.is_within_work_hours()
            print(f"\n时间窗口: {'[在工作时间内]' if within else '[在工作时间外]'}")
            if not within:
                next_time = tw_checker.get_next_work_time()
                print(f"下次工作时间: {next_time}")

    elif args.command == "time-window":
        tw = TimeWindowChecker()

        if args.tw_command == "status":
            print("\n[TIME WINDOW STATUS]")
            print("=" * 50)
            print(f"Enabled:      {tw.config.get('enabled', False)}")
            print(f"Work hours:   {tw.config.get('work_hours', {}).get('start', '09:00')} - "
                  f"{tw.config.get('work_hours', {}).get('end', '22:00')}")
            print(f"Timezone:     {tw.config.get('timezone', 'Asia/Shanghai')}")
            print(f"Weekend:      {'Allowed' if tw.config.get('allow_weekend', True) else 'Not allowed'}")
            print(f"Overnight:    {'Allowed' if tw.config.get('allow_overnight', False) else 'Not allowed'}")
            print(f"\n当前状态:    {'[在工作时间内]' if tw.is_within_work_hours() else '[在工作时间外]'}")
            if tw.should_defer_task():
                print(f"下次工作时间: {tw.get_next_work_time()}")

        elif args.tw_command == "enable":
            tw.configure(enabled=True)
            print("[OK] Time window enabled")

        elif args.tw_command == "disable":
            tw.configure(enabled=False)
            print("[OK] Time window disabled")

        elif args.tw_command == "config":
            allow_weekend = None
            if args.weekend:
                allow_weekend = True
            elif args.no_weekend:
                allow_weekend = False

            tw.configure(
                start=args.start,
                end=args.end,
                allow_weekend=allow_weekend
            )


if __name__ == "__main__":
    main()
