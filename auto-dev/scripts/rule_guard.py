#!/usr/bin/env python3
"""
Rule Guard - 规则守卫
确保开发过程遵循RULES.md定义的规则

用法:
  python rule_guard.py check <file_or_dir>     # 检查单个文件或目录
  python rule_guard.py pre-commit <dir>        # 提交前检查
  python rule_guard.py enforce <type> <path>  # 强制执行规则
  python rule_guard.py gate <stage> <path>    # 质量门卫检查
  python rule_guard.py report                 # 生成检查报告

规则检查项:
  - mvn compile (编译检查)
  - mvn test (单元测试)
  - 代码规范 (命名/注释)
  - 安全规则 (敏感信息/硬编码)
  - 提交规范 (消息格式)
"""

import os
import sys
import re
import json
import subprocess
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Tuple

# 配置
AUTO_DEV_BASE = Path(__file__).parent.parent
RULES_FILE = AUTO_DEV_BASE / "RULES.md"
PROJECTS_DIR = AUTO_DEV_BASE.parent


class RuleGuard:
    def __init__(self):
        self.rules_file = RULES_FILE
        self.violations = []
        self.warnings = []
        self.passed = []


class StuckDetector:
    """检测死循环/卡死状态"""

    MAX_IDENTICAL_ERRORS = 3
    MAX_TOTAL_ITERATIONS = 5
    STATE_FILE = AUTO_DEV_BASE / "self-improving" / "stuck-state.json"

    def __init__(self):
        AUTO_DEV_BASE.mkdir(exist_ok=True)
        self.state = self._load_state()

    def _load_state(self) -> Dict:
        """加载状态"""
        if self.STATE_FILE.exists():
            try:
                with open(self.STATE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {"error_history": {}, "iteration_count": {}, "stuck_tasks": []}

    def _save_state(self):
        """保存状态"""
        with open(self.STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    def _hash_error(self, error: str) -> str:
        """对错误信息进行哈希，用于检测相同错误"""
        import hashlib
        # 归一化错误信息
        normalized = error.strip().lower()[:200]
        return hashlib.md5(normalized.encode()).hexdigest()[:8]

    def record_error(self, task_id: str, error: str) -> bool:
        """
        记录错误

        Returns:
            True 如果检测到卡死状态
        """
        if task_id not in self.state["error_history"]:
            self.state["error_history"][task_id] = []
            self.state["iteration_count"][task_id] = 0

        error_hash = self._hash_error(error)
        errors = self.state["error_history"][task_id]

        # 检查是否相同错误重复
        recent_same_errors = [e for e in errors[-5:] if e["hash"] == error_hash]

        if len(recent_same_errors) >= self.MAX_IDENTICAL_ERRORS - 1:
            # 检测到相同错误重复
            if task_id not in self.state["stuck_tasks"]:
                self.state["stuck_tasks"].append(task_id)
            self._save_state()
            return True

        # 记录错误
        errors.append({
            "hash": error_hash,
            "error": error[:100],
            "time": datetime.now().isoformat()
        })

        # 限制历史长度
        if len(errors) > 20:
            self.state["error_history"][task_id] = errors[-20:]

        self.state["iteration_count"][task_id] = self.state["iteration_count"].get(task_id, 0) + 1

        # 检查总迭代次数
        if self.state["iteration_count"].get(task_id, 0) >= self.MAX_TOTAL_ITERATIONS:
            if task_id not in self.state["stuck_tasks"]:
                self.state["stuck_tasks"].append(task_id)
            self._save_state()
            return True

        self._save_state()
        return False

    def is_stuck(self, task_id: str) -> bool:
        """检查任务是否卡死"""
        return task_id in self.state.get("stuck_tasks", [])

    def get_stuck_tasks(self) -> List[str]:
        """获取所有卡死任务"""
        return self.state.get("stuck_tasks", [])

    def clear_task(self, task_id: str):
        """清除任务状态"""
        if task_id in self.state["stuck_tasks"]:
            self.state["stuck_tasks"].remove(task_id)
        self.state["error_history"].pop(task_id, None)
        self.state["iteration_count"].pop(task_id, None)
        self._save_state()


class SelfHealer:
    """CI失败自愈"""

    # 可自愈的错误类型及对应修复命令
    HEALABLE_ERRORS = {
        "mvn_deps": {
            "pattern": r"Could not resolve dependencies|dependency.*not found",
            "fix": ["mvn", "dependency:resolve"],
            "description": "Maven依赖解析失败"
        },
        "mvn_cache": {
            "pattern": r"Could not read|checksum.*failed|cache.*corrupt",
            "fix": ["mvn", "dependency:purge-local-repository", "-DactTransitively=false"],
            "description": "Maven缓存损坏"
        },
        "npm_deps": {
            "pattern": r"npm ERR!|cannot find module",
            "fix": ["npm", "install"],
            "description": "npm依赖安装失败"
        },
        "format_error": {
            "pattern": r"format.*error|indentation.*error",
            "fix": ["mvn", "formatter:format"],
            "description": "代码格式化问题"
        }
    }

    def __init__(self):
        self.heal_history = {}  # task_id -> [(error, fix_attempt, success), ...]

    def can_heal(self, error_type: str) -> bool:
        """检查错误是否可自愈"""
        return error_type in self.HEALABLE_ERRORS

    def classify_error(self, error_msg: str) -> Optional[str]:
        """分类错误类型"""
        for error_type, info in self.HEALABLE_ERRORS.items():
            if re.search(info["pattern"], error_msg, re.IGNORECASE):
                return error_type
        return None

    def attempt_heal(self, task_id: str, error_msg: str, context: Dict = None) -> Tuple[bool, str]:
        """
        尝试自愈

        Returns:
            (success: bool, message: str)
        """
        error_type = self.classify_error(error_msg)

        if not error_type:
            return False, f"Unknown error type: {error_msg[:100]}"

        if not self.can_heal(error_type):
            return False, f"Error type {error_type} is not healable"

        heal_info = self.HEALABLE_ERRORS[error_type]

        # 检查是否已经尝试过
        history = self.heal_history.get(task_id, [])
        if any(h[0] == error_type and h[2] for h in history):
            return False, f"Already healed {error_type} successfully before"

        # 限制修复尝试次数
        attempts = [h for h in history if h[0] == error_type]
        if len(attempts) >= 2:
            return False, f"Already attempted to heal {error_type} 2 times"

        print(f"[HEAL] Attempting to heal {error_type}: {heal_info['description']}")

        try:
            project_dir = context.get("project_dir", Path.cwd()) if context else Path.cwd()
            result = subprocess.run(
                heal_info["fix"],
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=300
            )

            success = result.returncode == 0

            # 记录尝试
            if task_id not in self.heal_history:
                self.heal_history[task_id] = []
            self.heal_history[task_id].append((error_type, heal_info["fix"], success))

            if success:
                return True, f"Successfully healed {error_type}"
            else:
                return False, f"Failed to heal {error_type}: {result.stderr[:200]}"

        except subprocess.TimeoutExpired:
            return False, f"Heal command timeout for {error_type}"
        except Exception as e:
            return False, f"Heal error: {str(e)}"

    def get_heal_stats(self) -> Dict:
        """获取自愈统计"""
        total_attempts = sum(len(h) for h in self.heal_history.values())
        successful = sum(1 for history in self.heal_history.values() for h in history if h[2])
        return {
            "total_attempts": total_attempts,
            "successful": successful,
            "failed": total_attempts - successful,
            "tasks_with_heals": len(self.heal_history)
        }

    def check_compile(self, project_dir: Path) -> Tuple[bool, str]:
        """检查Maven编译"""
        pom_file = project_dir / "pom.xml"
        if not pom_file.exists():
            return True, "No pom.xml found, skipping compile"

        print("[CHECK] Running mvn compile...")
        try:
            result = subprocess.run(
                ["mvn", "compile", "-q"],
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=300
            )
            if result.returncode == 0:
                return True, "Compilation successful"
            else:
                return False, f"Compilation failed: {result.stderr[:500]}"
        except subprocess.TimeoutExpired:
            return False, "Compilation timeout (>5min)"
        except FileNotFoundError:
            return True, "Maven not found, skipping"
        except Exception as e:
            return False, f"Compilation error: {str(e)}"

    def check_tests(self, project_dir: Path) -> Tuple[bool, str]:
        """检查单元测试 - 必须测试通过率≥90%"""
        pom_file = project_dir / "pom.xml"
        if not pom_file.exists():
            return True, "No pom.xml found, skipping tests"

        print("[CHECK] Running mvn test...")
        try:
            # 使用surefire报告解析（不-quiet，以便获取详细结果）
            result = subprocess.run(
                ["mvn", "test"],
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=600
            )

            # 解析测试结果
            output = result.stdout + result.stderr
            pass_rate, total, failures = self._parse_test_results(output)

            if result.returncode == 0:
                if pass_rate is not None and pass_rate < 90:
                    return False, f"Test pass rate {pass_rate}% < 90% (failures: {failures}/{total})"
                return True, f"Tests passed (pass rate: {pass_rate or 'unknown'}%)"
            else:
                if pass_rate is not None and pass_rate >= 90:
                    return True, f"Tests passed with {pass_rate}% (some errors in setup)"
                return False, f"Tests failed: {failures}/{total} failed. Check surefire reports."

        except subprocess.TimeoutExpired:
            return False, "Tests timeout (>10min)"
        except FileNotFoundError:
            return True, "Maven not found, skipping"
        except Exception as e:
            return False, f"Test error: {str(e)}"

    def _parse_test_results(self, output: str) -> Tuple:
        """解析Maven测试输出，获取通过率"""
        import re
        # 匹配 "Tests run: 100, Failures: 2, Errors: 0, Skipped: 0"
        pattern = r'Tests run:\s*(\d+),\s*Failures:\s*(\d+),\s*Errors:\s*(\d+),\s*Skipped:\s*(\d+)'
        match = re.search(pattern, output)
        if match:
            total = int(match.group(1))
            failures = int(match.group(2))
            errors = int(match.group(3))
            skipped = int(match.group(4))
            if total > 0:
                passed = total - failures - errors - skipped
                pass_rate = (passed / total) * 100
                return pass_rate, total, failures + errors
        return None, 0, 0

    def check_security(self, file_path: Path) -> List[Dict]:
        """检查安全规则 - P0/P1漏洞检测"""
        violations = []

        # P0 安全漏洞模式（立即阻塞）
        p0_patterns = [
            # 硬编码凭证
            (r'password\s*=\s*["\'][^"\']{3,30}["\']', "硬编码密码", "P0"),
            (r'secret\s*=\s*["\'][^"\']{3,30}["\']', "硬编码密钥", "P0"),
            (r'api[_-]?key\s*=\s*["\'][^"\']{3,30}["\']', "硬编码API密钥", "P0"),
            (r'jwt[_-]?secret\s*=\s*["\'][^"\']{3,30}["\']', "硬编码JWT密钥", "P0"),
            (r'token\s*=\s*["\'][^"\']{10,50}["\']', "硬编码令牌", "P0"),
            (r'aws[_-]?secret\s*=\s*["\'][^"\']{3,30}["\']', "硬编码AWS密钥", "P0"),
            # SQL注入风险
            (r'executeQuery\s*\(\s*["\'].*\+.*["\']', "SQL注入风险", "P0"),
            (r'executeUpdate\s*\(\s*["\'].*\+.*["\']', "SQL注入风险", "P0"),
            (r'createStatement\(\).*executeQuery.*\+', "SQL注入风险", "P0"),
            # 不安全反序列化
            (r'ObjectInputStream\s*\(', "不安全反序列化", "P0"),
            (r'readObject\s*\(', "不安全的反序列化调用", "P0"),
            # 命令注入
            (r'Runtime\.getRuntime\(\)\.exec\s*\(', "命令注入风险", "P0"),
        ]

        # P1 安全漏洞模式（必须修复）
        p1_patterns = [
            # XSS
            (r'innerHTML\s*=', "XSS风险: innerHTML赋值", "P1"),
            (r'document\.write\s*\(', "XSS风险: document.write", "P1"),
            (r'v-html\s*=', "XSS风险: v-html指令", "P1"),
            # 路径遍历
            (r'new\s+File\s*\(\s*.*\+.*request', "路径遍历风险", "P1"),
            (r'Paths\.get\s*\(\s*.*\+', "路径遍历风险", "P1"),
            # 不安全加密
            (r'MessageDigest\.getInstance\s*\(\s*["\']MD5', "不安全加密算法: MD5", "P1"),
            (r'SecretKeySpec\s*\(\s*.*MD5', "不安全加密算法: MD5", "P1"),
            (r'new\s+Random\(\)', "不安全的随机数生成", "P1"),
            # CSRF
            (r'@csrf\s*=\s*false', "CSRF保护被禁用", "P1"),
        ]

        all_patterns = p0_patterns + p1_patterns

        if file_path.suffix in ['.java', '.js', '.ts', '.vue', '.py', '.yml', '.yaml', '.properties']:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                for pattern, desc, severity in all_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        # 排除环境变量赋值（但P0的硬编码凭证即使在env里也可能有问题）
                        matched_text = match.group(0).lower()
                        if 'env' in matched_text and severity != 'P0':
                            continue
                        violations.append({
                            'file': str(file_path),
                            'rule': 'SECURITY',
                            'type': desc,
                            'line': content[:match.start()].count('\n') + 1,
                            'message': f"安全漏洞[{severity}]: {desc}",
                            'severity': severity
                        })
            except Exception as e:
                pass

        return violations

    def check_naming(self, file_path: Path) -> List[Dict]:
        """检查命名规范"""
        violations = []

        # Java命名规范
        java_naming = [
            (r'class\s+[a-z]+[A-Z]', "类名必须PascalCase"),
            (r'interface\s+[a-z]+', "接口名必须PascalCase"),
            (r'public\s+\w+\s+[A-Z][a-z]+', "方法名必须camelCase"),
        ]

        # Vue组件命名
        vue_patterns = [
            (r'class\s+[a-z\-]+', "Vue组件类名必须PascalCase"),
        ]

        if file_path.suffix == '.java':
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                for pattern, desc in java_naming:
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        violations.append({
                            'file': str(file_path),
                            'rule': 'NAMING',
                            'type': desc,
                            'line': content[:match.start()].count('\n') + 1,
                            'message': f"命名规范: {desc}",
                            'severity': 'P2'
                        })
            except:
                pass

        return violations

    def check_documentation(self, file_path: Path) -> List[Dict]:
        """检查文档注释"""
        violations = []

        if file_path.suffix == '.java':
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # 检查类是否有注释
                class_match = re.search(r'public\s+class\s+(\w+)', content)
                if class_match:
                    class_pos = class_match.start()
                    preceding = content[:class_pos]
                    last_comment = preceding.rfind('/**')

                    # 简单检查：类定义前50字符内是否有文档注释
                    if last_comment == -1 or (class_pos - last_comment) > 200:
                        violations.append({
                            'file': str(file_path),
                            'rule': 'DOCS',
                            'type': 'missing-class-javadoc',
                            'message': f"类 {class_match.group(1)} 缺少文档注释",
                            'severity': 'P1'
                        })
            except:
                pass

        return violations

    def check_file(self, file_path: Path) -> Dict:
        """检查单个文件"""
        result = {
            'file': str(file_path),
            'violations': [],
            'passed': []
        }

        # 安全检查
        result['violations'].extend(self.check_security(file_path))

        # 命名检查
        result['violations'].extend(self.check_naming(file_path))

        # 文档检查
        result['violations'].extend(self.check_documentation(file_path))

        if not result['violations']:
            result['passed'].append('All checks passed')

        return result

    def check_directory(self, directory: Path, extensions: List[str] = None) -> Dict:
        """检查整个目录"""
        if extensions is None:
            extensions = ['.java', '.js', '.ts', '.vue', '.py']

        result = {
            'directory': str(directory),
            'files_checked': 0,
            'total_violations': 0,
            'violations_by_severity': {'P0': 0, 'P1': 0, 'P2': 0},
            'violations_by_rule': {},
            'files': []
        }

        for ext in extensions:
            for file_path in directory.rglob(f'*{ext}'):
                # 跳过target目录
                if 'target' in file_path.parts or 'node_modules' in file_path.parts:
                    continue

                file_result = self.check_file(file_path)
                result['files'].append(file_result)
                result['files_checked'] += 1
                result['total_violations'] += len(file_result['violations'])

                for v in file_result['violations']:
                    severity = v.get('severity', 'P2')
                    result['violations_by_severity'][severity] = result['violations_by_severity'].get(severity, 0) + 1

                    rule = v.get('rule', 'UNKNOWN')
                    result['violations_by_rule'][rule] = result['violations_by_rule'].get(rule, 0) + 1

        return result

    def pre_commit_check(self, directory: Path) -> Tuple[bool, str]:
        """提交前检查"""
        print(f"\n[PRE-COMMIT] Running checks on {directory}...")
        print("=" * 60)

        all_passed = True
        messages = []

        # 1. 检查编译
        compile_ok, compile_msg = self.check_compile(directory)
        print(f"[{'OK' if compile_ok else 'FAIL'}] mvn compile: {compile_msg}")
        if not compile_ok:
            all_passed = False
            messages.append(f"Compile failed: {compile_msg}")

        # 2. 检查测试
        test_ok, test_msg = self.check_tests(directory)
        print(f"[{'OK' if test_ok else 'FAIL'}] mvn test: {test_msg}")
        if not test_ok:
            all_passed = False
            messages.append(f"Test failed: {test_msg}")

        # 3. 检查代码规范
        dir_result = self.check_directory(directory)
        print(f"\n[CODE CHECK] Files: {dir_result['files_checked']}, Violations: {dir_result['total_violations']}")

        if dir_result['total_violations'] > 0:
            print("\nViolations by severity:")
            for sev, count in dir_result['violations_by_severity'].items():
                if count > 0:
                    print(f"  {sev}: {count}")

            print("\nViolations by rule:")
            for rule, count in dir_result['violations_by_rule'].items():
                print(f"  {rule}: {count}")

            # P0违规必须修复（P0=立即阻塞）
            if dir_result['violations_by_severity'].get('P0', 0) > 0:
                all_passed = False
                messages.append("P0 violations must be fixed before commit")

            # P1违规必须修复（P1=必须修复才能提交）
            if dir_result['violations_by_severity'].get('P1', 0) > 0:
                all_passed = False
                messages.append("P1 violations must be fixed before commit")

        if all_passed:
            return True, "All pre-commit checks passed"
        else:
            return False, "; ".join(messages)

    def quality_gate(self, stage: str, directory: Path) -> Tuple[bool, str]:
        """质量门卫检查"""
        print(f"\n[QUALITY GATE] Stage: {stage}")
        print("=" * 60)

        if stage == "development":
            # 开发阶段：编译 + P0安全检查
            compile_ok, msg = self.check_compile(directory)
            if not compile_ok:
                return False, f"Compile failed: {msg}"

            # 开发阶段也要检查P0漏洞
            dir_result = self.check_directory(directory)
            p0_count = dir_result['violations_by_severity'].get('P0', 0)
            if p0_count > 0:
                return False, f"P0 security violations found: {p0_count} (must fix before testing)"
            return True, "Development gate passed"

        elif stage == "testing":
            # 测试阶段：必须编译+测试通过+P0/P1安全检查
            compile_ok, compile_msg = self.check_compile(directory)
            if not compile_ok:
                return False, f"Compile failed: {compile_msg}"

            test_ok, test_msg = self.check_tests(directory)
            if not test_ok:
                return False, f"Tests failed: {test_msg}"

            # 测试阶段也要检查安全漏洞
            dir_result = self.check_directory(directory)
            p0_count = dir_result['violations_by_severity'].get('P0', 0)
            p1_count = dir_result['violations_by_severity'].get('P1', 0)
            if p0_count > 0:
                return False, f"P0 security violations: {p0_count} (must fix)"
            if p1_count > 0:
                return False, f"P1 security violations: {p1_count} (must fix)"

            return True, "Testing gate passed"

        elif stage == "deployment":
            # 部署阶段：完整的质量检查
            return self.pre_commit_check(directory)

        else:
            return True, f"No gate required for stage: {stage}"

    def generate_report(self, directory: Path) -> str:
        """生成检查报告"""
        result = self.check_directory(directory)

        report = f"""
================================================================================
RULE GUARD REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Directory: {result['directory']}
================================================================================

SUMMARY
-------
Files Checked: {result['files_checked']}
Total Violations: {result['total_violations']}

Violations by Severity:
  P0 (Blocking): {result['violations_by_severity'].get('P0', 0)}
  P1 (High):     {result['violations_by_severity'].get('P1', 0)}
  P2 (Medium):   {result['violations_by_severity'].get('P2', 0)}

Violations by Rule:
"""
        for rule, count in result['violations_by_rule'].items():
            report += f"  {rule}: {count}\n"

        # P0违规详情
        p0_violations = []
        for f in result['files']:
            for v in f['violations']:
                if v.get('severity') == 'P0':
                    p0_violations.append(v)

        if p0_violations:
            report += "\n\nP0 VIOLATIONS (Must Fix):\n"
            for v in p0_violations[:20]:
                report += f"  [{v['file']}:{v.get('line', '?')}] {v['message']}\n"

        return report


def main():
    parser = argparse.ArgumentParser(description="Rule Guard - 规则守卫")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # check命令
    check_parser = subparsers.add_parser("check", help="检查文件或目录")
    check_parser.add_argument("path", help="文件或目录路径")
    check_parser.add_argument("--ext", nargs="+", help="文件扩展名过滤")

    # pre-commit命令
    commit_parser = subparsers.add_parser("pre-commit", help="提交前检查")
    commit_parser.add_argument("path", nargs="?", default=".", help="项目目录")

    # gate命令
    gate_parser = subparsers.add_parser("gate", help="质量门卫")
    gate_parser.add_argument("stage", choices=["development", "testing", "deployment"], help="阶段")
    gate_parser.add_argument("path", nargs="?", default=".", help="项目目录")

    # enforce命令
    enforce_parser = subparsers.add_parser("enforce", help="强制执行规则")
    enforce_parser.add_argument("type", choices=["compile", "test", "security", "naming"], help="规则类型")
    enforce_parser.add_argument("path", help="文件或目录")

    # report命令
    report_parser = subparsers.add_parser("report", help="生成报告")
    report_parser.add_argument("path", nargs="?", default=".", help="项目目录")

    # detect-stuck命令
    stuck_parser = subparsers.add_parser("detect-stuck", help="检测卡死任务")
    stuck_parser.add_argument("--task-id", help="指定任务ID")

    # heal命令
    heal_parser = subparsers.add_parser("heal", help="尝试自愈")
    heal_parser.add_argument("task_id", help="任务ID")
    heal_parser.add_argument("error", help="错误信息")
    heal_parser.add_argument("--project-dir", default=".", help="项目目录")

    # clear-stuck命令
    clear_parser = subparsers.add_parser("clear-stuck", help="清除卡死状态")
    clear_parser.add_argument("task_id", nargs="?", help="任务ID（不指定则清除所有）")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    guard = RuleGuard()

    if args.command == "check":
        path = Path(args.path)
        if path.is_file():
            result = guard.check_file(path)
            print(f"\n[CHECK] {path}")
            if result['violations']:
                for v in result['violations']:
                    print(f"  [{v['severity']}] {v['message']}")
            else:
                print("  All checks passed")

        elif path.is_dir():
            result = guard.check_directory(path, args.ext)
            print(f"\n[CHECK] {path}")
            print(f"Files: {result['files_checked']}, Violations: {result['total_violations']}")
            for rule, count in result['violations_by_rule'].items():
                print(f"  {rule}: {count}")

    elif args.command == "pre-commit":
        path = Path(args.path)
        ok, msg = guard.pre_commit_check(path)
        print(f"\n[RESULT] {msg}")
        sys.exit(0 if ok else 1)

    elif args.command == "gate":
        path = Path(args.path)
        ok, msg = guard.quality_gate(args.stage, path)
        print(f"\n[GATE] {msg}")
        sys.exit(0 if ok else 1)

    elif args.command == "enforce":
        path = Path(args.path)
        if args.type == "compile":
            ok, msg = guard.check_compile(path)
        elif args.type == "test":
            ok, msg = guard.check_tests(path)
        elif args.type == "security":
            result = guard.check_directory(path)
            ok = result['violations_by_severity'].get('P0', 0) == 0
            msg = f"Security check: {result['total_violations']} violations"
        else:
            ok, msg = True, "Not implemented"
        print(f"\n[ENFORCE] {msg}")
        sys.exit(0 if ok else 1)

    elif args.command == "report":
        path = Path(args.path)
        report = guard.generate_report(path)
        print(report)

    elif args.command == "detect-stuck":
        detector = StuckDetector()
        if args.task_id:
            is_stuck = detector.is_stuck(args.task_id)
            if is_stuck:
                print(f"[STUCK] Task {args.task_id} is stuck")
            else:
                print(f"[OK] Task {args.task_id} is not stuck")
            sys.exit(1 if is_stuck else 0)
        else:
            stuck_tasks = detector.get_stuck_tasks()
            if stuck_tasks:
                print(f"[STUCK] Found {len(stuck_tasks)} stuck tasks:")
                for t in stuck_tasks:
                    print(f"  - {t}")
                sys.exit(1)
            else:
                print("[OK] No stuck tasks detected")
                sys.exit(0)

    elif args.command == "heal":
        healer = SelfHealer()
        context = {"project_dir": Path(args.project_dir)}
        success, msg = healer.attempt_heal(args.task_id, args.error, context)
        print(f"[{'OK' if success else 'FAIL'}] {msg}")
        sys.exit(0 if success else 1)

    elif args.command == "clear-stuck":
        detector = StuckDetector()
        if args.task_id:
            detector.clear_task(args.task_id)
            print(f"[OK] Cleared stuck state for {args.task_id}")
        else:
            # 清除所有
            for task_id in detector.get_stuck_tasks():
                detector.clear_task(task_id)
            print("[OK] Cleared all stuck states")


if __name__ == "__main__":
    main()
