# Reviewer Skill

## 简介

Reviewer（代码审核）是 auto-dev 开发流程中的第二道质量防线。它在代码通过质量门禁后执行深度代码审查，检查命名规范、文档完整性、安全问题、测试覆盖率等，确保代码符合团队编码标准。

## 触发条件

**Pipeline 阶段**: development → reviewer_check

**手动调用**:
```
/reviewer <task_id>
python auto-dev/scripts/reviewer.py
```

## 审核流程

```
代码提交
    │
    ▼
┌─────────────────┐
│  质量门禁检查    │ ──失败──▶ 阻止提交
│  (Quality Gate) │
└────────┬────────┘
         │成功
         ▼
┌─────────────────┐
│  代码审核        │
│  (Reviewer)     │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
  通过      失败
    │         │
    ▼         ▼
┌───────┐  REVISION_REQUESTED
│审核通过│    (需要修改)
└───────┘         │
                  ▼
            修改代码 ──▶ 再次提交
                  │
                  ▼
            ┌───────────┐
            │  迭代判断  │
            └─────┬─────┘
                  │
       ┌──────────┴──────────┐
       │                     │
   迭代<3                迭代>=3
       │                     │
       ▼                     ▼
  再次审核              REJECTED
                            (审核拒绝)
```

## 审核标准

### 1. 编译成功 (compile_success)

**要求**: 代码必须能成功编译

**检查方式**: 执行 `mvn compile`

**失败处理**: 审核拒绝

---

### 2. 测试通过率 (test_pass_rate)

**要求**: 测试通过率 >= 90%

**检查方式**: `mvn test` + 解析 surefire 报告

**失败处理**: REVISION_REQUESTED

---

### 3. 无 P0 安全问题 (no_p0_security)

**要求**: 代码中不能有 P0 级别安全漏洞

**检查方式**:
- 硬编码密钥扫描
- 依赖漏洞扫描

**失败处理**: REVISION_REQUESTED

---

### 4. 无 P1 安全问题 (no_p1_security)

**要求**: 代码中不能有 P1 级别安全漏洞

**检查方式**: 同上

**失败处理**: 仅警告（可配置）

---

### 5. 无硬编码密钥 (no_hardcoded_secrets)

**要求**: 不能在代码中硬编码密码、token、API密钥等

**检查正则**:
```yaml
pattern: '(password|secret|token|api_key)\s*=\s*["\'][^"\']{3,}["\']'
severity: P0
```

**失败处理**: REVISION_REQUESTED

---

### 6. 命名规范 (naming_convention)

**要求**: 符合项目命名规范

**Java 规范**:
| 类型 | 规范 | 示例 |
|------|------|------|
| 类名 | PascalCase | `UserService`, `OrderController` |
| 方法名 | camelCase | `getUserById`, `createOrder` |
| 变量名 | camelCase | `userName`, `orderList` |
| 常量 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| 包名 | lowercase | `com.example.service` |

**失败处理**: 仅警告（MINOR 问题）

---

### 7. Javadoc 文档 (javadoc_required)

**要求**: 公共类需要 Javadoc 注释

**检查方式**: 扫描 `public class` 是否包含 `/** */` 注释

**失败处理**: 仅警告（INFO 问题）

---

## 审核结果

### APPROVED - 审核通过

所有检查项均通过，可以进入下一阶段。

### REVISION_REQUESTED - 需要修改

存在以下任一情况：
- 发现 CRITICAL/MAJOR 问题
- 硬编码密钥
- 测试覆盖率不足
- 未达到迭代上限

**处理**: 返回给开发者修改后重新提交

### REJECTED - 审核拒绝

达到最大迭代次数（默认 3 次）仍未通过审核。

**处理**: 记录问题，人工介入

---

## P0 问题（立即阻塞）

以下问题一旦发现，立即 `REJECTED`，不计入迭代次数：

- SQL注入
- 硬编码密钥/密码/凭证
- 不安全的反序列化
- 敏感信息泄露（身份证、银行卡等）
- 命令注入

---

## P1 问题（必须修复）

以下问题需要修复后才能通过审核：

- XSS
- CSRF
- 不安全的加密算法（MD5/SHA1用于安全用途）
- 路径遍历
- 权限绕过

---

## 配置示例

在 `.auto-dev.yaml` 中配置：

```yaml
# Reviewer 配置
reviewer:
  # 是否启用审核
  enabled: true

  # 最大迭代次数
  max_iterations: 3

  # 必须通过的审核次数
  required_approvals: 1

  # 审核标准
  standards:
    # 编译必须成功
    compile_success: true

    # 测试通过率 >= 90%
    test_pass_rate: 90

    # 禁止 P0 安全问题
    no_p0_security: true

    # P1 问题仅警告
    no_p1_security: false

    # 禁止硬编码密钥
    no_hardcoded_secrets: true

    # 必须符合命名规范
    naming_convention: true

    # 公共类需要 Javadoc（可选）
    javadoc_required: false
```

---

## 使用方式

### 手动执行

```bash
# 执行代码审核
python auto-dev/scripts/reviewer.py

# 指定迭代次数
python auto-dev/scripts/reviewer.py --iteration 2

# 详细输出
python auto-dev/scripts/reviewer.py --verbose

# 导出JSON报告
python auto-dev/scripts/reviewer.py --json review_report.json
```

### 在 Pipeline 中执行

```bash
# 开发完成后、测试前执行审核
python auto-dev/scripts/reviewer.py --iteration 1

# 审核通过后才能进入测试阶段
if [ $? -eq 0 ]; then
    echo "审核通过，进入测试阶段"
else
    echo "审核失败，请修改后重试"
fi
```

---

## 输出示例

### APPROVED

```
=== 代码审核 (Code Review) ===

  [1/5] 检查命名规范...
      ✓ 通过 (UserService, OrderController)

  [2/5] 检查Javadoc文档...
      ⚠ 3 个公共类缺少Javadoc

  [3/5] 检查硬编码密钥...
      ✓ 通过

  [4/5] 检查测试覆盖率...
      ✓ 通过 (85%)

  [5/5] 检查代码复杂度...
      ✓ 通过

========================================
审核结果汇总
========================================
状态: ✓ APPROVED - 审核通过
迭代次数: 1/3
审核耗时: 12.3秒

检查项:
  ✓ 命名规范
  ✓ 硬编码密钥
  ✓ 测试覆盖率
  ✓ 代码复杂度

问题汇总: 3 个
  INFO: 3 个 (Javadoc缺失)
========================================

✓ 审核通过，可以继续
```

### REVISION_REQUESTED

```
=== 代码审核 (Code Review) ===

  [1/5] 检查命名规范...
      ⚠ 2 个命名问题

  [2/5] 检查硬编码密钥...
      ✗ 发现硬编码密钥: password="123456"

  [3/5] 检查测试覆盖率...
      ✗ 覆盖率不足: 45% (要求: 70%)

========================================
审核结果汇总
========================================
状态: ⚠ REVISION_REQUESTED - 需要修改
迭代次数: 1/3
审核耗时: 8.7秒

失败项:
  ✗ 命名规范
  ✗ 硬编码密钥
  ✗ 测试覆盖率

问题汇总: 5 个
  CRITICAL: 1 个 (硬编码密钥)
  MAJOR: 2 个 (覆盖率)
  MINOR: 2 个 (命名)
========================================

⚠ 审核未通过，请修改后重试
```

---

## 审核问题级别

| 级别 | 颜色 | 说明 | 处理 |
|------|------|------|------|
| CRITICAL | 红色 | 严重问题（硬编码密钥） | 必须修复 |
| MAJOR | 黄色 | 重大问题（覆盖率不足） | 应该修复 |
| MINOR | 蓝色 | 次要问题（命名不规范） | 建议修复 |
| INFO | 灰色 | 提示信息 | 可忽略 |

---

## 故障排查

### Q: 审核太严格？

A: 调整 `.auto-dev.yaml` 中的标准：
```yaml
reviewer:
  standards:
    test_pass_rate: 70      # 降低到 70%
    naming_convention: false  # 禁用命名检查
    javadoc_required: false  # 禁用Javadoc检查
```

### Q: 如何跳过审核直接提交？

A: 不建议！但如果确实需要：
```bash
git commit --no-verify  # 跳过所有钩子
```

### Q: 审核结果有争议？

A: 在 `.auto-dev.yaml` 中配置 `required_approvals: 2` 要求多人审核。

---

## 集成

### Pipeline 集成

```
development → reviewer_check → APPROVED → testing
                              ↓
                         REVISION_REQUESTED
                              ↓ (max 3 iterations)
                         [REJECTED if still failing]
```

### Checkpoint 集成

审核状态保存到 checkpoint，便于重启后恢复。

### Notification 集成

审核结果通知相关 Agent 和 PM。

---

## 相关文件

- `scripts/reviewer.py` - 审核脚本
- `scripts/quality_gate.py` - 质量门禁
- `scripts/install_hooks.py` - 钩子安装
