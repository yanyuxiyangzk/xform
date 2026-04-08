#!/usr/bin/env python3
"""
Auto Heartbeat - 定时心跳守护
每10分钟检查一次，维护自我改进系统

功能:
- 定时心跳检查
- 每小时自动质量门禁
- 每小时自动保存检查点
- Stuck检测 + 模型升级
- Discord通知（可选）
- 限流保护

用法:
  python auto_heartbeat.py run [--continuous]
  python auto_heartbeat.py check
  python auto_heartbeat.py status
"""

import sys
import time
import json
import subprocess
from datetime import datetime
from pathlib import Path

# 配置
AUTO_DEV_BASE = Path(__file__).parent.parent
SELF_IMPROVE_DIR = AUTO_DEV_BASE / "self-improving"
SCRIPTS_DIR = AUTO_DEV_BASE / "scripts"
PROJECTS_DIR = AUTO_DEV_BASE.parent
HEARTBEAT_INTERVAL = 600  # 10分钟
QUALITY_GATE_INTERVAL = 6  # 每6个心跳 = 1小时


class Colors:
    RED = '\033[91m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def color_text(text: str, color: str) -> str:
    return f"{color}{text}{Colors.RESET}"


class AutoHeartbeat:
    """心跳守护主类"""

    def __init__(self):
        self.checkpoint_ops = SCRIPTS_DIR / "checkpoint_ops.py"
        self.quality_gate_script = SCRIPTS_DIR / "quality_gate.py"
        self.reviewer_script = SCRIPTS_DIR / "reviewer.py"
        self.pace_control_script = SCRIPTS_DIR / "pace_control.py"
        self.model_escalation_script = SCRIPTS_DIR / "model_escalation.py"
        self.notification_script = SCRIPTS_DIR / "notification_ops.py"
        self.rule_guard_script = SCRIPTS_DIR / "rule_guard.py"
        self.heartbeat_count = 0
        self.hourly_actions = []  # 每小时执行的操作

    def _run_script(self, script_path: Path, *args, timeout: int = 60) -> tuple:
        """运行脚本"""
        if not script_path.exists():
            return -1, "", "Script not found"

        try:
            cmd = [sys.executable, str(script_path)] + list(args)
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Timeout"
        except Exception as e:
            return -1, "", str(e)

    def heartbeat(self) -> dict:
        """执行单次心跳"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "status": "HEARTBEAT_OK",
            "actions": [],
            "errors": []
        }

        self.heartbeat_count += 1

        # ========== 每心跳执行 ==========

        # 1. 检查stuck状态
        stuck_result = self._check_stuck()
        if stuck_result:
            result["stuck_detected"] = stuck_result
            result["status"] = "STUCK_DETECTED"
            result["actions"].append("stuck_check")

        # 2. Pace control检查
        pace_result = self._check_pace()
        if pace_result:
            result["pace_status"] = pace_result
            result["actions"].append("pace_check")

        # ========== 每小时执行 (heartbeat_count % 6 == 0) ==========
        if self.heartbeat_count % QUALITY_GATE_INTERVAL == 0:
            self.hourly_actions.append(datetime.now().isoformat())

            # 3. 保存checkpoint
            checkpoint_ok = self._save_checkpoint()
            if checkpoint_ok:
                result["actions"].append("checkpoint_saved")

            # 4. 质量门禁检查
            quality_result = self._run_quality_gate()
            if quality_result:
                result["quality_gate"] = quality_result
                result["actions"].append("quality_gate")

                # 如果质量门禁失败，发送通知
                if not quality_result.get("passed"):
                    self._send_notification("quality_gate_failed", quality_result)

            # 5. 模型升级检查
            escalation_result = self._check_model_escalation()
            if escalation_result:
                result["model_escalation"] = escalation_result
                result["actions"].append("model_escalation_check")

            # 6. 检测阻塞任务
            blocks_result = self._detect_blocks()
            if blocks_result:
                result["blocks_detected"] = blocks_result
                result["status"] = "BLOCKS_DETECTED"
                result["actions"].append("block_detected")

                # 发送阻塞通知
                self._send_notification("pipeline_blocked", blocks_result)

        return result

    def _check_stuck(self) -> dict:
        """检查stuck状态"""
        if not self.rule_guard_script.exists():
            return None

        returncode, stdout, stderr = self._run_script(
            self.rule_guard_script, "detect-stuck", timeout=30
        )

        if returncode == 0:
            return None  # 没有stuck任务

        # 检测到stuck任务
        return {
            "detected": True,
            "message": stdout.strip()
        }

    def _check_pace(self) -> dict:
        """检查限流状态"""
        if not self.pace_control_script.exists():
            return None

        returncode, stdout, stderr = self._run_script(
            self.pace_control_script, "stats", timeout=30
        )

        if returncode == 0:
            return {"status": "ok", "message": stdout.strip()}
        else:
            return {"status": "limited", "message": stderr.strip()[:200]}

    def _check_model_escalation(self) -> dict:
        """检查是否需要模型升级"""
        if not self.model_escalation_script.exists():
            return None

        # 获取所有stuck任务
        returncode, stdout, stderr = self._run_script(
            self.rule_guard_script, "detect-stuck", timeout=30
        )

        if returncode != 0:
            # 有stuck任务，检查是否需要升级
            returncode, stdout, stderr = self._run_script(
                self.model_escalation_script, "status", timeout=30
            )

            if returncode == 0 and "stuck_tasks" in stdout:
                # 发现stuck任务，触发升级
                returncode, stdout, stderr = self._run_script(
                    self.model_escalation_script, "escalate", "auto-task", timeout=30
                )

                if returncode == 0:
                    return {"escalated": True, "message": stdout.strip()}

        return {"status": "ok"}

    def _save_checkpoint(self) -> bool:
        """保存检查点"""
        if not self.checkpoint_ops.exists():
            return False

        returncode, stdout, stderr = self._run_script(
            self.checkpoint_ops, "save", timeout=30
        )

        return returncode == 0

    def _run_quality_gate(self) -> dict:
        """运行质量门禁"""
        if not self.quality_gate_script.exists():
            return None

        returncode, stdout, stderr = self._run_script(
            self.quality_gate_script,
            "--project", str(PROJECTS_DIR),
            "--json", str(SELF_IMPROVE_DIR / "quality-gate-report.json"),
            timeout=600
        )

        return {
            "passed": returncode == 0,
            "timestamp": datetime.now().isoformat(),
            "output": stdout[-500:] if stdout else ""
        }

    def _detect_blocks(self) -> dict:
        """检测阻塞任务"""
        if not self.checkpoint_ops.exists():
            return None

        returncode, stdout, stderr = self._run_script(
            self.checkpoint_ops, "status", timeout=30
        )

        if returncode == 0 and "error_queue" in stdout:
            # 有错误队列
            return {"detected": True, "message": "Errors in queue"}
        elif returncode == 0 and stdout:
            return {"detected": False, "message": "No blocks"}

        return None

    def _send_notification(self, event_type: str, data: dict):
        """发送通知"""
        if not self.notification_script.exists():
            return

        message = f"Heartbeat event: {event_type}"

        self._run_script(
            self.notification_script, "send", event_type, message,
            timeout=10
        )

    def update_state_file(self, result: dict):
        """更新心跳状态文件"""
        state_file = SELF_IMPROVE_DIR / "heartbeat-state.md"

        lines = [
            "# Self-Improving Heartbeat State",
            "",
            f"last_heartbeat: {result['timestamp']}",
            f"status: {result['status']}",
            f"heartbeat_count: {self.heartbeat_count}",
            f"hourly_actions_count: {len(self.hourly_actions)}",
            "",
            "## Last Actions",
        ]

        for action in result.get('actions', []):
            lines.append(f"- {action}")

        if 'stuck_detected' in result:
            lines.append("")
            lines.append("## Stuck Detection")
            lines.append(f"- detected: {result['stuck_detected'].get('detected')}")
            lines.append(f"- message: {result['stuck_detected'].get('message', '')[:100]}")

        if 'quality_gate' in result:
            lines.append("")
            lines.append("## Quality Gate")
            lines.append(f"- passed: {result['quality_gate'].get('passed')}")
            lines.append(f"- timestamp: {result['quality_gate'].get('timestamp')}")

        lines.append("")
        lines.append(f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        state_file.write_text("\n".join(lines), encoding='utf-8')

    def run(self, continuous: bool = False):
        """运行心跳守护"""
        print(color_text("\n[HEARTBEAT] 自动开发心跳守护", Colors.CYAN + Colors.BOLD))
        print("=" * 60)
        print(f"心跳间隔: {HEARTBEAT_INTERVAL}s (10分钟)")
        print(f"质量门禁: 每{QUALITY_GATE_INTERVAL}次心跳 (~1小时)")
        print(f"检查点保存: 与质量门禁同步")
        print()
        print(color_text("按 Ctrl+C 停止\n", Colors.YELLOW))

        # 启动时检查是否需要恢复
        self._try_recover()

        # 发送启动通知
        self._send_notification("heartbeat_started", {"message": "Heartbeat daemon started"})

        while True:
            try:
                result = self.heartbeat()

                # 打印状态
                status_color = {
                    "HEARTBEAT_OK": Colors.GREEN,
                    "STUCK_DETECTED": Colors.RED,
                    "BLOCKS_DETECTED": Colors.YELLOW,
                }.get(result["status"], Colors.BLUE)

                timestamp = result["timestamp"][11:19]
                print(f"[{timestamp}] {color_text(result['status'], status_color)} ", end="")

                for action in result.get("actions", []):
                    print(f"{action} ", end="")
                print()

                # 更新状态文件
                self.update_state_file(result)

                if not continuous:
                    break

                time.sleep(HEARTBEAT_INTERVAL)

            except KeyboardInterrupt:
                print(color_text("\n[HEARTBEAT] Stopped by user", Colors.YELLOW))
                self._send_notification("heartbeat_stopped", {"message": "Heartbeat daemon stopped"})
                break
            except Exception as e:
                print(color_text(f"\n[ERROR] {e}", Colors.RED))
                time.sleep(HEARTBEAT_INTERVAL)

    def _try_recover(self):
        """尝试从检查点恢复"""
        if not self.checkpoint_ops.exists():
            return

        returncode, stdout, stderr = self._run_script(
            self.checkpoint_ops, "recover", timeout=30
        )

        if returncode == 0 and "No checkpoint" not in stdout:
            print(color_text("\n[RECOVERY] 已从检查点恢复", Colors.GREEN))
            print(stdout[:500] if stdout else "")
        else:
            print(color_text("\n[RECOVERY] 无检查点或无需恢复", Colors.BLUE))

    def check(self) -> dict:
        """检查当前状态"""
        print(color_text("\n[HEARTBEAT] 状态检查", Colors.CYAN))
        print("=" * 60)

        # 读取状态文件
        state_file = SELF_IMPROVE_DIR / "heartbeat-state.md"
        if state_file.exists():
            content = state_file.read_text(encoding='utf-8')
            print(content)
        else:
            print(color_text("  无状态文件，心跳守护尚未启动", Colors.YELLOW))

        # 检查各组件
        print(color_text("\n[COMPONENTS]", Colors.BLUE))
        components = [
            ("checkpoint_ops.py", self.checkpoint_ops),
            ("quality_gate.py", self.quality_gate_script),
            ("pace_control.py", self.pace_control_script),
            ("model_escalation.py", self.model_escalation_script),
            ("notification_ops.py", self.notification_script),
        ]

        for name, path in components:
            status = color_text("[OK]", Colors.GREEN) if path.exists() else color_text("[MISSING]", Colors.RED)
            print(f"  {status} {name}")

        return {}

    def status(self) -> dict:
        """查看详细状态"""
        self.check()

        print(color_text("\n[QUALITY GATE REPORT]", Colors.CYAN))
        report_file = SELF_IMPROVE_DIR / "quality-gate-report.json"
        if report_file.exists():
            try:
                with open(report_file, "r", encoding="utf-8") as f:
                    report = json.load(f)
                if "summary" in report:
                    for key, value in report["summary"].items():
                        print(f"  {key}: {value}")
            except Exception:
                print("  无法读取报告")
        else:
            print("  无质量门禁报告")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Auto Heartbeat - 心跳守护")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # run命令
    run_parser = subparsers.add_parser("run", help="运行心跳守护")
    run_parser.add_argument("--continuous", action="store_true", help="持续运行")

    # check命令
    subparsers.add_parser("check", help="检查状态")

    # status命令
    subparsers.add_parser("status", help="查看详细状态")

    args = parser.parse_args()

    heartbeat = AutoHeartbeat()

    if not args.command or args.command == "run":
        heartbeat.run(continuous=getattr(args, 'continuous', False))
    elif args.command == "check":
        heartbeat.check()
    elif args.command == "status":
        heartbeat.status()


if __name__ == "__main__":
    main()
