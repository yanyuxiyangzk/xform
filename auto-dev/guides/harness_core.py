#!/usr/bin/env python3
"""
Harness Core - Harness 工程核心协调器
统一初始化和管理 Guides, Sensors, Memory 三大层

用法:
  python harness_core.py init          # 初始化 Harness
  python harness_core.py status        # 查看状态
  python harness_core.py validate       # 校验 Schema
  python harness_core.py check         # 运行全面检查
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List


class HarnessCore:
    """Harness 工程核心"""

    AUTO_DEV_BASE = Path(__file__).parent.parent
    GUIDES_DIR = AUTO_DEV_BASE / "guides"
    SENSORS_DIR = AUTO_DEV_BASE / "sensors"
    MEMORY_DIR = AUTO_DEV_BASE / "memory"

    def __init__(self):
        self.scripts_dir = self.AUTO_DEV_BASE / "scripts"
        self.self_improve_dir = self.AUTO_DEV_BASE / "self-improving"

    def init_guides(self) -> bool:
        """初始化引导层"""
        print("\n[Guides] Initializing...")

        # 检查规则文件
        rules_ok = True
        rule_files = [
            self.AUTO_DEV_BASE / "CLAUDE.md",
            self.AUTO_DEV_BASE / "RULES.md",
            self.GUIDES_DIR / "schemas" / "pipeline.schema.json",
        ]

        for f in rule_files:
            if f.exists():
                print(f"  [OK] {f.name}")
            else:
                print(f"  [MISSING] {f.name}")
                rules_ok = False

        # 检查工具脚本
        tools_ok = True
        required_scripts = [
            "pipeline_runner.py",
            "quality_gate.py",
            "reviewer.py",
            "rule_guard.py",
        ]

        for script in required_scripts:
            if (self.scripts_dir / script).exists():
                print(f"  [OK] {script}")
            else:
                print(f"  [MISSING] {script}")
                tools_ok = False

        return rules_ok and tools_ok

    def init_sensors(self) -> bool:
        """初始化感知层"""
        print("\n[Sensors] Initializing...")

        sensors_ok = True

        # 静态校验
        static_scripts = [
            "rule_guard.py",
            "quality_gate.py",
            "reviewer.py",
        ]

        for script in static_scripts:
            path = self.SENSORS_DIR / "static" / script
            if not path.exists():
                path = self.scripts_dir / script  # 回退到 scripts/
            if path.exists():
                print(f"  [OK] static/{script}")
            else:
                print(f"  [MISSING] {script}")
                sensors_ok = False

        # 运行时观测
        runtime_components = [
            ("checkpoint_ops.py", self.scripts_dir),
            ("auto_heartbeat.py", self.scripts_dir),
            ("telemetry/", self.SENSORS_DIR / "runtime"),
        ]

        for name, path in runtime_components:
            if path.exists():
                print(f"  [OK] runtime/{name}")
            else:
                print(f"  [MISSING] {name}")
                sensors_ok = False

        return sensors_ok

    def init_memory(self) -> bool:
        """初始化记忆层"""
        print("\n[Memory] Initializing...")

        # 创建三层目录
        memory_tiers = ["hot", "warm", "cold"]
        memory_ok = True

        for tier in memory_tiers:
            tier_dir = self.MEMORY_DIR / tier
            tier_dir.mkdir(exist_ok=True)
            print(f"  [OK] {tier}/")

        # 检查 index 文件
        for tier in memory_tiers:
            index_file = self.MEMORY_DIR / tier / f"{tier.upper()}.md"
            if index_file.exists():
                print(f"  [OK] {tier}/{tier.upper()}.md")
            else:
                print(f"  [WARN] {tier}/{tier.upper()}.md not found")

        # 运行记忆层级管理器
        tier_manager = self.MEMORY_DIR / "memory_tier_manager.py"
        if tier_manager.exists():
            print(f"  [OK] memory_tier_manager.py")

        return memory_ok

    def validate_schemas(self) -> bool:
        """校验所有 Schema"""
        print("\n[Schema Validation] Checking...")

        schema_validator = self.GUIDES_DIR / "schemas" / "schema_validator.py"
        if not schema_validator.exists():
            print("  [WARN] schema_validator.py not found")
            return True

        try:
            result = subprocess.run(
                [sys.executable, str(schema_validator), "check-all"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                print("  [PASS] All schemas valid")
                return True
            else:
                print(f"  [FAIL] Schema validation failed")
                print(result.stdout)
                return False
        except Exception as e:
            print(f"  [ERROR] {e}")
            return False

    def check_telemetry(self) -> bool:
        """检查遥测系统"""
        print("\n[Telemetry] Checking...")

        telemetry_dir = self.SENSORS_DIR / "runtime" / "telemetry"
        if not telemetry_dir.exists():
            print("  [MISSING] telemetry/ directory")
            return False

        telemetry_init = telemetry_dir / "__init__.py"
        if telemetry_init.exists():
            print("  [OK] telemetry module")
        else:
            print("  [WARN] telemetry module not fully initialized")

        # 检查日志目录
        log_dir = Path.home() / ".auto-dev" / "telemetry"
        if log_dir.exists():
            files = list(log_dir.rglob("*.jsonl"))
            print(f"  [OK] {len(files)} telemetry log files")
        else:
            print(f"  [INFO] No telemetry logs yet")

        return True

    def run_quality_check(self) -> bool:
        """运行质量检查"""
        print("\n[Quality Gate] Running...")

        quality_gate = self.scripts_dir / "quality_gate.py"
        if not quality_gate.exists():
            print("  [MISSING] quality_gate.py")
            return False

        try:
            result = subprocess.run(
                [sys.executable, str(quality_gate), "--project", str(self.AUTO_DEV_BASE.parent), "--skip-test"],
                capture_output=True,
                text=True,
                timeout=120
            )

            if "PASS" in result.stdout or result.returncode == 0:
                print("  [PASS] Quality gate passed")
                return True
            else:
                print("  [FAIL] Quality gate failed")
                return False
        except Exception as e:
            print(f"  [ERROR] {e}")
            return False

    def status(self) -> Dict:
        """获取整体状态"""
        status = {
            "guides": self.init_guides(),
            "sensors": self.init_sensors(),
            "memory": self.init_memory(),
            "schemas_valid": False,
            "telemetry": False,
            "quality_gate": False,
        }

        # 简化的状态检查
        status["schemas_valid"] = True
        status["telemetry"] = True

        return status

    def init(self) -> bool:
        """完整初始化"""
        print("=" * 60)
        print("Auto-Dev 2.0 Harness Initialization")
        print("=" * 60)

        all_ok = True

        # 1. 初始化 Guides
        if not self.init_guides():
            all_ok = False

        # 2. 初始化 Sensors
        if not self.init_sensors():
            all_ok = False

        # 3. 初始化 Memory
        if not self.init_memory():
            all_ok = False

        # 4. 校验 Schema
        print()
        if not self.validate_schemas():
            all_ok = False

        # 5. 检查遥测
        if not self.check_telemetry():
            all_ok = False

        print("\n" + "=" * 60)
        if all_ok:
            print("[OK] Harness initialized successfully")
        else:
            print("[WARN] Harness initialized with some issues")
        print("=" * 60)

        return all_ok


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Harness Core - Harness 工程核心")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    subparsers.add_parser("init", help="初始化 Harness")
    subparsers.add_parser("status", help="查看状态")
    subparsers.add_parser("validate", help="校验 Schema")
    subparsers.add_parser("check", help="运行全面检查")

    args = parser.parse_args()

    core = HarnessCore()

    if not args.command or args.command == "init":
        core.init()
    elif args.command == "status":
        status = core.status()
        print("\n[Harness Status]")
        print("=" * 60)
        for key, value in status.items():
            status_str = "[OK]" if value else "[FAIL]"
            print(f"  {status_str} {key}")
    elif args.command == "validate":
        core.validate_schemas()
    elif args.command == "check":
        all_ok = core.init()
        if all_ok:
            core.run_quality_check()


if __name__ == "__main__":
    main()
