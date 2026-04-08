#!/usr/bin/env python3
"""
Auto Reflect Hook - 自动反思触发器
Pipeline每个阶段完成后自动触发反思

用法:
  python auto_reflect_hook.py reflect <stage> <result> [--issue ISSUE]
  python auto_reflect_hook.py trigger <pipeline_id> <stage>

阶段:
  requirement - 需求分析
  design - 技术设计
  development - 开发实现
  testing - 测试验证
  deployment - 上线部署
"""

import sys
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

# 配置
AUTO_DEV_BASE = Path(__file__).parent.parent
SELF_IMPROVE_DIR = AUTO_DEV_BASE / "self-improving"

# 阶段名称
STAGES = {
    "requirement": "需求分析",
    "design": "技术设计",
    "development": "开发实现",
    "testing": "测试验证",
    "deployment": "上线部署",
    "completed": "已完成"
}

# 反思模板
REFLECT_TEMPLATES = {
    "requirement": {
        "success": "需求分析顺利完成，理解了{topic}的核心需求",
        "issue": "需求分析中发现{issue}，已调整理解",
        "lesson": "以后应更早确认关键需求细节"
    },
    "design": {
        "success": "技术设计方案完成，确定了{tech}技术选型",
        "issue": "设计方案遇到{issue}，已重新评估",
        "lesson": "技术选型应考虑团队熟悉度和长期维护"
    },
    "development": {
        "success": "代码开发完成，{module}模块已就绪",
        "issue": "开发中发现{issue}，已修复",
        "lesson": "编码前应先完成详细设计，避免返工"
    },
    "testing": {
        "success": "测试通过，{cases}个用例全部OK",
        "issue": "测试发现{issue}缺陷，已提交修复",
        "lesson": "测试用例应覆盖更多边界情况"
    },
    "deployment": {
        "success": "部署成功，服务已上线",
        "issue": "部署遇到{issue}，已解决",
        "lesson": "部署前应准备好回滚方案"
    }
}


class AutoReflectHook:
    def __init__(self):
        self.self_improve_ops = AUTO_DEV_BASE / "scripts" / "self_improve_ops.py"

    def generate_reflection(self, stage: str, result: str, issue: Optional[str] = None) -> dict:
        """
        生成反思内容
        """
        stage_name = STAGES.get(stage, stage)

        if issue:
            reflection = f"{stage_name}中发现问题: {issue}"
            lesson = "从问题中学习"
        else:
            reflection = f"{stage_name}完成: {result}"
            lesson = "顺利完成，保持当前状态"

        return {
            "context": f"Pipeline阶段: {stage_name}",
            "reflection": reflection,
            "lesson": lesson
        }

    def trigger_reflect(self, stage: str, result: str = "", issue: Optional[str] = None) -> Optional[str]:
        """
        触发反思
        返回反思记录ID
        """
        reflection_data = self.generate_reflection(stage, result, issue)

        try:
            # 添加scripts目录到path
            import os
            scripts_dir = str(self.self_improve_ops.parent)
            if scripts_dir not in os.sys.path:
                os.sys.path.insert(0, scripts_dir)

            from self_improve_ops import SelfImproveOps

            ops = SelfImproveOps()
            entry_id = ops.reflect(
                reflection_data["context"],
                reflection_data["reflection"],
                reflection_data["lesson"]
            )

            return entry_id
        except Exception as e:
            print(f"[ERROR] Failed to trigger reflect: {e}")
            return None

    def trigger_from_pipeline(self, pipeline_id: str, stage: str) -> Optional[str]:
        """
        从流水线触发反思
        """
        # 读取流水线文件获取上下文
        pipeline_dir = AUTO_DEV_BASE / "tasks" / "pipeline" / pipeline_id
        pipeline_file = pipeline_dir / f"{pipeline_id}.md"

        if not pipeline_file.exists():
            print(f"[WARN] Pipeline file not found: {pipeline_id}")
            return None

        # 提取相关信息
        with open(pipeline_file, "r", encoding="utf-8") as f:
            content = f.read()

        # 简单处理：直接触发
        return self.trigger_reflect(stage, f"Pipeline {pipeline_id} {STAGES.get(stage, stage)}完成")

    def log_reflect(self, stage: str, result: str, reflect_id: str) -> bool:
        """
        记录反思日志
        """
        log_file = SELF_IMPROVE_DIR / "logs" / "auto_reflect.log"
        log_file.parent.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"{timestamp} | {stage} | {result} | ID: {reflect_id}\n")

        return True


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Auto Reflect Hook - 自动反思触发器")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # reflect命令
    reflect_parser = subparsers.add_parser("reflect", help="手动触发反思")
    reflect_parser.add_argument("stage", choices=list(STAGES.keys()), help="阶段")
    reflect_parser.add_argument("result", help="执行结果")
    reflect_parser.add_argument("--issue", "-i", help="发现的问题")

    # trigger命令
    trigger_parser = subparsers.add_parser("trigger", help="从流水线触发")
    trigger_parser.add_argument("pipeline_id", help="流水线ID")
    trigger_parser.add_argument("stage", choices=list(STAGES.keys()), help="阶段")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    hook = AutoReflectHook()

    if args.command == "reflect":
        result = hook.trigger_reflect(args.stage, args.result, args.issue)
        if result:
            print(f"[OK] Reflect triggered: {result}")
        else:
            print(f"[ERROR] Failed to trigger reflect")

    elif args.command == "trigger":
        result = hook.trigger_from_pipeline(args.pipeline_id, args.stage)
        if result:
            print(f"[OK] Reflect triggered from pipeline: {result}")
        else:
            print(f"[ERROR] Failed to trigger reflect")


if __name__ == "__main__":
    main()
