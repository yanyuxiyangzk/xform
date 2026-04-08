#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码审核脚本 - Auto-Dev Reviewer
基于 .auto-dev.yaml 配置执行代码审核
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional


class ReviewStatus(Enum):
    APPROVED = "APPROVED"           # 审核通过
    REVISION_REQUESTED = "REVISION_REQUESTED"  # 需要修改
    REJECTED = "REJECTED"           # 审核拒绝


class Severity(Enum):
    CRITICAL = "CRITICAL"
    MAJOR = "MAJOR"
    MINOR = "MINOR"
    INFO = "INFO"


@dataclass
class ReviewComment:
    severity: Severity
    category: str
    message: str
    file: Optional[str] = None
    line: Optional[int] = None
    rule_id: Optional[str] = None

    def to_dict(self):
        return {
            "severity": self.severity.value,
            "category": self.category,
            "message": self.message,
            "file": self.file,
            "line": self.line,
            "rule_id": self.rule_id
        }


@dataclass
class ReviewResult:
    status: ReviewStatus
    iteration: int
    max_iterations: int
    comments: list[ReviewComment] = field(default_factory=list)
    passed_checks: list[str] = field(default_factory=list)
    failed_checks: list[str] = field(default_factory=list)
    duration: float = 0.0

    @property
    def has_critical(self) -> bool:
        return any(c.severity == Severity.CRITICAL for c in self.comments)

    @property
    def has_major(self) -> bool:
        return any(c.severity == Severity.MAJOR for c in self.comments)


class Colors:
    RED = '\033[91m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    CYAN = '\033[96m'


def color_text(text: str, color: str) -> str:
    return f"{color}{text}{Colors.RESET}"


class ConfigLoader:
    """加载 .auto-dev.yaml 配置文件"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.config = {}
        self._load()

    def _load(self):
        config_file = self.project_root / ".auto-dev.yaml"
        if not config_file.exists():
            print(f"Warning: {config_file} not found, using defaults")
            return

        import yaml
        with open(config_file, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f) or {}

    @property
    def reviewer_enabled(self) -> bool:
        rev = self.config.get('reviewer', {})
        return rev.get('enabled', True)

    @property
    def max_iterations(self) -> int:
        rev = self.config.get('reviewer', {})
        return rev.get('max_iterations', 3)

    @property
    def required_approvals(self) -> int:
        rev = self.config.get('reviewer', {})
        return rev.get('required_approvals', 1)

    @property
    def standards(self) -> dict:
        rev = self.config.get('reviewer', {})
        return rev.get('standards', {})


class CommandExecutor:
    """命令执行器"""

    def __init__(self, timeout: int = 300, verbose: bool = False):
        self.timeout = timeout
        self.verbose = verbose

    def run(self, command: str, cwd: str = ".") -> tuple[int, str, str]:
        """执行命令，返回 (returncode, stdout, stderr)"""
        if self.verbose:
            print(f"  Executing: {command}")

        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", f"Command timeout after {self.timeout}s"
        except Exception as e:
            return -1, "", str(e)


class NamingConventionChecker:
    """命名规范检查器"""

    TOOL_NAME = "naming-convention"

    # Java命名规范
    JAVA_PATTERNS = {
        'class': re.compile(r'^[A-Z][a-zA-Z0-9]*$'),
        'interface': re.compile(r'^[A-Z][a-zA-Z0-9]*$'),
        'method': re.compile(r'^[a-z][a-zA-Z0-9]*$'),
        'variable': re.compile(r'^[a-z][a-zA-Z0-9]*$'),
        'constant': re.compile(r'^[A-Z][A-Z0-9_]*$'),
        'enum': re.compile(r'^[A-Z][a-zA-Z0-9]*$'),
    }

    # 文件名规范
    FILENAME_PATTERNS = {
        'java': re.compile(r'^[A-Z][a-zA-Z0-9]*\.java$'),
        'xml': re.compile(r'^[a-z][a-z0-9]*\.xml$'),
        'yaml': re.compile(r'^[a-z][a-z0-9]*\.ya?ml$'),
        'properties': re.compile(r'^[a-z][a-z0-9]*\.properties$'),
    }

    # 常见错误命名
    BAD_PATTERNS = [
        (re.compile(r'^[a-z]$'), "变量名太短"),
        (re.compile(r'.*[A-Z][A-Z]+.*'), "变量名包含连续大写"),
        (re.compile(r'.*_[a-z].*'), "变量名以下划线开头"),
        (re.compile(r'.*__.*'), "变量名包含双下划线"),
    ]

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.ignore_dirs = {'target', 'node_modules', '.git', 'dist', 'build', '.mvn'}

    def check(self) -> tuple[list[ReviewComment], list[str]]:
        comments = []
        passed = []

        # 检查Java文件
        for java_file in self.project_root.rglob('*.java'):
            if any(ignore in java_file.parts for ignore in self.ignore_dirs):
                continue

            file_name = java_file.name
            class_name = file_name[:-5]  # 去掉.java

            # 检查类名
            if not self.JAVA_PATTERNS['class'].match(class_name):
                # 可能是内部类或者常见模式
                if '$' in class_name:  # 内部类
                    passed.append(f"{file_name} (内部类)")
                    continue

                comments.append(ReviewComment(
                    severity=Severity.MINOR,
                    category=self.TOOL_NAME,
                    message=f"类名 '{class_name}' 不符合PascalCase规范",
                    file=str(java_file.relative_to(self.project_root)),
                    rule_id="java-class-naming"
                ))
            else:
                passed.append(f"{file_name} (类名)")

            # 检查文件内容中的命名
            try:
                content = java_file.read_text(encoding='utf-8', errors='ignore')
                lines = content.split('\n')

                for line_num, line in enumerate(lines, 1):
                    line = line.strip()

                    # 检查方法命名
                    method_match = re.search(r'(public|private|protected)?\s+(static)?\s+\w+\s+(\w+)\s*\(', line)
                    if method_match:
                        method_name = method_match.group(3)
                        if not self.JAVA_PATTERNS['method'].match(method_name) and method_name != 'main':
                            comments.append(ReviewComment(
                                severity=Severity.MINOR,
                                category=self.TOOL_NAME,
                                message=f"方法名 '{method_name}' 不符合camelCase规范",
                                file=str(java_file.relative_to(self.project_root)),
                                line=line_num,
                                rule_id="java-method-naming"
                            ))

                    # 检查变量命名
                    var_match = re.search(r'(private|public|protected)?\s+(final)?\s+(static)?\s+\w+\s+(\w+)\s*=', line)
                    if var_match:
                        var_name = var_match.group(4)
                        if var_name and not self.JAVA_PATTERNS['variable'].match(var_name):
                            comments.append(ReviewComment(
                                severity=Severity.MINOR,
                                category=self.TOOL_NAME,
                                message=f"变量名 '{var_name}' 不符合camelCase规范",
                                file=str(java_file.relative_to(self.project_root)),
                                line=line_num,
                                rule_id="java-variable-naming"
                            ))

            except Exception:
                continue

        return comments, passed


class JavadocChecker:
    """Javadoc检查器"""

    TOOL_NAME = "javadoc"

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.ignore_dirs = {'target', 'node_modules', '.git', 'dist', 'build'}

    def check(self) -> tuple[list[ReviewComment], list[str]]:
        comments = []
        passed = []

        for java_file in self.project_root.rglob('*.java'):
            if any(ignore in java_file.parts for ignore in self.ignore_dirs):
                continue

            try:
                content = java_file.read_text(encoding='utf-8', errors='ignore')

                # 检查是否有Javadoc注释
                has_javadoc = re.search(r'/\*\*[\s\S]*?\*/', content) is not None

                # 检查public class
                is_public_class = re.search(r'public\s+class\s+\w+', content) is not None
                is_public_method = re.search(r'public\s+\w+\s+\w+\s*\([^\)]*\)', content) is not None

                if is_public_class and not has_javadoc:
                    # 只对公共类要求Javadoc
                    class_name = java_file.stem
                    comments.append(ReviewComment(
                        severity=Severity.INFO,
                        category=self.TOOL_NAME,
                        message=f"公共类 '{class_name}' 缺少Javadoc文档注释",
                        file=str(java_file.relative_to(self.project_root)),
                        rule_id="javadoc-required"
                    ))
                elif has_javadoc:
                    passed.append(f"{java_file.stem} (有Javadoc)")
                else:
                    passed.append(f"{java_file.stem} (非公共类)")

            except Exception:
                continue

        return comments, passed


class HardcodedSecretChecker:
    """硬编码密钥检查器"""

    TOOL_NAME = "hardcoded-secret"

    SECRET_PATTERNS = [
        (re.compile(r'password\s*=\s*["\'][^"\']{3,}["\']', re.IGNORECASE), "password"),
        (re.compile(r'secret\s*=\s*["\'][^"\']{3,}["\']', re.IGNORECASE), "secret"),
        (re.compile(r'token\s*=\s*["\'][a-zA-Z0-9\-_.]{10,}["\']', re.IGNORECASE), "token"),
        (re.compile(r'api_key\s*=\s*["\'][a-zA-Z0-9\-_.]{10,}["\']', re.IGNORECASE), "api_key"),
        (re.compile(r'apiKey\s*=\s*["\'][a-zA-Z0-9\-_.]{10,}["\']', re.IGNORECASE), "apiKey"),
        (re.compile(r'Bearer\s+[a-zA-Z0-9\-_.]+', re.IGNORECASE), "Bearer token"),
        (re.compile(r'sk_[a-zA-Z0-9]{20,}', re.IGNORECASE), "OpenAI API Key"),
    ]

    # 允许的配置文件
    ALLOWED_FILES = ['application.yml', 'application.yaml', 'application.properties',
                     'application-dev.yml', 'application-prod.yml',
                     'config.yaml', 'config.yml']

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.ignore_dirs = {'target', 'node_modules', '.git', 'dist', 'build', '.mvn'}

    def check(self) -> tuple[list[ReviewComment], list[str]]:
        comments = []
        passed = []

        for java_file in self.project_root.rglob('*.java'):
            if any(ignore in java_file.parts for ignore in self.ignore_dirs):
                continue

            # 跳过测试文件
            if 'test' in java_file.parts:
                passed.append(f"{java_file.stem} (测试文件)")
                continue

            try:
                content = java_file.read_text(encoding='utf-8', errors='ignore')
                lines = content.split('\n')

                for line_num, line in enumerate(lines, 1):
                    # 跳过注释行
                    stripped = line.strip()
                    if stripped.startswith('//') or stripped.startswith('*') or stripped.startswith('#'):
                        continue

                    for pattern, secret_type in self.SECRET_PATTERNS:
                        if pattern.search(line):
                            comments.append(ReviewComment(
                                severity=Severity.CRITICAL,
                                category=self.TOOL_NAME,
                                message=f"发现硬编码密钥: {secret_type}",
                                file=str(java_file.relative_to(self.project_root)),
                                line=line_num,
                                rule_id="hardcoded-secret"
                            ))
                            break

            except Exception:
                continue

        # 检查配置文件
        for config_file in self.project_root.rglob('*.yml'):
            if any(ignore in config_file.parts for ignore in self.ignore_dirs):
                continue

            if config_file.name not in self.ALLOWED_FILES:
                continue

            try:
                content = config_file.read_text(encoding='utf-8', errors='ignore')

                for line_num, line in enumerate(lines, 1):
                    for pattern, secret_type in self.SECRET_PATTERNS:
                        if pattern.search(line):
                            comments.append(ReviewComment(
                                severity=Severity.MAJOR,
                                category=self.TOOL_NAME,
                                message=f"配置文件中发现密钥: {secret_type} (建议使用环境变量)",
                                file=str(config_file.relative_to(self.project_root)),
                                line=line_num,
                                rule_id="config-secret"
                            ))
                            break

            except Exception:
                continue

        if not comments:
            passed.append("无硬编码密钥")

        return comments, passed


class TestCoverageChecker:
    """测试覆盖率检查器"""

    TOOL_NAME = "test-coverage"

    def __init__(self, executor: CommandExecutor, project_root: str = "."):
        self.executor = executor
        self.project_root = Path(project_root)

    def check(self, threshold: float = 70.0) -> tuple[list[ReviewComment], list[str]]:
        comments = []
        passed = []

        # 检查是否有测试目录
        test_dir = self.project_root / "src" / "test"
        if not test_dir.exists():
            comments.append(ReviewComment(
                severity=Severity.MAJOR,
                category=self.TOOL_NAME,
                message="项目缺少测试目录 src/test",
                rule_id="missing-test-dir"
            ))
            return comments, passed

        # 检查测试文件数量
        test_files = list(test_dir.rglob('*Test.java'))
        main_files = list((self.project_root / "src" / "main").rglob('*.java'))

        if main_files and not test_files:
            comments.append(ReviewComment(
                severity=Severity.MAJOR,
                category=self.TOOL_NAME,
                message="项目缺少单元测试",
                rule_id="missing-unit-tests"
            ))
            return comments, passed

        if len(test_files) < len(main_files) * 0.3:
            comments.append(ReviewComment(
                severity=Severity.MINOR,
                category=self.TOOL_NAME,
                message=f"测试文件数量较少: {len(test_files)} 测试 vs {len(main_files)} 源码",
                rule_id="low-test-count"
            ))

        # 尝试运行测试覆盖率
        returncode, stdout, stderr = self.executor.run(
            "mvn test jacoco:report -q",
            str(self.project_root)
        )

        # 解析覆盖率
        coverage_file = self.project_root / "target" / "site" / "jacoco" / "index.html"
        if coverage_file.exists():
            try:
                content = coverage_file.read_text(encoding='utf-8', errors='ignore')
                # 简单解析 - 实际应该用XML
                coverage_match = re.search(r'Total.*?(\d+)%', content)
                if coverage_match:
                    coverage = int(coverage_match.group(1))
                    if coverage < threshold:
                        comments.append(ReviewComment(
                            severity=Severity.MAJOR,
                            category=self.TOOL_NAME,
                            message=f"测试覆盖率不足: {coverage}% (要求: {threshold}%)",
                            rule_id="coverage-below-threshold"
                        ))
                    else:
                        passed.append(f"测试覆盖率: {coverage}%")
            except Exception:
                pass
        else:
            passed.append(f"测试文件数: {len(test_files)}")

        return comments, passed


class ComplexityChecker:
    """代码复杂度检查器"""

    TOOL_NAME = "complexity"

    MAX_METHOD_LENGTH = 50
    MAX_METHOD_COMPLEXITY = 10

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.ignore_dirs = {'target', 'node_modules', '.git', 'dist', 'build'}

    def check(self) -> tuple[list[ReviewComment], list[str]]:
        comments = []
        passed = []

        for java_file in self.project_root.rglob('*.java'):
            if any(ignore in java_file.parts for ignore in self.ignore_dirs):
                continue

            try:
                content = java_file.read_text(encoding='utf-8', errors='ignore')
                lines = content.split('\n')

                in_method = False
                method_line_count = 0
                method_name = ""
                brace_count = 0

                for line_num, line in enumerate(lines, 1):
                    stripped = line.strip()

                    # 检测方法开始
                    if re.search(r'(public|private|protected)?\s+(static)?\s+\w+\s+\w+\s*\(', stripped):
                        in_method = True
                        method_line_count = 0
                        method_match = re.search(r'\w+\s+(\w+)\s*\(', stripped)
                        method_name = method_match.group(1) if method_match else "unknown"
                        brace_count = 0

                    if in_method:
                        method_line_count += 1
                        brace_count += stripped.count('{') - stripped.count('}')

                        # 方法结束
                        if brace_count <= 0 and '{' in content[content.find(stripped):]:
                            in_method = False

                            # 检查方法长度
                            if method_line_count > self.MAX_METHOD_LENGTH:
                                comments.append(ReviewComment(
                                    severity=Severity.MINOR,
                                    category=self.TOOL_NAME,
                                    message=f"方法 '{method_name}' 过长: {method_line_count} 行 (建议: {self.MAX_METHOD_LENGTH})",
                                    file=str(java_file.relative_to(self.project_root)),
                                    line=line_num,
                                    rule_id="method-too-long"
                                ))

                # 检查圈复杂度 (简化版)
                complexity = len(re.findall(r'\b(if|while|for|switch|case|catch|\?\s*:)\b', content))
                file_name = java_file.stem

                if complexity > self.MAX_METHOD_COMPLEXITY * 5:
                    comments.append(ReviewComment(
                        severity=Severity.MINOR,
                        category=self.TOOL_NAME,
                        message=f"文件 '{file_name}' 复杂度较高 (约{complexity}处条件分支)",
                        file=str(java_file.relative_to(self.project_root)),
                        rule_id="high-complexity"
                    ))
                else:
                    passed.append(f"{file_name} (复杂度正常)")

            except Exception:
                continue

        return comments, passed


class ReviewerOrchestrator:
    """审核编排器"""

    def __init__(self, config_loader: ConfigLoader, verbose: bool = False):
        self.config_loader = config_loader
        self.verbose = verbose
        self.executor = CommandExecutor(timeout=600, verbose=verbose)
        self.iteration = 1
        self.results: list[ReviewResult] = []

    def run(self) -> ReviewResult:
        """执行代码审核"""
        print(color_text("\n=== 代码审核 (Code Review) ===", Colors.CYAN + Colors.BOLD))

        if not self.config_loader.reviewer_enabled:
            print(color_text("  [SKIP] 代码审核已被禁用", Colors.YELLOW))
            return ReviewResult(
                status=ReviewStatus.APPROVED,
                iteration=0,
                max_iterations=self.config_loader.max_iterations
            )

        standards = self.config_loader.standards
        max_iterations = self.config_loader.max_iterations
        project_root = str(self.config_loader.project_root)

        all_comments = []
        all_passed = []
        all_failed = []

        start_time = time.time()

        # 1. 命名规范检查
        if standards.get('naming_convention', True):
            print(color_text("\n  [1/5] 检查命名规范...", Colors.BLUE))
            naming_checker = NamingConventionChecker(project_root)
            comments, passed = naming_checker.check()
            all_comments.extend(comments)
            all_passed.extend(passed)
            if comments:
                all_failed.append("命名规范")
                print(color_text(f"    发现 {len(comments)} 个命名问题", Colors.YELLOW))
            else:
                print(color_text(f"    [PASS] 通过 ({len(passed)} 项)", Colors.GREEN))

        # 2. Javadoc检查
        if standards.get('javadoc_required', False):
            print(color_text("\n  [2/5] 检查Javadoc文档...", Colors.BLUE))
            javadoc_checker = JavadocChecker(project_root)
            comments, passed = javadoc_checker.check()
            all_comments.extend(comments)
            all_passed.extend(passed)
            if comments:
                all_failed.append("Javadoc")
                print(color_text(f"    发现 {len(comments)} 个Javadoc问题", Colors.YELLOW))
            else:
                print(color_text(f"    [PASS] 通过 ({len(passed)} 项)", Colors.GREEN))

        # 3. 硬编码密钥检查
        if standards.get('no_hardcoded_secrets', True):
            print(color_text("\n  [3/5] 检查硬编码密钥...", Colors.BLUE))
            secret_checker = HardcodedSecretChecker(project_root)
            comments, passed = secret_checker.check()
            all_comments.extend(comments)
            all_passed.extend(passed)
            if comments:
                all_failed.append("硬编码密钥")
                for c in comments:
                    if c.severity == Severity.CRITICAL:
                        print(color_text(f"    [FAIL] {c.message} ({c.file}:{c.line})", Colors.RED))
                    else:
                        print(color_text(f"    ⚠ {c.message}", Colors.YELLOW))
            else:
                print(color_text(f"    [PASS] 通过", Colors.GREEN))

        # 4. 测试覆盖率检查
        if standards.get('test_pass_rate'):
            print(color_text("\n  [4/5] 检查测试覆盖率...", Colors.BLUE))
            coverage_checker = TestCoverageChecker(self.executor, project_root)
            threshold = self.config_loader.config.get('test', {}).get('coverage_threshold', 70)
            comments, passed = coverage_checker.check(threshold)
            all_comments.extend(comments)
            all_passed.extend(passed)
            if comments:
                all_failed.append("测试覆盖率")
                print(color_text(f"    发现 {len(comments)} 个覆盖率问题", Colors.YELLOW))
            else:
                print(color_text(f"    [PASS] 通过 ({len(passed)} 项)", Colors.GREEN))

        # 5. 代码复杂度检查
        print(color_text("\n  [5/5] 检查代码复杂度...", Colors.BLUE))
        complexity_checker = ComplexityChecker(project_root)
        comments, passed = complexity_checker.check()
        all_comments.extend(comments)
        all_passed.extend(passed)
        if comments:
            all_failed.append("代码复杂度")
            print(color_text(f"    发现 {len(comments)} 个复杂度问题", Colors.YELLOW))
        else:
            print(color_text(f"    [PASS] 通过 ({len(passed)} 项)", Colors.GREEN))

        duration = time.time() - start_time

        # 判断审核状态
        status = self._determine_status(all_comments, standards, duration)

        result = ReviewResult(
            status=status,
            iteration=self.iteration,
            max_iterations=max_iterations,
            comments=all_comments,
            passed_checks=all_passed,
            failed_checks=all_failed,
            duration=duration
        )

        self.results.append(result)
        self._print_summary(result)

        return result

    def _determine_status(self, comments: list[ReviewComment], standards: dict, duration: float) -> ReviewStatus:
        """根据评论判断审核状态"""

        # 检查是否有CRITICAL级别问题
        critical_issues = [c for c in comments if c.severity == Severity.CRITICAL]
        if critical_issues:
            return ReviewStatus.REVISION_REQUESTED

        # 检查是否有必须修复的问题
        if standards.get('no_hardcoded_secrets') and any(c.category == 'hardcoded-secret' for c in comments):
            return ReviewStatus.REVISION_REQUESTED

        # 检查是否有MAJOR级别问题
        major_issues = [c for c in comments if c.severity == Severity.MAJOR]
        if major_issues and self.iteration < self.config_loader.max_iterations:
            return ReviewStatus.REVISION_REQUESTED

        # 检查审核迭代次数
        if self.iteration >= self.config_loader.max_iterations:
            if comments:
                return ReviewStatus.REJECTED
            else:
                return ReviewStatus.APPROVED

        return ReviewStatus.APPROVED

    def _print_summary(self, result: ReviewResult):
        """打印审核结果汇总"""
        print(color_text("\n" + "=" * 50, Colors.CYAN))
        print(color_text("审核结果汇总", Colors.BOLD + Colors.CYAN))
        print(color_text("=" * 50, Colors.CYAN))

        status_colors = {
            ReviewStatus.APPROVED: Colors.GREEN,
            ReviewStatus.REVISION_REQUESTED: Colors.YELLOW,
            ReviewStatus.REJECTED: Colors.RED,
        }

        status_texts = {
            ReviewStatus.APPROVED: "[PASS] APPROVED - 审核通过",
            ReviewStatus.REVISION_REQUESTED: "⚠ REVISION_REQUESTED - 需要修改",
            ReviewStatus.REJECTED: "[FAIL] REJECTED - 审核拒绝",
        }

        print(color_text(f"状态: {status_texts[result.status]}", status_colors.get(result.status, Colors.RESET)))
        print(f"迭代次数: {result.iteration}/{result.max_iterations}")
        print(f"审核耗时: {result.duration:.1f}秒")

        print(color_text(f"\n检查项:", Colors.BOLD))
        if result.passed_checks:
            for check in result.passed_checks[:5]:
                print(color_text(f"  [PASS] {check}", Colors.GREEN))
            if len(result.passed_checks) > 5:
                print(color_text(f"  ... 还有 {len(result.passed_checks) - 5} 项", Colors.BLUE))

        if result.failed_checks:
            print(color_text(f"\n失败项:", Colors.RED))
            for check in result.failed_checks:
                print(color_text(f"  [FAIL] {check}", Colors.RED))

        if result.comments:
            critical = [c for c in result.comments if c.severity == Severity.CRITICAL]
            major = [c for c in result.comments if c.severity == Severity.MAJOR]
            minor = [c for c in result.comments if c.severity == Severity.MINOR]

            print(color_text(f"\n问题汇总: {len(result.comments)} 个", Colors.BOLD))
            if critical:
                print(color_text(f"  CRITICAL: {len(critical)} 个", Colors.RED))
            if major:
                print(color_text(f"  MAJOR: {len(major)} 个", Colors.YELLOW))
            if minor:
                print(color_text(f"  MINOR: {len(minor)} 个", Colors.BLUE))

        print(color_text("=" * 50, Colors.CYAN))

    def export_json(self, output_file: str):
        """导出JSON格式报告"""
        data = {
            "timestamp": datetime.now().isoformat(),
            "results": [
                {
                    "status": r.status.value,
                    "iteration": r.iteration,
                    "max_iterations": r.max_iterations,
                    "comments": [c.to_dict() for c in r.comments],
                    "passed_checks": r.passed_checks,
                    "failed_checks": r.failed_checks,
                    "duration": r.duration
                }
                for r in self.results
            ],
            "final_status": self.results[-1].status.value if self.results else "UNKNOWN"
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(color_text(f"\n报告已导出: {output_file}", Colors.BLUE))


def main():
    parser = argparse.ArgumentParser(
        description="Auto-Dev 代码审核脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--project-root', '-p',
        default='.',
        help='项目根目录 (默认: .)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='显示详细信息'
    )
    parser.add_argument(
        '--iteration', '-i',
        type=int,
        default=1,
        help='当前迭代次数'
    )
    parser.add_argument(
        '--json',
        metavar='FILE',
        help='导出JSON格式报告'
    )

    args = parser.parse_args()

    # 加载配置
    config_loader = ConfigLoader(args.project_root)

    # 执行审核
    orchestrator = ReviewerOrchestrator(config_loader, verbose=args.verbose)
    orchestrator.iteration = args.iteration
    result = orchestrator.run()

    # 导出报告
    if args.json:
        orchestrator.export_json(args.json)

    # 返回状态码
    if result.status == ReviewStatus.APPROVED:
        sys.exit(0)
    elif result.status == ReviewStatus.REJECTED:
        sys.exit(2)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
