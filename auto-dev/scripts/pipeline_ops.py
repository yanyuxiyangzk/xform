#!/usr/bin/env python3
"""
Pipeline Operations - 流水线管理脚本
支持创建、执行、监控需求开发流水线

用法:
  python pipeline_ops.py create <title> <type> [--description DESC]
  python pipeline_ops.py list [--status STATUS]
  python pipeline_ops.py status <pipeline_id>
  python pipeline_ops.py advance <pipeline_id> <next_stage>
  python pipeline_ops.py report [--format plain|markdown]

流水线阶段:
  requirement → design → development → testing → deployment → completed

类型:
  feature | bugfix | optimization
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
PIPELINE_DIR = AUTO_DEV_BASE / "tasks" / "pipeline"
MEMORY_OPS = AUTO_DEV_BASE / "scripts" / "memory_ops.py"

# 流水线阶段
STAGES = ["requirement", "design", "development", "testing", "deployment", "completed"]

# 阶段名称
STAGE_NAMES = {
    "requirement": "需求分析",
    "design": "技术设计",
    "development": "开发实现",
    "testing": "测试验证",
    "deployment": "上线部署",
    "completed": "已完成"
}

# 任务类型
TYPE_OPTIONS = ["feature", "bugfix", "optimization"]


class PipelineOps:
    def __init__(self):
        self.pipeline_dir = PIPELINE_DIR
        self.pipeline_dir.mkdir(parents=True, exist_ok=True)

    def generate_id(self, prefix: str = "PIPELINE") -> str:
        """生成流水线ID"""
        date = datetime.now().strftime("%Y%m%d")
        count = len(list(self.pipeline_dir.rglob("*.md"))) + 1
        return f"{prefix}-{date}-{count:03d}"

    def create(self, title: str, pipeline_type: str = "feature", description: str = "") -> str:
        """创建新流水线"""
        pipeline_id = self.generate_id()

        # 创建流水线目录
        pipeline_dir = self.pipeline_dir / pipeline_id
        pipeline_dir.mkdir(exist_ok=True)

        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        content = f"""# 流水线任务: {title}

## 基本信息
- ID: {pipeline_id}
- 需求名称: {title}
- 类型: {pipeline_type}
- 描述: {description or "无"}
- 创建时间: {now}
- 创建人: project-manager
- 当前阶段: requirement
- 状态: 进行中

## 阶段进度

### 阶段1：需求分析 (requirement)
- 负责人: product-manager
- 状态: pending
- 开始时间: -
- 完成时间: -
- 交付物: {pipeline_id}/01-requirement.md
- 下一步自动触发: architect

### 阶段2：技术设计 (design)
- 负责人: architect
- 状态: pending
- 开始时间: -
- 完成时间: -
- 交付物: {pipeline_id}/02-design.md
- 下一步自动触发: backend-dev + frontend-dev

### 阶段3：开发实现 (development)
- 负责人: backend-dev + frontend-dev
- 状态: pending
- 开始时间: -
- 完成时间: -
- 交付物: 代码已提交到仓库
- 下一步自动触发: tester

### 阶段4：测试验证 (testing)
- 负责人: tester
- 状态: pending
- 开始时间: -
- 完成时间: -
- 交付物: {pipeline_id}/04-test-report.md
- 下一步自动触发: operation

### 阶段5：上线部署 (deployment)
- 负责人: operation
- 状态: pending
- 开始时间: -
- 完成时间: -
- 交付物: {pipeline_id}/05-deploy-report.md

## 阻塞记录
- 无

## 向用户汇报
- 最后汇报时间: -
- 汇报内容: -
"""
        filepath = pipeline_dir / f"{pipeline_id}.md"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        # 创建阶段目录
        for i in range(1, 6):
            (pipeline_dir / f"0{i}").mkdir(exist_ok=True)

        print(f"[OK] 流水线已创建: {pipeline_id}")
        print(f"   需求: {title}")
        print(f"   类型: {pipeline_type}")
        print(f"   目录: {pipeline_dir}")
        print(f"\n[TODO] 下一步: 进入需求分析阶段 (product-manager)")

        return pipeline_id

    def list_pipelines(self, status_filter: Optional[str] = None) -> List[Dict]:
        """列出流水线"""
        results = []

        for pipeline_file in self.pipeline_dir.rglob("*.md"):
            if pipeline_file.name == "README.md":
                continue

            try:
                with open(pipeline_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # 提取信息
                pipeline_id = pipeline_file.parent.name
                title = pipeline_file.stem.replace("流水线任务: ", "")
                current_stage = "unknown"
                pipeline_status = "unknown"
                pipeline_type = "feature"

                for line in content.split("\n"):
                    if line.startswith("- 当前阶段:"):
                        current_stage = line.split(":", 1)[1].strip()
                    elif line.startswith("- 状态:"):
                        pipeline_status = line.split(":", 1)[1].strip()
                    elif line.startswith("- 类型:"):
                        pipeline_type = line.split(":", 1)[1].strip()

                if status_filter and pipeline_status != status_filter:
                    continue

                results.append({
                    "id": pipeline_id,
                    "title": title,
                    "current_stage": current_stage,
                    "stage_name": STAGE_NAMES.get(current_stage, current_stage),
                    "status": pipeline_status,
                    "type": pipeline_type,
                    "file": str(pipeline_file.relative_to(self.pipeline_dir))
                })
            except Exception:
                continue

        # 按创建时间降序
        results.sort(key=lambda x: x["id"], reverse=True)
        return results

    def get_status(self, pipeline_id: str) -> Optional[Dict]:
        """获取流水线详细状态"""
        pipeline_dir = self.pipeline_dir / pipeline_id
        pipeline_file = pipeline_dir / f"{pipeline_id}.md"

        if not pipeline_file.exists():
            print(f"❌ 未找到流水线: {pipeline_id}")
            return None

        with open(pipeline_file, "r", encoding="utf-8") as f:
            content = f.read()

        # 解析状态
        info = {
            "id": pipeline_id,
            "title": "",
            "type": "feature",
            "current_stage": "requirement",
            "status": "进行中",
            "stages": {}
        }

        current_section = None
        for line in content.split("\n"):
            if line.startswith("# 流水线任务:"):
                info["title"] = line.split(":", 1)[1].strip()
            elif line.startswith("- "):
                key, value = line[2:].split(":", 1)
                key = key.strip()
                value = value.strip()
                if key == "当前阶段":
                    info["current_stage"] = value
                elif key == "状态":
                    info["status"] = value
                elif key == "类型":
                    info["type"] = value
            elif line.startswith("### 阶段"):
                # 解析阶段信息
                parts = line.split("：")
                if len(parts) > 1:
                    stage_key = parts[0].replace("### 阶段", "").strip()
                    for stage_name, stage_label in [("1", "requirement"), ("2", "design"),
                                                    ("3", "development"), ("4", "testing"),
                                                    ("5", "deployment")]:
                        if stage_name in stage_key:
                            current_section = stage_label
                            info["stages"][stage_label] = {"status": "pending"}
                            break

        return info

    def advance(self, pipeline_id: str, next_stage: str) -> bool:
        """推进流水线到下一阶段"""
        if next_stage not in STAGES:
            print(f"❌ 无效阶段: {next_stage}")
            print(f"   有效阶段: {', '.join(STAGES)}")
            return False

        pipeline_dir = self.pipeline_dir / pipeline_id
        pipeline_file = pipeline_dir / f"{pipeline_id}.md"

        if not pipeline_file.exists():
            print(f"❌ 未找到流水线: {pipeline_id}")
            return False

        with open(pipeline_file, "r", encoding="utf-8") as f:
            content = f.read()

        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        lines = content.split("\n")

        # 更新当前阶段
        for i, line in enumerate(lines):
            if line.startswith("- 当前阶段:"):
                lines[i] = f"- 当前阶段: {next_stage}"
            elif line.startswith("- 状态:") and next_stage == "completed":
                lines[i] = f"- 状态: 已完成"

        new_content = "\n".join(lines)

        with open(pipeline_file, "w", encoding="utf-8") as f:
            f.write(new_content)

        stage_name = STAGE_NAMES.get(next_stage, next_stage)
        print(f"[OK] 流水线已推进: {pipeline_id}")
        print(f"   当前阶段: {stage_name}")
        print(f"   时间: {now}")

        return True

    def report(self, output_format: str = "markdown") -> str:
        """生成流水线报告"""
        pipelines = self.list_pipelines()

        if output_format == "plain":
            lines = ["=" * 60]
            lines.append("[TODO] 流水线状态报告")
            lines.append("=" * 60)
            lines.append(f"总任务数: {len(pipelines)}")
            lines.append("")

            in_progress = [p for p in pipelines if p["status"] == "进行中"]
            completed = [p for p in pipelines if p["status"] == "已完成"]

            lines.append(f"进行中: {len(in_progress)}")
            for p in in_progress:
                lines.append(f"  - {p['id']} | {p['title'][:30]}")
                lines.append(f"    阶段: {p['stage_name']}")

            lines.append(f"\n已完成: {len(completed)}")
            for p in completed:
                lines.append(f"  - {p['id']} | {p['title'][:30]}")

            return "\n".join(lines)
        else:
            lines = ["## [STATS] 流水线状态报告", ""]
            lines.append(f"**总任务数**: {len(pipelines)}")
            lines.append("")
            lines.append("### 进行中任务")
            lines.append("| ID | 需求 | 当前阶段 | 状态 |")
            lines.append("|----|------|----------|------|")

            in_progress = [p for p in pipelines if p["status"] == "进行中"]
            for p in in_progress:
                lines.append(f"| {p['id']} | {p['title'][:30]} | {p['stage_name']} | {p['status']} |")

            lines.append("")
            lines.append("### 已完成")
            lines.append("| ID | 需求 |")
            lines.append("|----|------|")

            completed = [p for p in pipelines if p["status"] == "已完成"]
            for p in completed:
                lines.append(f"| {p['id']} | {p['title'][:40]} |")

            return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Pipeline Operations - 流水线管理")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # create命令
    create_parser = subparsers.add_parser("create", help="创建流水线")
    create_parser.add_argument("title", help="需求标题")
    create_parser.add_argument("type", nargs="?", default="feature", choices=TYPE_OPTIONS, help="类型")
    create_parser.add_argument("--description", "-d", default="", help="描述")

    # list命令
    list_parser = subparsers.add_parser("list", help="列出流水线")
    list_parser.add_argument("--status", "-s", help="状态筛选")

    # status命令
    status_parser = subparsers.add_parser("status", help="查看状态")
    status_parser.add_argument("pipeline_id", help="流水线ID")

    # advance命令
    advance_parser = subparsers.add_parser("advance", help="推进阶段")
    advance_parser.add_argument("pipeline_id", help="流水线ID")
    advance_parser.add_argument("next_stage", choices=STAGES, help="下一阶段")

    # report命令
    report_parser = subparsers.add_parser("report", help="生成报告")
    report_parser.add_argument("--format", "-f", choices=["plain", "markdown"], default="markdown", help="格式")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    ops = PipelineOps()

    if args.command == "create":
        ops.create(args.title, args.type, args.description)

    elif args.command == "list":
        pipelines = ops.list_pipelines(args.status)
        if pipelines:
            print(f"\n[TODO] 流水线列表 (共 {len(pipelines)} 条)")
            print("=" * 80)
            for p in pipelines:
                status_icon = "[RUNNING]" if p["status"] == "进行中" else "[OK]"
                print(f"{status_icon} {p['id']} | {p['title'][:40]}")
                print(f"   阶段: {p['stage_name']} | 类型: {p['type']}")
        else:
            print("暂无流水线")

    elif args.command == "status":
        result = ops.get_status(args.pipeline_id)
        if result:
            print(f"\n[STATS] 流水线: {result['id']}")
            print("=" * 60)
            print(f"需求: {result['title']}")
            print(f"类型: {result['type']}")
            print(f"当前阶段: {STAGE_NAMES.get(result['current_stage'], result['current_stage'])}")
            print(f"状态: {result['status']}")

    elif args.command == "advance":
        ops.advance(args.pipeline_id, args.next_stage)

    elif args.command == "report":
        print(ops.report(args.format))


if __name__ == "__main__":
    main()
