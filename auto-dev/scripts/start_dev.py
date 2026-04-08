#!/usr/bin/env python3
"""
Auto Dev Runner - 自动开发主入口
一键启动 auto-dev 全自动开发系统

用法:
  python start_dev.py                           # 交互模式
  python start_dev.py auto "<需求>"           # 启动自动开发
  python start_dev.py continue                 # 继续开发
  python start_dev.py status                   # 查看状态
  python start_dev.py health                  # 健康检查
  python start_dev.py quality                 # 质量检查
  python start_dev.py review                  # 代码审核
  python start_dev.py heartbeat               # 启动心跳守护
  python start_dev.py install-hook            # 安装Git Hooks
  python start_dev.py check                  # 检查系统状态
"""

import sys
import os
import re
import json
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple, Dict

# 配置
AUTO_DEV_BASE = Path(__file__).parent.parent
SCRIPTS_DIR = AUTO_DEV_BASE / "scripts"
PROJECTS_DIR = AUTO_DEV_BASE.parent


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


class IntentRecognizer:
    """用户意图识别"""

    PATTERNS = {
        "auto_develop": r"(自动开发|开始自动开发|开发新功能|开发需求|开始自动化开发|auto-dev|automated-dev)",
        "continue": r"(继续开发|恢复开发|接着开发|resume)",
        "status": r"(检查状态|查看进度|状态如何|现在到哪了|status)",
        "test": r"(运行测试|执行测试|跑一下测试|run test)",
        "quality": r"(质量检查|门禁检查|检查一下代码质量|quality gate)",
        "review": r"(代码审核|审核代码|review|code review)",
        "deploy": r"(部署|上线|发布|deploy)",
        "heartbeat": r"(心跳守护|启动监控|monitor)",
        "install_hook": r"(安装钩子|install.*hook|setup.*git)",
    }

    @classmethod
    def recognize(cls, user_input: str) -> Optional[str]:
        """识别用户意图"""
        for intent, pattern in cls.PATTERNS.items():
            if re.search(pattern, user_input, re.IGNORECASE):
                return intent
        return None

    @classmethod
    def extract_requirement(cls, user_input: str) -> str:
        """从用户输入中提取需求描述"""
        # 移除意图关键词
        text = user_input
        for pattern in cls.PATTERNS.values():
            text = re.sub(pattern, "", text, flags=re.IGNORECASE)

        # 清理多余空白
        text = re.sub(r'\s+', ' ', text).strip()

        # 如果清理后为空，返回默认
        if not text:
            return "新功能开发"
        return text


class AutoDevRunner:
    """Auto-Dev 自动开发运行器"""

    def __init__(self):
        self.scripts_dir = SCRIPTS_DIR
        self.pipeline_dir = AUTO_DEV_BASE / "tasks" / "pipeline"
        self.checkpoint_file = AUTO_DEV_BASE / "self-improving" / "checkpoint.json"

    def _run_script(self, script_name: str, *args, timeout: int = 600) -> Tuple[int, str, str]:
        """运行脚本并返回结果"""
        script_path = self.scripts_dir / script_name
        if not script_path.exists():
            return -1, "", f"Script not found: {script_name}"

        cmd = [sys.executable, str(script_path)] + list(args)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", f"Timeout after {timeout}s"
        except Exception as e:
            return -1, "", str(e)

    def _load_latest_pipeline(self) -> Optional[Dict]:
        """加载最新的流水线"""
        if not self.pipeline_dir.exists():
            return None

        pipelines = sorted(self.pipeline_dir.glob("PIPELINE-*"), key=lambda x: x.name, reverse=True)
        if not pipelines:
            return None

        status_file = pipelines[0] / "status.json"
        if not status_file.exists():
            return None

        try:
            with open(status_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def run_auto_develop(self, requirement: str) -> bool:
        """启动自动开发流程"""
        print(color_text("\n" + "=" * 60, Colors.CYAN + Colors.BOLD))
        print(color_text("  AUTO-DEV 全自动开发系统", Colors.CYAN + Colors.BOLD))
        print(color_text("=" * 60, Colors.CYAN + Colors.BOLD))
        print()

        # 1. 初始化流水线
        print(color_text("[1/7] 初始化流水线...", Colors.BLUE))
        returncode, stdout, stderr = self._run_script(
            "pipeline_runner.py", "init", requirement
        )
        if returncode != 0:
            print(color_text(f"  [FAIL] 流水线初始化失败: {stderr[-200:]}", Colors.RED))
            return False
        print(color_text(f"  [OK] 流水线已创建", Colors.GREEN))

        # 提取 pipeline_id
        pipeline_id = None
        for line in stdout.split('\n'):
            if 'ID:' in line:
                pipeline_id = line.split('ID:')[-1].strip()
                break

        if not pipeline_id:
            # 从stdout中解析
            match = re.search(r'PIPELINE-\d{8}-\d{3}', stdout)
            if match:
                pipeline_id = match.group(0)

        print(f"  Pipeline: {color_text(pipeline_id or 'unknown', Colors.CYAN)}")
        print()

        # 2. 创建团队
        print(color_text("[2/7] 创建开发团队...", Colors.BLUE))
        returncode, stdout, stderr = self._run_script(
            "team_launcher.py", "create", f"team-{pipeline_id}", "--pipeline", pipeline_id
        )
        if returncode == 0:
            print(color_text("  [OK] 团队已创建", Colors.GREEN))
        else:
            print(color_text(f"  [WARN] 团队创建有问题: {stderr[-200:]}", Colors.YELLOW))

        # 2.5 启动Agent团队 (agent_spawner)
        print(color_text("[2.5/7] 启动Agent团队...", Colors.BLUE))
        returncode, stdout, stderr = self._run_script(
            "agent_spawner.py", "spawn-team", "dev-team", timeout=60
        )
        if returncode == 0:
            print(color_text("  [OK] Agent团队已启动", Colors.GREEN))
        else:
            print(color_text(f"  [WARN] Agent启动: {stdout[-200:]}", Colors.YELLOW))
        print()

        # 3. 运行流水线
        print(color_text("[3/8] 运行流水线...", Colors.BLUE))
        returncode, stdout, stderr = self._run_script(
            "pipeline_runner.py", "run", pipeline_id or "latest", timeout=7200
        )
        print(stdout)
        if stderr:
            print(color_text(f"  [STDERR] {stderr[-500:]}", Colors.YELLOW))
        print()

        # 4. 质量门禁
        print(color_text("[4/8] 执行质量门禁...", Colors.BLUE))
        returncode, stdout, stderr = self._run_script(
            "quality_gate.py",
            "--project", str(PROJECTS_DIR),
            "--verbose",
            timeout=600
        )
        if returncode == 0:
            print(color_text("  [OK] 质量门禁通过", Colors.GREEN))
        else:
            print(color_text("  [FAIL] 质量门禁未通过", Colors.RED))
            print(stdout[-500:] if stdout else "")
        print()

        # 5. 代码审核
        print(color_text("[5/8] 执行代码审核...", Colors.BLUE))
        returncode, stdout, stderr = self._run_script(
            "reviewer.py",
            "--project", str(PROJECTS_DIR),
            "--iteration", "1",
            timeout=600
        )
        if returncode == 0:
            print(color_text("  [OK] 代码审核通过", Colors.GREEN))
        else:
            print(color_text("  [WARN] 代码审核有问题", Colors.YELLOW))
            print(stdout[-500:] if stdout else "")
        print()

        # 6. 保存 Checkpoint
        print(color_text("[6/8] 保存检查点...", Colors.BLUE))
        returncode, stdout, stderr = self._run_script(
            "checkpoint_ops.py", "save", timeout=30
        )
        if returncode == 0:
            print(color_text("  [OK] 检查点已保存", Colors.GREEN))
        else:
            print(color_text(f"  [WARN] 检查点保存失败", Colors.YELLOW))
        print()

        # 7. 启动心跳守护
        print(color_text("[7/8] 启动心跳守护...", Colors.BLUE))
        print(color_text("  [INFO] 心跳守护将在后台持续监控", Colors.CYAN))
        print(color_text("  运行: python auto_heartbeat.py run --continuous", Colors.CYAN))
        print()

        # 总结
        print(color_text("=" * 60, Colors.GREEN + Colors.BOLD))
        print(color_text("  自动开发已启动!", Colors.GREEN + Colors.BOLD))
        print(color_text("=" * 60, Colors.GREEN + Colors.BOLD))
        print()
        print(f"  Pipeline ID: {color_text(pipeline_id or 'unknown', Colors.CYAN)}")
        print(f"  下一步:")
        print(f"    - 查看状态: python start_dev.py status")
        print(f"    - 继续开发: python start_dev.py continue")
        print(f"    - 启动心跳: python start_dev.py heartbeat")
        print()

        return True

    def run_continue(self) -> bool:
        """继续之前的开发"""
        print(color_text("\n[CONTINUE] 从检查点恢复...", Colors.CYAN))

        # 1. 尝试恢复
        returncode, stdout, stderr = self._run_script(
            "checkpoint_ops.py", "recover", timeout=30
        )
        if returncode != 0 or "No checkpoint" in stdout:
            print(color_text("  [WARN] 没有找到检查点，将创建新流水线", Colors.YELLOW))
            return False

        print(color_text("  [OK] 已恢复检查点", Colors.GREEN))
        print(stdout)

        # 2. 加载最新流水线
        pipeline = self._load_latest_pipeline()
        if not pipeline:
            print(color_text("  [ERROR] 无法加载流水线", Colors.RED))
            return False

        print(f"  Pipeline: {color_text(pipeline['id'], Colors.CYAN)}")
        print(f"  当前阶段: {color_text(pipeline.get('current_stage', 'unknown'), Colors.CYAN)}")

        # 3. 继续运行
        print(color_text("\n[CONTINUE] 继续运行流水线...", Colors.BLUE))
        returncode, stdout, stderr = self._run_script(
            "pipeline_runner.py", "run", pipeline['id'], timeout=7200
        )
        print(stdout)

        return returncode == 0

    def run_status(self) -> bool:
        """查看流水线状态"""
        print(color_text("\n[STATUS] 流水线状态", Colors.CYAN))
        print("=" * 50)

        # 1. 查看所有流水线
        returncode, stdout, stderr = self._run_script(
            "pipeline_runner.py", "list", timeout=30
        )
        print(stdout or stderr)

        # 2. 健康检查
        print(color_text("\n[HEALTH] 系统健康检查", Colors.CYAN))
        print("-" * 50)
        returncode, stdout, stderr = self._run_script(
            "orchestrator_ops.py", "health", timeout=30
        )
        print(stdout or stderr)

        # 3. Checkpoint状态
        print(color_text("\n[CHECKPOINT] 检查点状态", Colors.CYAN))
        print("-" * 50)
        returncode, stdout, stderr = self._run_script(
            "checkpoint_ops.py", "status", timeout=30
        )
        print(stdout or stderr)

        return True

    def run_quality(self) -> bool:
        """运行质量门禁"""
        print(color_text("\n[QUALITY] 质量门禁检查", Colors.CYAN))
        print("=" * 50)

        returncode, stdout, stderr = self._run_script(
            "quality_gate.py",
            "--project", str(PROJECTS_DIR),
            "--verbose",
            timeout=600
        )

        print(stdout)
        if stderr:
            print(color_text(f"STDERR: {stderr}", Colors.YELLOW))

        if returncode == 0:
            print(color_text("\n[OK] 质量门禁通过!", Colors.GREEN))
        else:
            print(color_text("\n[FAIL] 质量门禁未通过", Colors.RED))

        return returncode == 0

    def run_review(self) -> bool:
        """运行代码审核"""
        print(color_text("\n[REVIEW] 代码审核", Colors.CYAN))
        print("=" * 50)

        returncode, stdout, stderr = self._run_script(
            "reviewer.py",
            "--project", str(PROJECTS_DIR),
            "--iteration", "1",
            "--verbose",
            timeout=600
        )

        print(stdout)
        if stderr:
            print(color_text(f"STDERR: {stderr}", Colors.YELLOW))

        if returncode == 0:
            print(color_text("\n[OK] 代码审核通过!", Colors.GREEN))
        elif returncode == 2:
            print(color_text("\n[REJECTED] 代码审核拒绝 (达到最大迭代次数)", Colors.RED))
        else:
            print(color_text("\n[REVISION] 需要修改代码", Colors.YELLOW))

        return returncode == 0

    def run_heartbeat(self) -> bool:
        """启动心跳守护"""
        print(color_text("\n[HEARTBEAT] 启动心跳守护", Colors.CYAN))
        print("=" * 50)
        print(color_text("  每10分钟心跳检查", Colors.BLUE))
        print(color_text("  每小时自动质量门禁", Colors.BLUE))
        print(color_text("  每小时自动保存检查点", Colors.BLUE))
        print()
        print(color_text("  按 Ctrl+C 停止", Colors.YELLOW))
        print()

        returncode, stdout, stderr = self._run_script(
            "auto_heartbeat.py", "run", "--continuous", timeout=86400
        )

        print(stdout)
        return True

    def run_install_hook(self) -> bool:
        """安装Git Hooks"""
        print(color_text("\n[HOOK] 安装 Git Hooks", Colors.CYAN))
        print("=" * 50)

        returncode, stdout, stderr = self._run_script(
            "install_hooks.py", "install", "--force", timeout=30
        )

        print(stdout)
        if stderr:
            print(color_text(f"STDERR: {stderr}", Colors.YELLOW))

        if returncode == 0:
            print(color_text("\n[OK] Git Hooks 安装成功!", Colors.GREEN))
            print(color_text("  每次 git commit 将自动触发质量门禁", Colors.CYAN))
        else:
            print(color_text("\n[FAIL] Git Hooks 安装失败", Colors.RED))

        return returncode == 0

    def run_check(self) -> bool:
        """检查系统状态"""
        print(color_text("\n[AUTO-DEV] 系统检查", Colors.CYAN + Colors.BOLD))
        print("=" * 60)

        all_ok = True

        # 检查核心脚本
        print(color_text("\n[1] 核心脚本", Colors.BLUE))
        core_scripts = [
            "pipeline_runner.py",
            "quality_gate.py",
            "reviewer.py",
            "rule_guard.py",
            "guardian_agent.py",
            "team_launcher.py",
            "agent_spawner.py",
            "checkpoint_ops.py",
            "auto_heartbeat.py",
            "install_hooks.py",
            "orchestrator_ops.py",
        ]

        for script in core_scripts:
            path = self.scripts_dir / script
            status = color_text("[OK]", Colors.GREEN) if path.exists() else color_text("[MISSING]", Colors.RED)
            print(f"  {status} {script}")
            if not path.exists():
                all_ok = False

        # 检查 Skill 文件
        print(color_text("\n[2] Skill 文件", Colors.BLUE))
        skills_dir = AUTO_DEV_BASE / "skills"
        if skills_dir.exists():
            skill_files = list(skills_dir.glob("*skill*.md"))
            print(f"  {color_text('[OK]', Colors.GREEN)} {len(skill_files)} skill 文件")
        else:
            print(f"  {color_text('[MISSING]', Colors.RED)} skills/ 目录")
            all_ok = False

        # 检查 Agent 文件
        print(color_text("\n[3] Agent 文件", Colors.BLUE))
        agents_dir = AUTO_DEV_BASE / "agents"
        if agents_dir.exists():
            agent_files = list(agents_dir.glob("*.md"))
            print(f"  {color_text('[OK]', Colors.GREEN)} {len(agent_files)} agent 文件")
        else:
            print(f"  {color_text('[MISSING]', Colors.RED)} agents/ 目录")
            all_ok = False

        # 检查配置文件
        print(color_text("\n[4] 配置文件", Colors.BLUE))
        config_files = [
            AUTO_DEV_BASE / "RULES.md",
            AUTO_DEV_BASE / ".auto-dev.yaml",
        ]

        for config in config_files:
            status = color_text("[OK]", Colors.GREEN) if config.exists() else color_text("[MISSING]", Colors.RED)
            print(f"  {status} {config.name}")
            if not config.exists():
                all_ok = False

        # 检查自我改进系统
        print(color_text("\n[5] 自我改进系统", Colors.BLUE))
        self_improve_dir = AUTO_DEV_BASE / "self-improving"
        if self_improve_dir.exists():
            print(f"  {color_text('[OK]', Colors.GREEN)} self-improving/ 目录存在")

        # 检查 Harness 架构
        print(color_text("\n[6] Harness 架构 (Guides/Sensors/Memory)", Colors.BLUE))
        guides_ok = (AUTO_DEV_BASE / "guides").exists()
        sensors_ok = (AUTO_DEV_BASE / "sensors").exists()
        memory_ok = (AUTO_DEV_BASE / "memory").exists()
        schema_ok = (AUTO_DEV_BASE / "guides" / "schemas").exists()
        telemetry_ok = (AUTO_DEV_BASE / "sensors" / "runtime" / "telemetry").exists()

        print(f"  {color_text('[OK]' if guides_ok else '[MISSING]', Colors.GREEN if guides_ok else Colors.RED)} guides/ (引导层)")
        print(f"  {color_text('[OK]' if sensors_ok else '[MISSING]', Colors.GREEN if sensors_ok else Colors.RED)} sensors/ (感知层)")
        print(f"  {color_text('[OK]' if memory_ok else '[MISSING]', Colors.GREEN if memory_ok else Colors.RED)} memory/ (记忆层)")
        print(f"  {color_text('[OK]' if schema_ok else '[MISSING]', Colors.GREEN if schema_ok else Colors.RED)} schemas/ (类型化约束)")
        print(f"  {color_text('[OK]' if telemetry_ok else '[MISSING]', Colors.GREEN if telemetry_ok else Colors.RED)} telemetry/ (全链路可观测)")

        if not all([guides_ok, sensors_ok, memory_ok, schema_ok, telemetry_ok]):
            all_ok = False
            missing = []
            if not guides_ok: missing.append("guides")
            if not sensors_ok: missing.append("sensors")
            if not memory_ok: missing.append("memory")
            if not schema_ok: missing.append("schemas")
            if not telemetry_ok: missing.append("telemetry")
            for m in missing:
                print(f"  {color_text('[MISSING]', Colors.RED)} {m}/")

        # 总结
        print(color_text("\n" + "=" * 60, Colors.CYAN))
        if all_ok:
            print(color_text("  [OK] 系统检查完成，一切正常!", Colors.GREEN + Colors.BOLD))
        else:
            print(color_text("  [WARN] 系统检查完成，部分组件缺失", Colors.YELLOW + Colors.BOLD))

        return all_ok


def print_banner():
    print(color_text("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║     ██████╗  ██████╗ ██████╗ ████████╗ ██████╗            ║
║    ██╔════╝ ██╔═══██╗██╔══██╗╚══██╔══╝██╔═══██╗           ║
║    ██║  ███╗██║   ██║██║  ██║   ██║   ██║   ██║           ║
║    ██║   ██║██║   ██║██║  ██║   ██║   ██║   ██║           ║
║    ╚██████╔╝╚██████╔╝██████╔╝   ██║   ╚██████╔╝           ║
║     ╚═════╝  ╚═════╝ ╚═════╝    ╚═╝    ╚═════╝            ║
║                                                           ║
║            AUTO-DEV 全自动开发系统 v2.0                   ║
║            Skill + Script 架构                             ║
║            越用越聪明 - 自我改进系统                       ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """, Colors.CYAN))


def main():
    parser = argparse.ArgumentParser(
        description="Auto-Dev 全自动开发系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python start_dev.py auto "开发用户管理模块"    # 启动自动开发
  python start_dev.py continue                  # 继续之前的开发
  python start_dev.py status                    # 查看状态
  python start_dev.py quality                   # 质量门禁检查
  python start_dev.py review                   # 代码审核
  python start_dev.py heartbeat                # 启动心跳守护
  python start_dev.py install-hook             # 安装Git Hooks
  python start_dev.py check                    # 检查系统状态

一句话启动:
  只要对我说 "自动开发 XXX" 即可!
        """
    )

    parser.add_argument(
        'command',
        nargs='?',
        help='命令: auto, continue, status, quality, review, heartbeat, install-hook, check'
    )

    parser.add_argument(
        'args',
        nargs='*',
        help='命令参数'
    )

    args = parser.parse_args()

    runner = AutoDevRunner()

    # 无参数时显示帮助
    if not args.command:
        print_banner()
        parser.print_help()
        print()
        print(color_text("快速开始:", Colors.GREEN + Colors.BOLD))
        print(color_text("  只要对我说: 自动开发 XXX", Colors.CYAN))
        return 0

    cmd = args.command.lower()
    cmd_args = ' '.join(args.args) if args.args else ''

    # 根据命令执行
    if cmd == 'auto':
        requirement = cmd_args if cmd_args else "新功能开发"
        success = runner.run_auto_develop(requirement)

    elif cmd == 'continue':
        success = runner.run_continue()

    elif cmd == 'status':
        success = runner.run_status()

    elif cmd == 'health':
        success = runner.run_status()

    elif cmd == 'quality':
        success = runner.run_quality()

    elif cmd == 'review':
        success = runner.run_review()

    elif cmd == 'heartbeat':
        success = runner.run_heartbeat()

    elif cmd == 'install-hook' or cmd == 'install_hook':
        success = runner.run_install_hook()

    elif cmd == 'check':
        success = runner.run_check()

    else:
        print(color_text(f"[ERROR] 未知命令: {cmd}", Colors.RED))
        print(color_text("运行 'python start_dev.py' 查看帮助", Colors.YELLOW))
        return 1

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
