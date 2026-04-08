# Quality Gate Skill

## 简介

Quality Gate（质量门禁）是 auto-dev 开发流程中的第一道质量防线。它在代码提交前执行编译、测试、安全扫描等检查，确保只有符合质量标准的代码才能进入仓库。

## 触发条件

**Git Hook: pre-commit**

当开发者执行 `git commit` 时自动触发。

## 检查项

### 1. 编译检查 (Compile Check)

**目的**: 确保代码能够成功编译

**命令**: `mvn clean compile`（Maven项目）

**通过标准**: 编译返回码为 0

**失败处理**:
- `block_on_fail: true` → 阻止提交
- `block_on_fail: false` → 仅警告

**超时**: 默认 300 秒

---

### 2. 测试检查 (Test Check)

**目的**: 确保单元测试通过

**命令**: `mvn test`

**通过标准**:
- 所有测试通过（返回码 0）
- 覆盖率 >= 配置阈值（默认 70%）

**失败处理**:
- 测试失败 → 阻止提交
- 覆盖率不足 → 仅警告（除非 `coverage_low: true` 在 block_on）

**超时**: 默认 600 秒

---

### 3. 安全扫描 (Security Scan)

**目的**: 检测依赖漏洞和硬编码密钥

**工具**:
- `mvn dependency:analyze` - Maven依赖分析
- `mvn dependency:tree` - 依赖树检查（禁止依赖）
- 自定义正则扫描 - 硬编码密钥检测

**通过标准**:
- 无 P0 级别漏洞（严重安全漏洞）
- 无禁止的内部依赖

**问题级别**:
| 级别 | 说明 | 处理方式 |
|------|------|----------|
| P0 | 严重安全漏洞 | 阻止提交 |
| P1 | 高危漏洞 | 警告 |
| P2 | 中危漏洞 | 警告 |
| P3 | 低危漏洞 | 忽略 |

---

### 4. 代码风格检查 (Code Style Check)

**目的**: 确保代码符合项目规范

**命令**: `mvn checkstyle:check`

**通过标准**: checkstyle 返回码 0

**失败处理**: 仅警告（`block_on_fail: false`）

---

### 5. 禁止操作检查 (Forbidden Action Check)

**目的**: 阻止危险操作

**检查内容**:
- 禁止删除 `.git` 目录
- 禁止提交敏感文件（如 `.env`、证书等）
- 禁止硬编码密码/密钥

**正则模式**:
```yaml
hardcoded-secret:
  pattern: '(password|secret|token|api_key)\s*=\s*["\'][^"\']{3,}["\']'
  severity: P0
  message: "发现硬编码密钥，禁止提交"
```

---

## 配置示例

在项目根目录的 `.auto-dev.yaml` 中配置：

```yaml
# 质量门禁配置
gate:
  # 阻塞规则 - 满足任意一项即阻止通过
  block_on:
    compile_fail: true      # 编译失败 → 阻止
    test_fail: true        # 测试失败 → 阻止
    p0_security: true      # P0级别安全问题 → 阻止
    forbidden_action: true  # 禁止操作 → 阻止

  # 警告规则 - 满足任意一项仅警告
  warn_on:
    coverage_low: true     # 覆盖率低于阈值 → 警告
    checkstyle_fail: true  # 代码格式问题 → 警告
    p1_security: true     # P1级别安全问题 → 警告

# 测试配置
test:
  command: "mvn test"
  coverage_threshold: 70
  timeout: 600

# 安全扫描配置
security:
  enabled: true
  tools:
    - name: "dependency-analyze"
      command: "mvn dependency:analyze"
      on_fail: "warn"
    - name: "forbidden-deps"
      command: "mvn dependency:tree"
      pattern: "^(com.nocode|nocode-api)"
      allow_internal: true
  custom_rules:
    - id: "hardcoded-secret"
      pattern: '(password|secret|token|api_key)\s*=\s*["\'][^"\']{3,}["\']'
      severity: "P0"
      message: "发现硬编码密钥，禁止提交"

# Git Hooks 配置
git_hooks:
  auto_install: true
  pre_commit:
    enabled: true
    checks:
      - "quality_gate"    # 质量门禁
      - "security_scan"  # 安全扫描
      - "forbidden_check" # 禁止操作检查
    block_on_fail: true
```

## 使用方式

### 手动执行

```bash
# 执行完整质量门禁
python auto-dev/scripts/quality_gate.py

# 仅编译检查
python auto-dev/scripts/quality_gate.py --compile-only

# 仅测试检查
python auto-dev/scripts/quality_gate.py --test-only

# 跳过安全扫描
python auto-dev/scripts/quality_gate.py --skip-security

# 详细输出
python auto-dev/scripts/quality_gate.py --verbose

# 导出JSON报告
python auto-dev/scripts/quality_gate.py --json report.json
```

### Git Hook 自动执行

安装钩子后，每次 `git commit` 自动执行：

```bash
# 安装 Git Hooks
python auto-dev/scripts/install_hooks.py install

# 查看钩子状态
python auto-dev/scripts/install_hooks.py list
```

---

## 输出示例

### 通过

```
=== 质量门禁 (Quality Gate) ===

[1/5] 编译检查...
      ✓ 通过 (23.5s)

[2/5] 测试检查...
      ✓ 通过 (45.2s)

[3/5] 安全扫描...
      ✓ 通过 (12.1s)

[4/5] 代码风格检查...
      ⚠ 警告: 3 个格式问题

[5/5] 禁止操作检查...
      ✓ 通过

========================================
质量门禁检查完成: 4/5 项通过
========================================

✓ 质量门禁通过，可以提交
```

### 失败

```
=== 质量门禁 (Quality Gate) ===

[1/5] 编译检查...
      ✗ 失败
      Error: package com.example does not exist

[2/5] 测试检查...
      ✗ 失败
      Failed tests: TestUserService

========================================
质量门禁检查失败
========================================

✗ 编译失败，阻止提交
✗ 测试失败，阻止提交

请修复上述问题后重试
```

---

## 故障排查

### Q: 编译超时怎么办？

A: 增加超时时间：
```yaml
compile:
  timeout: 600  # 10分钟
```

### Q: 安全扫描太慢？

A: 禁用特定工具或使用异步扫描：
```yaml
security:
  tools:
    - name: "dependency-analyze"
      on_fail: "ignore"  # 跳过此工具
```

### Q: 误报硬编码密钥？

A: 将误报文件添加到忽略列表：
```yaml
security:
  exclude_files:
    - "**/application-prod.yml"
```

---

## 相关文件

- `scripts/quality_gate.py` - 主脚本
- `scripts/security_scan.py` - 安全扫描
- `scripts/install_hooks.py` - 钩子安装
