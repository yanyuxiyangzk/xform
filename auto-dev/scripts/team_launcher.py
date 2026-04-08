#!/usr/bin/env python3
"""
Team Launcher - Agent团队启动器
使用Claude Code的Team工具并行启动多个Agent

用法:
  python team_launcher.py create <team_name>           # 创建团队
  python team_launcher.py launch <team_name> <role>   # 启动Agent
  python team_launcher.py launch-all <pipeline_id>     # 启动完整团队
  python team_launcher.py status <team_name>          # 查看团队状态
  python team_launcher.py shutdown <team_name>         # 关闭团队

角色:
  backend-dev     - 后端开发
  frontend-dev    - 前端开发
  tester         - 测试工程师
  reviewer       - 代码审查
  ui-designer    - UI设计师
  devops         - DevOps工程师
  architect      - 架构师
"""

import os
import sys
import json
import argparse
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

# 配置
AUTO_DEV_BASE = Path(__file__).parent.parent
AGENTS_DIR = AUTO_DEV_BASE / "agents"
SKILLS_DIR = AUTO_DEV_BASE / "skills"
TEAMS_DIR = AUTO_DEV_BASE / "teams"
TASKS_DIR = AUTO_DEV_BASE / "tasks"

# Agent角色定义
AGENT_ROLES = {
    "backend-dev": {
        "name": "backend-dev",
        "description": "后端开发工程师",
        "agent_file": "backend-dev.md",
        "skill_file": "backend-dev-skill.md",
        "responsibilities": ["Java/Spring开发", "API实现", "数据库设计"]
    },
    "frontend-dev": {
        "name": "frontend-dev",
        "description": "前端开发工程师",
        "agent_file": "frontend-dev.md",
        "skill_file": "frontend-dev-skill.md",
        "responsibilities": ["Vue开发", "UI实现", "组件开发"]
    },
    "tester": {
        "name": "tester",
        "description": "测试工程师",
        "agent_file": "tester.md",
        "skill_file": "tester-skill.md",
        "responsibilities": ["单元测试", "集成测试", "测试报告"]
    },
    "ui-designer": {
        "name": "ui-designer",
        "description": "UI设计师",
        "agent_file": "ui-designer.md",
        "skill_file": "ui-designer-skill.md",
        "responsibilities": ["UI设计", "原型制作", "视觉规范"]
    },
    "devops": {
        "name": "devops",
        "description": "DevOps工程师",
        "agent_file": "devops.md",
        "skill_file": "devops-skill.md",
        "responsibilities": ["CI/CD", "构建部署", "环境配置"]
    },
    "architect": {
        "name": "architect",
        "description": "架构师",
        "agent_file": "architect.md",
        "skill_file": "architect-skill.md",
        "responsibilities": ["架构设计", "技术方案", "代码审查"]
    },
    "product-manager": {
        "name": "product-manager",
        "description": "产品经理",
        "agent_file": "product-manager.md",
        "skill_file": "product-manager-skill.md",
        "responsibilities": ["需求分析", "产品设计", "优先级排序"]
    },
    "reviewer": {
        "name": "reviewer",
        "description": "代码审查专家",
        "agent_file": "reviewer.md",
        "skill_file": "reviewer-skill.md",
        "responsibilities": ["代码审核", "质量评估", "安全审查"]
    },
    "operation": {
        "name": "operation",
        "description": "运维工程师",
        "agent_file": "operation.md",
        "skill_file": "operation-skill.md",
        "responsibilities": ["环境部署", "监控配置", "日志管理"]
    }
}


class TeamLauncher:
    def __init__(self):
        self.teams_dir = TEAMS_DIR
        self.teams_dir.mkdir(exist_ok=True)

    def load_agent(self, agent_name: str) -> Optional[Dict]:
        """加载Agent定义"""
        if agent_name not in AGENT_ROLES:
            return None

        role = AGENT_ROLES[agent_name]
        agent_file = AGENTS_DIR / role["agent_file"]

        if not agent_file.exists():
            return None

        with open(agent_file, "r", encoding="utf-8") as f:
            content = f.read()

        return {
            "name": role["name"],
            "description": role["description"],
            "responsibilities": role["responsibilities"],
            "prompt": content[:500]  # 截取前500字符
        }

    def load_skill(self, agent_name: str) -> Optional[str]:
        """加载Agent Skill"""
        if agent_name not in AGENT_ROLES:
            return None

        role = AGENT_ROLES[agent_name]
        skill_file = SKILLS_DIR / role["skill_file"]

        if not skill_file.exists():
            return None

        with open(skill_file, "r", encoding="utf-8") as f:
            return f.read()

    def create_team(self, team_name: str, pipeline_id: str = None) -> Dict:
        """创建团队配置"""
        team_config = {
            "name": team_name,
            "pipeline_id": pipeline_id,
            "created_at": datetime.now().isoformat(),
            "status": "created",
            "members": []
        }

        config_file = self.teams_dir / f"{team_name}.json"
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(team_config, f, ensure_ascii=False, indent=2)

        print(f"[OK] Team created: {team_name}")
        return team_config

    def add_member(self, team_name: str, role: str) -> bool:
        """添加团队成员"""
        config_file = self.teams_dir / f"{team_name}.json"

        if not config_file.exists():
            print(f"[ERROR] Team not found: {team_name}")
            return False

        with open(config_file, "r", encoding="utf-8") as f:
            team_config = json.load(f)

        agent = self.load_agent(role)
        if not agent:
            print(f"[ERROR] Agent not found: {role}")
            return False

        # 检查是否已存在
        for m in team_config["members"]:
            if m["role"] == role:
                print(f"[WARN] {role} already in team")
                return True

        team_config["members"].append({
            "role": role,
            "name": agent["name"],
            "description": agent["description"],
            "status": "idle",
            "added_at": datetime.now().isoformat()
        })

        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(team_config, f, ensure_ascii=False, indent=2)

        print(f"[OK] Added {role} to team {team_name}")
        return True

    def get_team(self, team_name: str) -> Optional[Dict]:
        """获取团队配置"""
        config_file = self.teams_dir / f"{team_name}.json"
        if not config_file.exists():
            return None

        with open(config_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def list_teams(self) -> List[Dict]:
        """列出所有团队"""
        teams = []
        for f in self.teams_dir.glob("*.json"):
            with open(f, "r", encoding="utf-8") as file:
                teams.append(json.load(file))
        return teams

    def generate_team_prompt(self, team_name: str) -> str:
        """生成团队启动提示"""
        team = self.get_team(team_name)
        if not team:
            return ""

        lines = [f"# Agent Team: {team_name}", ""]
        lines.append("## Team Members:")
        lines.append("")

        for member in team["members"]:
            skill = self.load_skill(member["role"])
            lines.append(f"### {member['role']} ({member['description']})")
            lines.append(f"**Responsibilities:** {', '.join(member.get('responsibilities', []))}")
            if skill:
                lines.append("")
                lines.append("**Skill:**")
                lines.append(skill[:300] + "..." if len(skill) > 300 else skill)
            lines.append("")

        return "\n".join(lines)

    def generate_launch_commands(self, team_name: str) -> Dict:
        """生成启动命令"""
        team = self.get_team(team_name)
        if not team:
            return {}

        commands = {}
        parallel_cmd = []

        for member in team["members"]:
            role = member["role"]
            cmd = f'claude-code --agent {role}'
            commands[role] = cmd
            parallel_cmd.append(cmd)

        commands["parallel"] = " & ".join(parallel_cmd) + " &"

        return commands

    def launch_team_parallel(self, team_name: str, pipeline_dir: Path = None) -> bool:
        """并行启动整个团队（通过生成脚本）"""
        team = self.get_team(team_name)
        if not team:
            print(f"[ERROR] Team not found: {team_name}")
            return False

        print(f"\n[LAUNCH] Team: {team_name}")
        print("=" * 60)
        print(f"Pipeline: {team.get('pipeline_id', 'none')}")
        print(f"Team Size: {len(team['members'])} agents")
        print("")

        # 生成团队启动脚本
        script_path = AUTO_DEV_BASE / f"launch-{team_name}.sh"
        prompt = self.generate_team_prompt(team_name)

        # 生成Claude Code team创建命令
        team_create_cmd = f'claude-code --team {team_name}'

        print("[INFO] To start this team in Claude Code, run:")
        print("")
        print(f"  1. Create team:")
        print(f"     /team create {team_name}")
        print("")
        print("  2. Spawn agents in parallel:")
        for member in team["members"]:
            print(f"     /spawn {member['role']} --team {team_name}")
        print("")
        print(f"  3. Or use single command:")
        print(f"     {team_create_cmd}")
        print("")

        # 列出每个agent的角色
        print("[TEAM MEMBERS]")
        for member in team["members"]:
            status = member.get("status", "idle")
            print(f"  [{status}] {member['role']}: {member['description']}")

        # 生成自动启动脚本
        script_content = f'''#!/bin/bash
# Auto-Dev Team Launcher Script
# Team: {team_name}
# Generated: {datetime.now().isoformat()}

TEAM_NAME="{team_name}"
PROJECT_DIR="{AUTO_DEV_BASE.parent}"

echo "[TEAM LAUNCHER] Starting team: $TEAM_NAME"

# Spawn agents in parallel
'''
        for member in team["members"]:
            script_content += f'''
echo "[SPAWN] Starting {member['role']}..."
claude-code --agent {member['role']} --project {team.get('pipeline_id', 'default')} &
'''

        script_content += '''
echo "[TEAM LAUNCHER] All agents spawned. Waiting..."
wait
echo "[TEAM LAUNCHER] All agents completed."
'''

        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script_content)

        print(f"\n[SCRIPT] Launch script saved: {script_path}")
        print(f"  chmod +x {script_path} && ./{script_path}")
        return True

    def show_team_status(self, team_name: str) -> Dict:
        """显示团队状态"""
        team = self.get_team(team_name)
        if not team:
            return {"error": f"Team not found: {team_name}"}

        return {
            "name": team["name"],
            "pipeline_id": team.get("pipeline_id"),
            "status": team.get("status"),
            "created_at": team.get("created_at"),
            "members": team.get("members", [])
        }


def main():
    parser = argparse.ArgumentParser(description="Team Launcher - Agent团队启动器")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # create命令
    create_parser = subparsers.add_parser("create", help="创建团队")
    create_parser.add_argument("team_name", help="团队名称")
    create_parser.add_argument("--pipeline", "-p", help="关联的流水线ID")

    # add命令
    add_parser = subparsers.add_parser("add", help="添加成员")
    add_parser.add_argument("team_name", help="团队名称")
    add_parser.add_argument("role", choices=list(AGENT_ROLES.keys()), help="角色")

    # launch命令
    launch_parser = subparsers.add_parser("launch", help="启动单个Agent")
    launch_parser.add_argument("team_name", help="团队名称")
    launch_parser.add_argument("role", choices=list(AGENT_ROLES.keys()), help="角色")

    # launch-all命令
    launch_all_parser = subparsers.add_parser("launch-all", help="启动完整团队")
    launch_all_parser.add_argument("pipeline_id", help="流水线ID")

    # status命令
    status_parser = subparsers.add_parser("status", help="查看团队状态")
    status_parser.add_argument("team_name", nargs="?", help="团队名称")

    # list命令
    subparsers.add_parser("list", help="列出所有团队")

    # roles命令
    subparsers.add_parser("roles", help="显示所有可用角色")

    # shutdown命令
    shutdown_parser = subparsers.add_parser("shutdown", help="关闭团队")
    shutdown_parser.add_argument("team_name", help="团队名称")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    launcher = TeamLauncher()

    if args.command == "create":
        team = launcher.create_team(args.team_name, args.pipeline)
        print(f"\n[OK] Team '{args.team_name}' created")
        print(f"    Pipeline: {args.pipeline or 'none'}")

        # 默认添加关键角色
        print("\n[INFO] Adding default roles...")
        default_roles = ["backend-dev", "frontend-dev", "tester"]
        for role in default_roles:
            launcher.add_member(args.team_name, role)

    elif args.command == "add":
        ok = launcher.add_member(args.team_name, args.role)
        sys.exit(0 if ok else 1)

    elif args.command == "launch":
        team = launcher.get_team(args.team_name)
        if not team:
            print(f"[ERROR] Team not found: {args.team_name}")
            sys.exit(1)

        print(f"[LAUNCH] Spawning {args.role} for team {args.team_name}")
        print(f"  claude-code --agent {args.role} --team {args.team_name}")

        # 这里应该使用Agent tool来spawn，但CLI模式只能打印命令
        print("\n[INFO] Run this command to start the agent:")
        print(f"  claude-code --agent {args.role}")

    elif args.command == "launch-all":
        team_name = f"team-{args.pipeline_id}"
        team = launcher.get_team(team_name)

        if not team:
            # 自动创建团队
            print(f"[INFO] Creating team for pipeline: {args.pipeline_id}")
            launcher.create_team(team_name, args.pipeline_id)
            # 添加所有角色
            for role in AGENT_ROLES.keys():
                launcher.add_member(team_name, role)
            team = launcher.get_team(team_name)

        launcher.launch_team_parallel(team_name)

    elif args.command == "status":
        if args.team_name:
            status = launcher.show_team_status(args.team_name)
            if "error" in status:
                print(f"[ERROR] {status['error']}")
            else:
                print(f"\n[TEAM STATUS] {status['name']}")
                print("=" * 50)
                print(f"Pipeline: {status.get('pipeline_id', 'none')}")
                print(f"Status: {status.get('status', 'unknown')}")
                print(f"Created: {status.get('created_at', 'unknown')}")
                print("\nMembers:")
                for m in status.get("members", []):
                    print(f"  [{m.get('status', '?')}] {m['role']}: {m['description']}")
        else:
            teams = launcher.list_teams()
            print(f"\n[TEAMS] Total: {len(teams)}")
            for t in teams:
                print(f"  {t['name']} ({len(t.get('members', []))} members) - {t.get('status', 'unknown')}")

    elif args.command == "list":
        teams = launcher.list_teams()
        print(f"\n[TEAMS] {len(teams)} teams")
        for t in teams:
            members = [m["role"] for m in t.get("members", [])]
            print(f"\n  {t['name']}")
            print(f"    Pipeline: {t.get('pipeline_id', 'none')}")
            print(f"    Members: {', '.join(members) or 'none'}")
            print(f"    Status: {t.get('status', 'unknown')}")

    elif args.command == "roles":
        print("\n[AVAILABLE AGENT ROLES]")
        print("=" * 50)
        for role, info in AGENT_ROLES.items():
            print(f"\n  {role}")
            print(f"    Description: {info['description']}")
            print(f"    Responsibilities: {', '.join(info['responsibilities'])}")

    elif args.command == "shutdown":
        team = launcher.get_team(args.team_name)
        if not team:
            print(f"[ERROR] Team not found: {args.team_name}")
            sys.exit(1)

        # 更新状态
        team["status"] = "shutdown"
        config_file = launcher.teams_dir / f"{args.team_name}.json"
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(team, f, ensure_ascii=False, indent=2)

        print(f"[OK] Team {args.team_name} marked as shutdown")


if __name__ == "__main__":
    main()
