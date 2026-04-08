#!/usr/bin/env python3
"""
Agent Spawner - Agent自动启动器
使用Claude Code CLI启动Agent团队

用法:
  python agent_spawner.py spawn <role>          # 启动单个Agent
  python agent_spawner.py spawn-all            # 启动完整团队
  python agent_spawner.py spawn-team <team_name> # 启动指定团队
  python agent_spawner.py list                # 列出所有Agent
  python agent_spawner.py kill <name>         # 停止Agent
"""

import os
import sys
import json
import subprocess
import argparse
import signal
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

# 配置
AUTO_DEV_BASE = Path(__file__).parent.parent
AGENTS_DIR = AUTO_DEV_BASE / "agents"
SKILLS_DIR = AUTO_DEV_BASE / "skills"
PROJECTS_DIR = AUTO_DEV_BASE.parent

# Claude Code CLI 路径 - 动态检测
def _detect_claude_cli() -> str:
    """动态检测 claude-code CLI 路径"""
    try:
        result = subprocess.run(
            ['powershell.exe', '-Command',
             'Get-Command claude -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source'],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass
    return "claude-code"  # fallback

CLAUDE_CODE_CLI = _detect_claude_cli()


class AgentSpawner:
    """Agent启动器"""

    def __init__(self):
        self.active_agents = []
        self.teams_config = self._load_teams_config()

    def _load_teams_config(self) -> Dict:
        """加载团队配置"""
        config_file = AUTO_DEV_BASE / "teams" / "teams-config.json"
        if config_file.exists():
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        return {
            "dev-team": {
                "description": "开发团队(基础)",
                "agents": ["backend-dev", "frontend-dev", "tester"]
            },
            "full-team": {
                "description": "完整团队(全角色)",
                "agents": ["product-manager", "architect", "backend-dev", "frontend-dev", "ui-designer", "tester", "devops", "reviewer"]
            },
            "frontend-team": {
                "description": "前端团队",
                "agents": ["frontend-dev", "ui-designer", "tester"]
            },
            "backend-team": {
                "description": "后端团队",
                "agents": ["backend-dev", "architect", "tester"]
            }
        }

    def _get_agent_prompt(self, role: str) -> str:
        """生成Agent启动提示词"""
        agent_file = AGENTS_DIR / f"{role}.md"
        skill_file = SKILLS_DIR / f"{role}-skill.md"

        prompt_lines = [
            f"# 你是 {role}",
            "",
            "## 你的角色",
        ]

        if agent_file.exists():
            content = agent_file.read_text(encoding="utf-8")
            prompt_lines.append(content[:1000])  # 取前1000字符

        prompt_lines.extend([
            "",
            "## Auto-Dev 规则",
            "你必须遵循 auto-dev 的开发规则，包括：",
            "1. 必须通过 TeamCreate 创建团队",
            "2. 开发前必须调用 gate 检查",
            "3. 提交前必须通过 pre-commit 检查",
            "4. 遵循 RULES.md 中的所有规则",
            "",
            "## 项目信息",
            f"项目目录: {PROJECTS_DIR}",
            f"Auto-Dev 目录: {AUTO_DEV_BASE}",
            "",
        ])

        if skill_file.exists():
            skill_content = skill_file.read_text(encoding="utf-8")
            prompt_lines.extend([
                "## 你的技能 (Skill)",
                skill_content[:2000],  # 取前2000字符
            ])

        return "\n".join(prompt_lines)

    def spawn_agent(self, role: str, name: str = None, team: str = None) -> bool:
        """
        启动单个Agent

        Args:
            role: Agent角色 (backend-dev, frontend-dev, etc.)
            name: Agent实例名称 (可选)
            team: 团队名称 (可选)

        Returns:
            bool: 是否成功启动
        """
        if not name:
            name = f"{role}-{datetime.now().strftime('%H%M%S')}"

        prompt = self._get_agent_prompt(role)

        # 构建命令 - 处理 PowerShell 脚本
        if CLAUDE_CODE_CLI.endswith('.ps1'):
            # PowerShell 脚本，使用 -Command 调用
            cmd = [
                'powershell.exe',
                '-ExecutionPolicy', 'Bypass',
                '-Command',
                f"& '{CLAUDE_CODE_CLI}' --agent {role} --name {name}" + (f" --team {team}" if team else "")
            ]
        else:
            cmd = [
                CLAUDE_CODE_CLI,
                "--agent", role,
                "--name", name,
            ]
            if team:
                cmd.extend(["--team", team])

        print(f"[SPAWN] Starting agent: {name} ({role})")
        print(f"        Command: {' '.join(cmd)}")

        try:
            # 在后台启动Agent
            process = subprocess.Popen(
                cmd,
                cwd=str(PROJECTS_DIR),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            self.active_agents.append({
                "name": name,
                "role": role,
                "team": team,
                "process": process,
                "started_at": datetime.now().isoformat()
            })

            print(f"[OK] Agent {name} started (PID: {process.pid})")
            return True

        except Exception as e:
            print(f"[ERROR] Failed to start agent {name}: {e}")
            return False

    def spawn_team(self, team_name: str = "dev-team") -> bool:
        """
        启动完整团队

        Args:
            team_name: 团队名称

        Returns:
            bool: 是否全部成功启动
        """
        if team_name not in self.teams_config:
            print(f"[ERROR] Unknown team: {team_name}")
            print(f"Available teams: {', '.join(self.teams_config.keys())}")
            return False

        team_config = self.teams_config[team_name]
        agents = team_config["agents"]

        print(f"\n[SPAWN] Starting team: {team_name}")
        print(f"        Description: {team_config['description']}")
        print(f"        Agents: {', '.join(agents)}")
        print("=" * 50)

        success_count = 0
        for role in agents:
            if self.spawn_agent(role, team=team_name):
                success_count += 1

        print("=" * 50)
        print(f"[OK] Team {team_name} started: {success_count}/{len(agents)} agents")

        return success_count == len(agents)

    def list_agents(self) -> List[Dict]:
        """列出所有Agent"""
        result = []

        for agent in self.active_agents:
            proc = agent["process"]
            is_running = proc.poll() is None

            result.append({
                "name": agent["name"],
                "role": agent["role"],
                "team": agent["team"],
                "started_at": agent["started_at"],
                "status": "running" if is_running else "stopped",
                "pid": proc.pid
            })

        return result

    def kill_agent(self, name: str) -> bool:
        """停止Agent"""
        for agent in self.active_agents:
            if agent["name"] == name:
                proc = agent["process"]
                if proc.poll() is None:  # 还在运行
                    proc.terminate()
                    try:
                        proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                    print(f"[OK] Agent {name} stopped")
                    return True
                else:
                    print(f"[WARN] Agent {name} already stopped")
                    return True

        print(f"[ERROR] Agent {name} not found")
        return False

    def kill_all(self):
        """停止所有Agent"""
        for agent in self.active_agents:
            self.kill_agent(agent["name"])

    def status(self) -> Dict:
        """获取状态"""
        running = sum(1 for a in self.list_agents() if a["status"] == "running")

        return {
            "total_agents": len(self.active_agents),
            "running": running,
            "stopped": len(self.active_agents) - running,
            "agents": self.list_agents()
        }


def main():
    parser = argparse.ArgumentParser(description="Agent Spawner - Agent自动启动器")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # spawn命令
    spawn_parser = subparsers.add_parser("spawn", help="启动单个Agent")
    spawn_parser.add_argument("role", help="Agent角色")
    spawn_parser.add_argument("--name", "-n", help="Agent名称")
    spawn_parser.add_argument("--team", "-t", help="团队名称")

    # spawn-all命令
    spawn_all_parser = subparsers.add_parser("spawn-all", help="启动完整团队")
    spawn_all_parser.add_argument("--team", "-t", default="dev-team",
                                  choices=list(AgentSpawner().teams_config.keys()),
                                  help="团队名称")

    # list命令
    subparsers.add_parser("list", help="列出所有Agent")

    # kill命令
    kill_parser = subparsers.add_parser("kill", help="停止Agent")
    kill_parser.add_argument("name", help="Agent名称")

    # kill-all命令
    subparsers.add_parser("kill-all", help="停止所有Agent")

    # status命令
    subparsers.add_parser("status", help="查看状态")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    spawner = AgentSpawner()

    if args.command == "spawn":
        success = spawner.spawn_agent(args.role, args.name, args.team)
        sys.exit(0 if success else 1)

    elif args.command == "spawn-all":
        success = spawner.spawn_team(args.team)
        sys.exit(0 if success else 1)

    elif args.command == "list":
        agents = spawner.list_agents()
        if not agents:
            print("[INFO] No active agents")
        else:
            print(f"\n[AGENTS] {len(agents)} agents")
            print("=" * 50)
            for agent in agents:
                status_color = "[RUNNING]" if agent["status"] == "running" else "[STOPPED]"
                print(f"{status_color} {agent['name']} ({agent['role']}) - {agent['team'] or 'no team'}")

    elif args.command == "kill":
        success = spawner.kill_agent(args.name)
        sys.exit(0 if success else 1)

    elif args.command == "kill-all":
        spawner.kill_all()

    elif args.command == "status":
        status = spawner.status()
        print(f"\n[STATUS] Agent Spawner")
        print("=" * 50)
        print(f"Total: {status['total_agents']}")
        print(f"Running: {status['running']}")
        print(f"Stopped: {status['stopped']}")


if __name__ == "__main__":
    main()
