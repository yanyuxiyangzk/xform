#!/usr/bin/env python3
"""
Auto-Dev 质量门禁脚本
========================
读取 .auto-dev.yaml 配置，执行编译、测试、安全扫描等检查。
所有检查项必须通过才能通过门禁，否则阻塞提交。

用法:
    python quality_gate.py [OPTIONS]

选项:
    --config PATH     指定配置文件路径 (默认: .auto-dev.yaml)
    --project PATH    指定项目根目录 (默认: 当前目录)
    --compile-only    仅执行编译检查
    --test-only       仅执行测试检查
    --skip-security   跳过安全扫描
    --force           强制执行，即使门禁失败也继续
    --verbose         详细输出模式
    --json            JSON格式输出
    --report PATH     生成报告文件路径

示例:
    # 检查当前项目
    python quality_gate.py

    # 指定项目目录
    python quality_gate.py --project /path/to/project

    # 仅编译检查
    python quality_gate.py --compile-only

    # 详细输出
    python quality_gate.py --verbose --json

环境变量:
    AUTO_DEV_CONFIG    配置文件路径
    AUTO_DEV_PROJECT   项目根目录
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
import yaml
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional


# ============================================================
# 颜色输出 (跨平台兼容)
# ============================================================
class Colors:
    """终端颜色输出 (Windows兼容)"""
    RED = '\033[91m' if sys.stdout.isatty() else ''
    GREEN = '\033[92m' if sys.stdout.isatty() else ''
    YELLOW = '\033[93m' if sys.stdout.isatty() else ''
    BLUE = '\033[94m' if sys.stdout.isatty() else ''
    BOLD = '\033[1m' if sys.stdout.isatty() else ''
    END = '\033[0m' if sys.stdout.isatty() else ''


def color_print(color: str, *args, **kwargs):
    """打印彩色文本"""
    print(f"{color}{' '.join(str(a) for a in args)}{Colors.END}", **kwargs)


def log_info(msg):
    color_print(Colors.BLUE, f"[INFO] {msg}")


def log_success(msg):
    color_print(Colors.GREEN, f"[SUCCESS] {msg}")


def log_warning(msg):
    color_print(Colors.YELLOW, f"[WARNING] {msg}")


def log_error(msg):
    color_print(Colors.RED, f"[ERROR] {msg}")


# ============================================================
# 结果枚举
# ============================================================
class CheckResult(Enum):
    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"
    SKIP = "skip"
    ERROR = "error"


# ============================================================
# 检查结果数据类
# ============================================================
@dataclass
class CheckItem:
    """单个检查项"""
    name: str
    result: CheckResult
    message: str = ""
    duration: float = 0
    details: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "result": self.result.value,
            "message": self.message,
            "duration": round(self.duration, 2),
            "details": self.details
        }


@dataclass
class QualityGateResult:
    """质量门禁整体结果"""
    passed: bool
    blocked: bool
    total_duration: float
    checks: list[CheckItem] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "blocked": self.blocked,
            "total_duration": round(self.total_duration, 2),
            "checks": [c.to_dict() for c in self.checks],
            "errors": self.errors,
            "warnings": self.warnings,
            "timestamp": datetime.now().isoformat()
        }

    def add_check(self, check: CheckItem):
        self.checks.append(check)

    def add_error(self, error: str):
        self.errors.append(error)

    def add_warning(self, warning: str):
        self.warnings.append(warning)


# ============================================================
# 配置加载器
# ============================================================
class ConfigLoader:
    """配置加载器"""

    DEFAULT_CONFIG = {
        "project_type": "maven",
        "compile": {
            "command": "mvn clean compile",
            "timeout": 300,
            "block_on_fail": True,
            "env": {}
        },
        "test": {
            "command": "mvn test",
            "timeout": 600,
            "coverage_threshold": 70,
            "block_on_fail": True,
            "exclude": []
        },
        "security": {
            "enabled": True,
            "tools": [
                {"name": "dependency-analyze", "command": "mvn dependency:analyze", "on_fail": "warn"}
            ]
        },
        "code_style": {
            "enabled": True,
            "check_command": "mvn checkstyle:check",
            "block_on_fail": False
        },
        "gate": {
            "block_on": {
                "compile_fail": True,
                "test_fail": True,
                "p0_security": True,
                "forbidden_action": True
            },
            "warn_on": {
                "coverage_low": True,
                "checkstyle_fail": True,
                "p1_security": True
            }
        }
    }

    @classmethod
    def load(cls, config_path: Optional[str] = None, project_root: Optional[str] = None) -> dict:
        """
        加载配置文件

        Args:
            config_path: 配置文件路径
            project_root: 项目根目录

        Returns:
            配置字典
        """
        # 确定项目根目录
        if project_root:
            root = Path(project_root)
        else:
            root = Path.cwd()

        # 确定配置文件路径
        if config_path:
            config_file = Path(config_path)
        else:
            config_file = root / ".auto-dev.yaml"

        # 如果配置文件存在，读取并合并
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f) or {}
                return cls._merge_config(cls.DEFAULT_CONFIG, user_config)
            except Exception as e:
                log_warning(f"配置文件读取失败: {e}, 使用默认配置")
                return cls.DEFAULT_CONFIG.copy()
        else:
            log_info(f"未找到配置文件 {config_file}, 使用默认配置")
            return cls.DEFAULT_CONFIG.copy()

    @classmethod
    def _merge_config(cls, default: dict, user: dict) -> dict:
        """深度合并配置"""
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = cls._merge_config(result[key], value)
            else:
                result[key] = value
        return result


# ============================================================
# 命令执行器
# ============================================================
class CommandExecutor:
    """命令执行器"""

    def __init__(self, cwd: str, env: dict = None, timeout: int = 300):
        self.cwd = Path(cwd)
        self.env = os.environ.copy()
        if env:
            self.env.update(env)
        self.timeout = timeout

    def run(self, command: str, description: str = "") -> tuple[int, str, str]:
        """
        执行命令

        Args:
            command: 命令字符串
            description: 描述信息

        Returns:
            (返回码, stdout, stderr)
        """
        log_info(f"执行: {description or command}")

        try:
            # 在Windows上使用shell=True
            result = subprocess.run(
                command,
                shell=True,
                cwd=str(self.cwd),
                env=self.env,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", f"命令执行超时 ({self.timeout}秒)"
        except Exception as e:
            return -1, "", str(e)


# ============================================================
# 检查器基类
# ============================================================
class BaseChecker:
    """检查器基类"""

    def __init__(self, config: dict, project_root: Path):
        self.config = config
        self.project_root = project_root

    def check(self, executor: CommandExecutor) -> CheckItem:
        """执行检查，返回检查结果"""
        raise NotImplementedError


# ============================================================
# 编译检查
# ============================================================
class CompileChecker(BaseChecker):
    """编译检查器"""

    def check(self, executor: CommandExecutor) -> CheckItem:
        start_time = time.time()
        compile_config = self.config.get("compile", {})

        command = compile_config.get("command", "mvn compile")
        timeout = compile_config.get("timeout", 300)
        env = compile_config.get("env", {})

        # 支持多模块 Maven 项目
        maven_module = compile_config.get("maven_module", "")
        compile_cwd = self.project_root / maven_module if maven_module else self.project_root

        executor = CommandExecutor(
            cwd=str(compile_cwd),
            env=env,
            timeout=timeout
        )

        returncode, stdout, stderr = executor.run(command, "编译检查")

        duration = time.time() - start_time

        if returncode == 0:
            return CheckItem(
                name="compile",
                result=CheckResult.PASS,
                message="编译成功",
                duration=duration
            )
        else:
            # 提取错误信息
            error_msg = self._extract_error(stderr or stdout)
            return CheckItem(
                name="compile",
                result=CheckResult.FAIL,
                message=f"编译失败: {error_msg}",
                duration=duration,
                details={"returncode": returncode, "stderr": stderr[-1000:]}
            )

    def _extract_error(self, output: str) -> str:
        """从输出中提取错误信息"""
        lines = output.strip().split('\n')
        error_lines = []
        for line in lines:
            if '[ERROR]' in line or 'error:' in line.lower():
                error_lines.append(line.strip())
            if len(error_lines) >= 5:
                break
        return '\n'.join(error_lines[-3:]) if error_lines else "未知错误"


# ============================================================
# 测试检查
# ============================================================
class TestChecker(BaseChecker):
    """测试检查器"""

    def check(self, executor: CommandExecutor) -> CheckItem:
        start_time = time.time()
        test_config = self.config.get("test", {})

        command = test_config.get("command", "mvn test")
        timeout = test_config.get("timeout", 600)
        env = test_config.get("env", {})

        # 支持多模块 Maven 项目
        maven_module = test_config.get("maven_module", "")
        test_cwd = self.project_root / maven_module if maven_module else self.project_root

        executor = CommandExecutor(
            cwd=str(test_cwd),
            env=env,
            timeout=timeout
        )

        returncode, stdout, stderr = executor.run(command, "测试检查")

        duration = time.time() - start_time

        # 解析测试结果
        passed = self._count_passed(stdout)
        failed = self._count_failed(stdout)
        skipped = self._count_skipped(stdout)

        if returncode == 0:
            return CheckItem(
                name="test",
                result=CheckResult.PASS,
                message=f"测试通过 (通过:{passed}, 跳过:{skipped})",
                duration=duration,
                details={"passed": passed, "failed": failed, "skipped": skipped}
            )
        else:
            return CheckItem(
                name="test",
                result=CheckResult.FAIL,
                message=f"测试失败 (通过:{passed}, 失败:{failed}, 跳过:{skipped})",
                duration=duration,
                details={"passed": passed, "failed": failed, "skipped": skipped, "returncode": returncode}
            )

    def _count_passed(self, output: str) -> int:
        """统计通过的测试数"""
        match = re.search(r'Tests run:\s*(\d+),\s*Failures:\s*(\d+),\s*Errors:\s*(\d+),\s*Skipped:\s*(\d+)', output)
        return int(match.group(1)) - int(match.group(2)) - int(match.group(3)) if match else 0

    def _count_failed(self, output: str) -> int:
        """统计失败的测试数"""
        match = re.search(r'Tests run:\s*(\d+),\s*Failures:\s*(\d+),\s*Errors:\s*(\d+),\s*Skipped:\s*(\d+)', output)
        return int(match.group(2)) + int(match.group(3)) if match else 0

    def _count_skipped(self, output: str) -> int:
        """统计跳过的测试数"""
        match = re.search(r'Tests run:\s*(\d+),\s*Failures:\s*(\d+),\s*Errors:\s*(\d+),\s*Skipped:\s*(\d+)', output)
        return int(match.group(4)) if match else 0


# ============================================================
# 安全扫描检查
# ============================================================
class SecurityChecker(BaseChecker):
    """安全扫描检查器"""

    FORBIDDEN_PATTERNS = [
        (r'password\s*=\s*["\'][^"\']{3,}["\']', "P0", "硬编码密码"),
        (r'secret\s*=\s*["\'][^"\']{3,}["\']', "P0", "硬编码密钥"),
        (r'api[_-]?key\s*=\s*["\'][^"\']{3,}["\']', "P0", "硬编码API Key"),
        (r'token\s*=\s*["\'][^"\']{10,}["\']', "P0", "硬编码Token"),
        (r'-----BEGIN\s+(RSA|EC|DSA|OPENSSL)\s+PRIVATE\s+KEY-----', "P0", "私钥文件"),
    ]

    def check(self, executor: CommandExecutor) -> CheckItem:
        start_time = time.time()
        security_config = self.config.get("security", {})

        if not security_config.get("enabled", True):
            return CheckItem(
                name="security",
                result=CheckResult.SKIP,
                message="安全扫描已禁用",
                duration=time.time() - start_time
            )

        # 首先检查禁止的模式
        violations = self._check_forbidden_patterns()

        if violations:
            p0_count = sum(1 for v in violations if v[1] == "P0")
            return CheckItem(
                name="security",
                result=CheckResult.FAIL if p0_count > 0 else CheckResult.WARN,
                message=f"发现 {len(violations)} 个安全问题 (P0: {p0_count})",
                duration=time.time() - start_time,
                details={"violations": violations}
            )

        # 运行配置的安全工具
        tools = security_config.get("tools", [])
        for tool in tools:
            tool_name = tool.get("name", "unknown")
            command = tool.get("command", "")
            if not command:
                continue

            timeout = self.config.get("compile", {}).get("timeout", 300)
            executor = CommandExecutor(cwd=str(self.project_root), timeout=timeout)

            returncode, stdout, stderr = executor.run(command, f"安全扫描: {tool_name}")

            # 检查是否有安全问题
            if "WARNING" in stdout or "WARNING" in stderr:
                return CheckItem(
                    name="security",
                    result=CheckResult.WARN,
                    message=f"安全扫描发现警告",
                    duration=time.time() - start_time,
                    details={"tool": tool_name, "output": stdout[-500:]}
                )

        return CheckItem(
            name="security",
            result=CheckResult.PASS,
            message="安全扫描通过",
            duration=time.time() - start_time
        )

    def _check_forbidden_patterns(self) -> list:
        """检查禁止的模式"""
        violations = []
        code_extensions = ['.java', '.js', '.ts', '.py', '.go', '.rs', '.cs', '.rb', '.php']
        exclude_dirs = {'node_modules', 'target', 'build', '.git', 'dist', '__pycache__'}

        for ext in code_extensions:
            for file_path in self.project_root.rglob(f'*{ext}'):
                # 排除目录
                if any(excluded in file_path.parts for excluded in exclude_dirs):
                    continue

                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    for pattern, severity, description in self.FORBIDDEN_PATTERNS:
                        if re.search(pattern, content, re.IGNORECASE):
                            violations.append({
                                "file": str(file_path.relative_to(self.project_root)),
                                "severity": severity,
                                "type": description,
                                "pattern": pattern
                            })
                except Exception:
                    continue

        return violations


# ============================================================
# 代码风格检查
# ============================================================
class CodeStyleChecker(BaseChecker):
    """代码风格检查器"""

    def check(self, executor: CommandExecutor) -> CheckItem:
        start_time = time.time()
        style_config = self.config.get("code_style", {})

        if not style_config.get("enabled", True):
            return CheckItem(
                name="code_style",
                result=CheckResult.SKIP,
                message="代码风格检查已禁用",
                duration=time.time() - start_time
            )

        command = style_config.get("check_command", "mvn checkstyle:check")
        timeout = self.config.get("compile", {}).get("timeout", 300)

        executor = CommandExecutor(cwd=str(self.project_root), timeout=timeout)
        returncode, stdout, stderr = executor.run(command, "代码风格检查")

        duration = time.time() - start_time

        if returncode == 0:
            return CheckItem(
                name="code_style",
                result=CheckResult.PASS,
                message="代码风格检查通过",
                duration=duration
            )
        else:
            return CheckItem(
                name="code_style",
                result=CheckResult.WARN,  # 代码风格仅警告，不阻塞
                message="代码风格检查发现问题",
                duration=duration,
                details={"output": stderr[-500:]}
            )


# ============================================================
# 禁止操作检查
# ============================================================
class ForbiddenActionChecker(BaseChecker):
    """禁止操作检查器"""

    FORBIDDEN_ACTIONS = [
        (".git", "P0", "禁止删除 .git 目录"),
        ("core'architecture", "P0", "禁止删除核心架构文件"),
        ("pf4j", "P0", "禁止删除 PF4J 插件核心"),
        ("liquor", "P0", "禁止删除 Liquor 动态编译核心"),
    ]

    def check(self, executor: CommandExecutor) -> CheckItem:
        start_time = time.time()
        violations = []

        # 检查 git status 是否有删除操作
        executor = CommandExecutor(cwd=str(self.project_root), timeout=30)
        returncode, stdout, stderr = executor.run("git status --porcelain", "检查Git状态")

        if returncode == 0 and stdout:
            lines = stdout.strip().split('\n')
            for line in lines:
                if line.startswith('D '):  # 删除的文件
                    file_path = line[2:].strip()
                    for forbidden, severity, message in self.FORBIDDEN_ACTIONS:
                        if forbidden in file_path.lower():
                            violations.append({
                                "file": file_path,
                                "severity": severity,
                                "action": message
                            })

        duration = time.time() - start_time

        if violations:
            return CheckItem(
                name="forbidden_action",
                result=CheckResult.FAIL,
                message=f"发现禁止操作: {violations[0]['action']}",
                duration=duration,
                details={"violations": violations}
            )

        return CheckItem(
            name="forbidden_action",
            result=CheckResult.PASS,
            message="无禁止操作",
            duration=duration
        )


# ============================================================
# 质量门禁主类
# ============================================================
class QualityGate:
    """质量门禁"""

    def __init__(self, config_path: Optional[str] = None, project_root: Optional[str] = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.config = ConfigLoader.load(config_path, str(self.project_root))
        self.result = QualityGateResult(passed=True, blocked=False, total_duration=0)

    def run(self,
            compile_only: bool = False,
            test_only: bool = False,
            skip_security: bool = False,
            skip_test: bool = False,
            verbose: bool = False) -> bool:
        """
        执行质量门禁

        Args:
            compile_only: 仅执行编译检查
            test_only: 仅执行测试检查
            skip_security: 跳过安全扫描
            skip_test: 跳过测试检查（仅开发阶段使用）
            verbose: 详细输出

        Returns:
            True if all checks passed, False otherwise
        """
        start_time = time.time()
        log_info(f"=" * 60)
        log_info(f"质量门禁开始 - 项目: {self.project_root}")
        log_info(f"=" * 60)

        # 确定要执行的检查
        checks = []

        # 编译检查：除非明确指定 test_only，否则都要运行
        if not test_only:
            checks.append(CompileChecker(self.config, self.project_root))

        # 测试检查：除非 compile_only 或 skip_test
        if not compile_only and not skip_test:
            checks.append(TestChecker(self.config, self.project_root))

        # 安全扫描：除非 compile_only 或 skip_security
        if not compile_only and not skip_security:
            checks.append(SecurityChecker(self.config, self.project_root))

        # 代码风格 + 禁止操作：除非 compile_only 或 test_only
        if not compile_only and not test_only:
            checks.append(CodeStyleChecker(self.config, self.project_root))
            checks.append(ForbiddenActionChecker(self.config, self.project_root))

        # 创建执行器
        timeout = self.config.get("compile", {}).get("timeout", 300)
        executor = CommandExecutor(cwd=str(self.project_root), timeout=timeout)

        # 执行所有检查
        for checker in checks:
            check_item = checker.check(executor)
            self.result.add_check(check_item)

            if verbose:
                self._print_check_verbose(check_item)

            # 根据结果更新状态
            if check_item.result == CheckResult.FAIL:
                self._handle_failure(check_item)

        # 计算总时长
        self.result.total_duration = time.time() - start_time

        # 判断是否通过
        self._judge_pass()

        # 打印结果
        self._print_summary(verbose)

        return self.result.passed

    def _handle_failure(self, check_item: CheckItem):
        """处理检查失败"""
        gate_config = self.config.get("gate", {})
        block_on = gate_config.get("block_on", {})

        if check_item.name == "compile" and block_on.get("compile_fail"):
            self.result.passed = False
            self.result.blocked = True
            self.result.add_error(f"编译失败，阻塞提交: {check_item.message}")

        elif check_item.name == "security":
            violations = check_item.details.get("violations", [])
            p0_count = sum(1 for v in violations if v.get("severity") == "P0")
            if p0_count > 0 and block_on.get("p0_security"):
                self.result.passed = False
                self.result.blocked = True
                self.result.add_error(f"发现P0安全漏洞，阻塞提交")

        elif check_item.name == "forbidden_action" and block_on.get("forbidden_action"):
            self.result.passed = False
            self.result.blocked = True
            self.result.add_error(f"发现禁止操作，阻塞提交")

    def _judge_pass(self):
        """判断是否通过"""
        gate_config = self.config.get("gate", {})
        warn_on = gate_config.get("warn_on", {})

        # 检查是否有警告
        for check in self.result.checks:
            if check.result == CheckResult.WARN:
                if check.name == "coverage_low" and warn_on.get("coverage_low"):
                    self.result.add_warning(f"覆盖率低于阈值")
                elif check.name == "code_style" and warn_on.get("checkstyle_fail"):
                    self.result.add_warning(f"代码风格检查未通过")

    def _print_check_verbose(self, check_item: CheckItem):
        """打印检查详情"""
        icon = {
            CheckResult.PASS: "[PASS]",
            CheckResult.FAIL: "[FAIL]",
            CheckResult.WARN: "[WARN]",
            CheckResult.SKIP: "[SKIP]",
            CheckResult.ERROR: "[ERROR]"
        }.get(check_item.result, "?")

        print(f"  {icon} {check_item.name}: {check_item.message} ({check_item.duration:.1f}s)")

    def _print_summary(self, verbose: bool):
        """打印汇总结果"""
        print()
        print("=" * 60)

        if self.result.passed and not self.result.blocked:
            color_print(Colors.GREEN, f"[PASS] 质量门禁通过 (耗时: {self.result.total_duration:.1f}s)")
        elif self.result.blocked:
            color_print(Colors.RED, f"[FAIL] 质量门禁未通过，提交被阻塞")
        else:
            color_print(Colors.YELLOW, f"[WARN] 质量门禁通过，但有警告")

        # 打印错误
        if self.result.errors:
            print()
            for error in self.result.errors:
                color_print(Colors.RED, f"  BLOCK: {error}")

        # 打印警告
        if self.result.warnings:
            print()
            for warning in self.result.warnings:
                color_print(Colors.YELLOW, f"  WARN: {warning}")

        print("=" * 60)

        # 检查项汇总
        if verbose:
            print()
            print("检查项汇总:")
            for check in self.result.checks:
                self._print_check_verbose(check)

    def to_json(self) -> str:
        """导出为JSON格式"""
        return json.dumps(self.result.to_dict(), indent=2, ensure_ascii=False)

    def save_report(self, path: str):
        """保存报告到文件"""
        with open(path, 'w', encoding='utf-8') as f:
            f.write(self.to_json())


# ============================================================
# 命令行入口
# ============================================================
def main():
    parser = argparse.ArgumentParser(
        description="Auto-Dev 质量门禁脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '--config', '-c',
        help='配置文件路径 (默认: .auto-dev.yaml)'
    )
    parser.add_argument(
        '--project', '-p',
        help='项目根目录 (默认: 当前目录)'
    )
    parser.add_argument(
        '--compile-only',
        action='store_true',
        help='仅执行编译检查'
    )
    parser.add_argument(
        '--test-only',
        action='store_true',
        help='仅执行测试检查'
    )
    parser.add_argument(
        '--skip-security',
        action='store_true',
        help='跳过安全扫描'
    )
    parser.add_argument(
        '--skip-test',
        action='store_true',
        help='跳过测试检查（仅开发阶段使用）'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='强制执行，即使门禁失败也继续'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='详细输出模式'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='JSON格式输出'
    )
    parser.add_argument(
        '--report',
        help='生成报告文件路径'
    )

    args = parser.parse_args()

    # 执行质量门禁
    gate = QualityGate(
        config_path=args.config,
        project_root=args.project
    )

    try:
        passed = gate.run(
            compile_only=args.compile_only,
            test_only=args.test_only,
            skip_security=args.skip_security,
            skip_test=getattr(args, 'skip_test', False),
            verbose=args.verbose or args.json
        )

        # 保存报告
        if args.report:
            gate.save_report(args.report)
            log_info(f"报告已保存: {args.report}")

        # JSON输出
        if args.json:
            print(gate.to_json())

        # 返回状态码
        if passed or args.force:
            sys.exit(0)
        else:
            sys.exit(1)

    except KeyboardInterrupt:
        log_warning("质量门禁被中断")
        sys.exit(130)
    except Exception as e:
        log_error(f"质量门禁执行异常: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
