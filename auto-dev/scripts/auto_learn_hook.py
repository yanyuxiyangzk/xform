#!/usr/bin/env python3
"""
Auto Learn Hook - 自动学习触发器
检测用户纠正，自动记录到自我改进系统

用法:
  python auto_learn_hook.py check "<user_input>" [--context CONTEXT]
  python auto_learn_hook.py learn "<correction>" --context CONTEXT

触发词检测:
  - "不对" / "不是" / "错了"
  - "应该" / "要这样"
  - "我之前说过" / "记住"
  - "不要" / "停止"
"""

import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Tuple

# 配置
AUTO_DEV_BASE = Path(__file__).parent.parent
SELF_IMPROVE_DIR = AUTO_DEV_BASE / "self-improving"


class AutoLearnHook:
    # 纠正模式
    CORRECTION_PATTERNS = [
        r"不对",
        r"不是\s*(这样|这样)",
        r"错了",
        r"应该\s*是",
        r"要\s*这样",
        r"我之前说过",
        r"记住",
        r"不要\s*再",
        r"停止",
        r"不是\s*的",
        r"其实\s*是",
        r"错了\s*，",
        r"no[,，]?\s*(that's\s*)?not",
        r"actually[,，]?\s*",
        r"you('re| are)\s*(wrong|incorrect)",
    ]

    # 偏好模式
    PREFERENCE_PATTERNS = [
        r"我\s*喜欢",
        r"我\s*希望",
        r"always\s*",
        r"never\s*",
        r"prefer\s*",
        r"我的\s*风格",
    ]

    def __init__(self):
        self.self_improve_ops = AUTO_DEV_BASE / "scripts" / "self_improve_ops.py"

    def check(self, user_input: str) -> Tuple[bool, str]:
        """
        检查用户输入是否包含学习信号
        返回: (is_correction, pattern_type)
        """
        # 检查纠正
        for pattern in self.CORRECTION_PATTERNS:
            if re.search(pattern, user_input, re.IGNORECASE):
                return True, "correction"

        # 检查偏好
        for pattern in self.PREFERENCE_PATTERNS:
            if re.search(pattern, user_input, re.IGNORECASE):
                return True, "preference"

        return False, "none"

    def extract_correction(self, user_input: str) -> str:
        """
        从用户输入中提取纠正内容
        """
        # 简单处理：返回原话
        # 实际可以更智能地提取
        return user_input.strip()

    def is_learn_signal(self, user_input: str) -> bool:
        """
        判断是否是学习信号
        """
        is_correction, _ = self.check(user_input)
        return is_correction

    def trigger_learn(self, user_input: str, context: str = "") -> Optional[str]:
        """
        触发学习
        返回学习记录ID
        """
        # 直接调用，不通过subprocess避免编码问题
        try:
            # 添加scripts目录到path
            import os
            scripts_dir = str(self.self_improve_ops.parent)
            if scripts_dir not in os.sys.path:
                os.sys.path.insert(0, scripts_dir)

            from self_improve_ops import SelfImproveOps

            correction = self.extract_correction(user_input)
            is_correction, ptype = self.check(user_input)

            # 确定类型
            if ptype == "correction":
                pattern_type = "technical"
            elif ptype == "preference":
                pattern_type = "format"
            else:
                pattern_type = "general"

            ops = SelfImproveOps()
            entry_id = ops.learn(correction, pattern_type, context or "auto-detected")

            return entry_id
        except Exception as e:
            print(f"[ERROR] Failed to trigger learn: {e}")
            return None

    def log_learn(self, user_input: str, context: str, result: str) -> bool:
        """
        记录学习结果到日志
        """
        log_file = SELF_IMPROVE_DIR / "logs" / "auto_learn.log"
        log_file.parent.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"{timestamp} | {context} | {user_input[:50]}... | {result}\n")

        return True


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Auto Learn Hook - 自动学习触发器")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # check命令
    check_parser = subparsers.add_parser("check", help="检查是否包含学习信号")
    check_parser.add_argument("user_input", help="用户输入")
    check_parser.add_argument("--context", "-c", default="", help="上下文")

    # learn命令
    learn_parser = subparsers.add_parser("learn", help="触发学习")
    learn_parser.add_argument("correction", help="纠正内容")
    learn_parser.add_argument("--context", "-c", default="auto", help="上下文")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    hook = AutoLearnHook()

    if args.command == "check":
        is_learn, ptype = hook.check(args.user_input)
        if is_learn:
            print(f"[DETECTED] Learning signal: {ptype}")
            print(f"[ACTION] Call: python auto_learn_hook.py learn \"{args.user_input[:50]}...\"")
        else:
            print(f"[CLEAN] No learning signal detected")

    elif args.command == "learn":
        result = hook.trigger_learn(args.correction, args.context)
        if result:
            print(f"[OK] Learn triggered: {result}")
        else:
            print(f"[ERROR] Failed to trigger learn")


if __name__ == "__main__":
    main()
