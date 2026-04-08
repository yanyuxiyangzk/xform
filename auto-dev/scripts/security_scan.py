#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全扫描脚本 - Auto-Dev Quality Gate
基于 .auto-dev.yaml 配置执行安全扫描
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


class Severity(Enum):
    P0 = "P0"  # 严重，必须修复
    P1 = "P1"  # 高危，应该修复
    P2 = "P2"  # 中危，建议修复
    P3 = "P3"  # 低危，可以忽略


class CheckStatus(Enum):
    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"
    SKIP = "skip"


@dataclass
class SecurityIssue:
    severity: Severity
    tool: str
    message: str
    file: Optional[str] = None
    line: Optional[int] = None
    rule_id: Optional[str] = None

    def to_dict(self):
        return {
            "severity": self.severity.value,
            "tool": self.tool,
            "message": self.message,
            "file": self.file,
            "line": self.line,
            "rule_id": self.rule_id
        }


@dataclass
class ScanResult:
    tool: str
    status: CheckStatus
    issues: list[SecurityIssue] = field(default_factory=list)
    output: str = ""
    duration: float = 0.0
    error: Optional[str] = None

    @property
    def has_p0(self) -> bool:
        return any(i.severity == Severity.P0 for i in self.issues)

    @property
    def has_p1(self) -> bool:
        return any(i.severity == Severity.P1 for i in self.issues)


class Colors:
    RED = '\033[91m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


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
    def security_enabled(self) -> bool:
        sec = self.config.get('security', {})
        return sec.get('enabled', True)

    @property
    def security_tools(self) -> list:
        sec = self.config.get('security', {})
        return sec.get('tools', [])

    @property
    def custom_rules(self) -> list:
        sec = self.config.get('security', {})
        return sec.get('custom_rules', [])

    @property
    def block_on_fail(self) -> dict:
        gate = self.config.get('gate', {})
        return gate.get('block_on', {})

    @property
    def warn_on(self) -> dict:
        gate = self.config.get('gate', {})
        return gate.get('warn_on', {})


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


class DependencyAnalyzeChecker:
    """Maven依赖分析检查器"""

    TOOL_NAME = "dependency-analyze"

    def __init__(self, config: dict, executor: CommandExecutor):
        self.config = config
        self.executor = executor

    def check(self) -> ScanResult:
        start = time.time()

        if self.config.get('on_fail', 'warn') == 'ignore':
            return ScanResult(
                tool=self.TOOL_NAME,
                status=CheckStatus.SKIP,
                output="Skipped by configuration"
            )

        command = self.config.get('command', 'mvn dependency:analyze')
        returncode, stdout, stderr = self.executor.run(command)

        issues = []
        output = stdout + stderr

        # 解析 dependency:analyze 输出
        # 查找 "Used undeclared dependencies" 和 "Unused declared dependencies"
        if "Used undeclared dependencies found" in output:
            issues.append(SecurityIssue(
                severity=Severity.P2,
                tool=self.TOOL_NAME,
                message="发现使用但未声明的依赖",
                rule_id="used-undeclared"
            ))

        if "Unused declared dependencies found" in output:
            issues.append(SecurityIssue(
                severity=Severity.P3,
                tool=self.TOOL_NAME,
                message="发现未使用的声明依赖",
                rule_id="unused-declared"
            ))

        # 检查严重问题
        critical_patterns = [
            (r'Remove\s+the\s+use\s+of\s+this\s+dependency', Severity.P1),
            (r'potential\s+security\s+vulnerability', Severity.P0),
            (r'CVE-\d+-\d+', Severity.P0),
        ]

        for line in output.split('\n'):
            for pattern, severity in critical_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(SecurityIssue(
                        severity=severity,
                        tool=self.TOOL_NAME,
                        message=line.strip(),
                        rule_id="vulnerability"
                    ))

        duration = time.time() - start
        status = CheckStatus.PASS if returncode == 0 else CheckStatus.WARN

        return ScanResult(
            tool=self.TOOL_NAME,
            status=status,
            issues=issues,
            output=output[:5000],  # 截断输出
            duration=duration,
            error=None if returncode == 0 else f"Exit code: {returncode}"
        )


class ForbiddenDepsChecker:
    """禁止依赖检查器"""

    TOOL_NAME = "forbidden-deps"

    def __init__(self, config: dict, executor: CommandExecutor):
        self.config = config
        self.executor = executor

    def check(self) -> ScanResult:
        start = time.time()

        pattern = self.config.get('pattern', '')
        if not pattern:
            return ScanResult(
                tool=self.TOOL_NAME,
                status=CheckStatus.SKIP,
                output="No pattern configured"
            )

        command = self.config.get('command', 'mvn dependency:tree')
        returncode, stdout, stderr = self.executor.run(command)

        issues = []
        allow_internal = self.config.get('allow_internal', True)

        for line in stdout.split('\n'):
            if re.search(pattern, line):
                # 检查是否是内部允许的依赖
                if allow_internal and 'com.nocode' in line:
                    continue

                issues.append(SecurityIssue(
                    severity=Severity.P0,
                    tool=self.TOOL_NAME,
                    message=f"禁止的依赖: {line.strip()}",
                    rule_id="forbidden-dep"
                ))

        duration = time.time() - start

        return ScanResult(
            tool=self.TOOL_NAME,
            status=CheckStatus.FAIL if issues else CheckStatus.PASS,
            issues=issues,
            output=stdout[:5000],
            duration=duration
        )


class HardcodedSecretScanner:
    """硬编码密钥扫描器"""

    TOOL_NAME = "hardcoded-secret-scan"

    # 默认扫描的文件类型
    SCAN_EXTENSIONS = ['.java', '.xml', '.properties', '.yml', '.yaml',
                      '.json', '.js', '.ts', '.py', '.sh', '.sql']

    # 忽略的目录
    IGNORE_DIRS = ['target', 'node_modules', '.git', 'dist', 'build',
                   '.mvn', '.idea', '.vscode', 'test', 'tests']

    def __init__(self, rules: list, executor: CommandExecutor, project_root: str = "."):
        self.rules = rules
        self.executor = executor
        self.project_root = Path(project_root)

    def check(self) -> ScanResult:
        start = time.time()
        issues = []
        scanned_files = 0

        for rule in self.rules:
            pattern = rule.get('pattern', '')
            rule_id = rule.get('id', 'unknown')
            severity_str = rule.get('severity', 'P1')
            message = rule.get('message', '发现安全问题')

            try:
                severity = Severity[severity_str] if severity_str in [s.value for s in Severity] else Severity.P1
            except ValueError:
                severity = Severity.P1

            regex = re.compile(pattern, re.IGNORECASE)

            for ext in self.SCAN_EXTENSIONS:
                for file_path in self.project_root.rglob(f'*{ext}'):
                    # 跳过忽略的目录
                    if any(ignore in file_path.parts for ignore in self.IGNORE_DIRS):
                        continue

                    scanned_files += 1

                    try:
                        content = file_path.read_text(encoding='utf-8', errors='ignore')
                        lines = content.split('\n')

                        for line_num, line in enumerate(lines, 1):
                            if regex.search(line):
                                # 排除注释中的匹配
                                stripped = line.strip()
                                if stripped.startswith('//') or stripped.startswith('#') or stripped.startswith('*'):
                                    continue

                                issues.append(SecurityIssue(
                                    severity=severity,
                                    tool=self.TOOL_NAME,
                                    message=f"{message}: {self._mask_secret(line.strip())}",
                                    file=str(file_path.relative_to(self.project_root)),
                                    line=line_num,
                                    rule_id=rule_id
                                ))
                    except Exception:
                        continue

        duration = time.time() - start

        return ScanResult(
            tool=self.TOOL_NAME,
            status=CheckStatus.FAIL if issues else CheckStatus.PASS,
            issues=issues,
            output=f"Scanned {scanned_files} files",
            duration=duration
        )

    def _mask_secret(self, line: str) -> str:
        """掩码敏感信息"""
        patterns = [
            (r'(password|secret|token|api_key)\s*=\s*["\'][^"\']{3,}["\']', r'\1=***'),
            (r'(Bearer\s+)[a-zA-Z0-9\-_.]+', r'\1***'),
            (r'(sk|api_key|token)[=:]\s*[a-zA-Z0-9\-_.]{10,}', r'\1=***'),
        ]

        result = line
        for pattern, replacement in patterns:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

        return result


class NpmAuditChecker:
    """NPM安全审计检查器"""

    TOOL_NAME = "npm-audit"

    def __init__(self, executor: CommandExecutor, project_root: str = "."):
        self.executor = executor
        self.project_root = Path(project_root)

    def check(self) -> ScanResult:
        start = time.time()

        # 检查是否存在 package.json
        package_json = self.project_root / "package.json"
        if not package_json.exists():
            return ScanResult(
                tool=self.TOOL_NAME,
                status=CheckStatus.SKIP,
                output="No package.json found"
            )

        returncode, stdout, stderr = self.executor.run("npm audit --json", str(self.project_root))

        issues = []

        # 解析 npm audit JSON 输出
        try:
            # 尝试解析JSON
            if stdout:
                audit_data = json.loads(stdout)
                vulnerabilities = audit_data.get('vulnerabilities', {})

                for vuln_id, vuln_info in vulnerabilities.items():
                    severity = vuln_info.get('severity', 'moderate')
                    severity_enum = {
                        'critical': Severity.P0,
                        'high': Severity.P1,
                        'moderate': Severity.P2,
                        'low': Severity.P3
                    }.get(severity, Severity.P2)

                    issues.append(SecurityIssue(
                        severity=severity_enum,
                        tool=self.TOOL_NAME,
                        message=f"NPM vulnerability: {vuln_id} ({severity})",
                        rule_id=f"npm-{vuln_id}"
                    ))
        except json.JSONDecodeError:
            # 如果不是JSON格式，检查文本输出
            if 'vulnerability' in stdout.lower() or 'CVE' in stdout:
                issues.append(SecurityIssue(
                    severity=Severity.P1,
                    tool=self.TOOL_NAME,
                    message="发现NPM安全漏洞",
                    rule_id="npm-vulnerability"
                ))

        duration = time.time() - start

        return ScanResult(
            tool=self.TOOL_NAME,
            status=CheckStatus.FAIL if issues else CheckStatus.PASS,
            issues=issues,
            output=stdout[:5000],
            duration=duration
        )


class TrivyChecker:
    """Trivy容器镜像扫描器"""

    TOOL_NAME = "trivy"

    def __init__(self, executor: CommandExecutor):
        self.executor = executor

    def check(self, image: str = "app:latest") -> ScanResult:
        start = time.time()

        command = f"trivy image --severity HIGH,CRITICAL --format json {image}"
        returncode, stdout, stderr = self.executor.run(command)

        issues = []

        try:
            if stdout:
                scan_data = json.loads(stdout)
                results = scan_data.get('Results', [])

                for result in results:
                    vulnerabilities = result.get('Vulnerabilities', []) or []
                    for vuln in vulnerabilities:
                        severity_str = vuln.get('Severity', 'UNKNOWN')
                        severity_enum = {
                            'CRITICAL': Severity.P0,
                            'HIGH': Severity.P1,
                            'MEDIUM': Severity.P2,
                            'LOW': Severity.P3
                        }.get(severity_str.upper(), Severity.P2)

                        issues.append(SecurityIssue(
                            severity=severity_enum,
                            tool=self.TOOL_NAME,
                            message=f"Container vulnerability: {vuln.get('PkgName', 'unknown')} - {vuln.get('Title', 'unknown')}",
                            rule_id=vuln.get('VulnerabilityID', 'unknown')
                        ))
        except json.JSONDecodeError:
            pass

        duration = time.time() - start

        return ScanResult(
            tool=self.TOOL_NAME,
            status=CheckStatus.FAIL if issues else CheckStatus.PASS,
            issues=issues,
            output=stdout[:5000] if stdout else stderr[:5000],
            duration=duration
        )


class SecurityScanOrchestrator:
    """安全扫描编排器"""

    def __init__(self, config_loader: ConfigLoader, verbose: bool = False):
        self.config_loader = config_loader
        self.verbose = verbose
        self.executor = CommandExecutor(timeout=300, verbose=verbose)
        self.results: list[ScanResult] = []

    def run(self) -> bool:
        """执行所有安全扫描，返回是否通过"""
        print(color_text("\n=== 安全扫描 (Security Scan) ===", Colors.BLUE + Colors.BOLD))

        if not self.config_loader.security_enabled:
            print(color_text("  [SKIP] 安全扫描已被禁用", Colors.YELLOW))
            return True

        # 1. Maven依赖分析
        for tool_config in self.config_loader.security_tools:
            tool_name = tool_config.get('name', '')

            if tool_name == 'dependency-analyze':
                checker = DependencyAnalyzeChecker(tool_config, self.executor)
                result = checker.check()
                self.results.append(result)
                self._print_result(result)

            elif tool_name == 'forbidden-deps':
                checker = ForbiddenDepsChecker(tool_config, self.executor)
                result = checker.check()
                self.results.append(result)
                self._print_result(result)

        # 2. 自定义规则扫描
        custom_rules = self.config_loader.custom_rules
        if custom_rules:
            scanner = HardcodedSecretScanner(custom_rules, self.executor)
            result = scanner.check()
            self.results.append(result)
            self._print_result(result)

        # 3. NPM审计（如果存在package.json）
        project_root = self.config_loader.project_root
        if (project_root / "package.json").exists():
            npm_checker = NpmAuditChecker(self.executor, str(project_root))
            result = npm_checker.check()
            self.results.append(result)
            self._print_result(result)

        # 汇总结果
        return self._summarize()

    def _print_result(self, result: ScanResult):
        """打印单个扫描结果"""
        icon = {
            CheckStatus.PASS: color_text("✓", Colors.GREEN),
            CheckStatus.FAIL: color_text("✗", Colors.RED),
            CheckStatus.WARN: color_text("⚠", Colors.YELLOW),
            CheckStatus.SKIP: color_text("○", Colors.BLUE),
        }.get(result.status, "?")

        status_text = {
            CheckStatus.PASS: color_text("通过", Colors.GREEN),
            CheckStatus.FAIL: color_text("失败", Colors.RED),
            CheckStatus.WARN: color_text("警告", Colors.YELLOW),
            CheckStatus.SKIP: color_text("跳过", Colors.BLUE),
        }.get(result.status, "未知")

        print(f"  {icon} [{result.tool}] {status_text} ({result.duration:.1f}s)")

        if result.issues and self.verbose:
            for issue in result.issues:
                severity_color = {
                    Severity.P0: Colors.RED,
                    Severity.P1: Colors.YELLOW,
                    Severity.P2: Colors.YELLOW,
                    Severity.P3: Colors.BLUE,
                }.get(issue.severity, Colors.RESET)

                location = f"{issue.file}:{issue.line}" if issue.file else ""
                print(f"      {color_text(f'[{issue.severity.value}]', severity_color)} {issue.message} {color_text(location, Colors.BLUE)}")

    def _summarize(self) -> bool:
        """汇总所有扫描结果"""
        total_issues = sum(len(r.issues) for r in self.results)
        p0_count = sum(1 for r in self.results for i in r.issues if i.severity == Severity.P0)
        p1_count = sum(1 for r in self.results for i in r.issues if i.severity == Severity.P1)

        print(color_text(f"\n  总计发现问题: {total_issues}", Colors.BOLD))
        if p0_count > 0:
            print(color_text(f"    P0 (严重): {p0_count}", Colors.RED))
        if p1_count > 0:
            print(color_text(f"    P1 (高危): {p1_count}", Colors.YELLOW))

        # 判断是否阻止
        block_on = self.config_loader.block_on_fail
        warn_on = self.config_loader.warn_on

        if block_on.get('p0_security') and p0_count > 0:
            print(color_text("\n✗ 安全扫描失败: 发现 P0 级别安全问题", Colors.RED + Colors.BOLD))
            return False

        if warn_on.get('p1_security') and p1_count > 0:
            print(color_text("\n⚠ 安全扫描警告: 发现 P1 级别安全问题", Colors.YELLOW))
            # P1只是警告，不阻止

        return True

    def export_json(self, output_file: str):
        """导出JSON格式报告"""
        data = {
            "timestamp": datetime.now().isoformat(),
            "results": [
                {
                    "tool": r.tool,
                    "status": r.status.value,
                    "issues": [i.to_dict() for i in r.issues],
                    "duration": r.duration,
                    "error": r.error
                }
                for r in self.results
            ],
            "summary": {
                "total_issues": sum(len(r.issues) for r in self.results),
                "p0_count": sum(1 for r in self.results for i in r.issues if i.severity == Severity.P0),
                "p1_count": sum(1 for r in self.results for i in r.issues if i.severity == Severity.P1),
            }
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(color_text(f"\n报告已导出: {output_file}", Colors.BLUE))


def main():
    parser = argparse.ArgumentParser(
        description="Auto-Dev 安全扫描脚本",
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
        '--json',
        metavar='FILE',
        help='导出JSON格式报告'
    )
    parser.add_argument(
        '--tool',
        choices=['dependency-analyze', 'forbidden-deps', 'hardcoded-secret', 'npm', 'all'],
        default='all',
        help='指定扫描工具'
    )

    args = parser.parse_args()

    # 加载配置
    config_loader = ConfigLoader(args.project_root)

    # 执行扫描
    orchestrator = SecurityScanOrchestrator(config_loader, verbose=args.verbose)
    success = orchestrator.run()

    # 导出报告
    if args.json:
        orchestrator.export_json(args.json)

    # 返回状态码
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
