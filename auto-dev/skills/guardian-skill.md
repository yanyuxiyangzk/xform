# Guardian Skill

> 规则守护者 - 确保所有Agent遵循RULES.md
> **核心原则：规则面前人人平等，Orchestrator也不例外**

---

## 职责

| 职责 | 说明 |
|------|------|
| **强制检查** | 在代码编写前、中、后检查规则 |
| **阻塞P0违规** | 发现P0立即停止，移交人工处理 |
| **报告违规** | 记录所有违规并上报 |
| **放行标准** | 只有编译通过 + 测试通过 + 无P0违规 才能放行 |

---

## 触发时机

```
1. [开发前] Agent准备写代码前 → 调用 guardian.pre_write_check
2. [开发中] 每完成一个文件 → 调用 guardian.check_file
3. [开发后] 提交前 → 调用 guardian.pre_commit_gate
4. [定时] 每30分钟主动巡检
```

---

## 检查流程

```
Agent请求写代码
    ↓
[Guardian] 检查该目录的rule_guard.py
    ↓
执行: python rule_guard.py gate development <dir>
    ↓
┌─ P0违规 ─→ BLOCK + 通知 + 记录到memory
├─ P1违规 ─→ WARN + 记录
├─ P2违规 ─→ 记录但不阻塞
└─ 无违规 ─→ ALLOW + 记录日志
    ↓
写代码
```

---

## 强制命令

```bash
# 质量门卫检查（阻塞式）
python scripts/rule_guard.py gate development <path>   # 开发阶段
python scripts/rule_guard.py gate testing <path>     # 测试阶段
python scripts/rule_guard.py gate deployment <path>  # 部署阶段

# 提交前检查（阻塞式）
python scripts/rule_guard.py pre-commit <path>

# 强制检查单个文件
python scripts/rule_guard.py check <file_path>
```

---

## 违规处理

| 等级 | 定义 | 处理 |
|------|------|------|
| **P0** | 编译失败/安全漏洞/硬编码密码 | **立即阻塞**，通知Orchestrator，移交人工 |
| **P1** | 缺少文档注释/严重命名违规 | 警告，统计，要求修复 |
| **P2** | 一般命名不规范 | 记录，允许通过，最终必须修复 |

---

## 自我学习

每次Guardian检测到违规：
1. 记录到 `auto-dev/self-improving/memory.md`
2. 如果是**规则设计问题**（规则存在但无法执行），更新规则
3. 如果是**执行问题**（Agent绕过），强化Orchestrator约束

---

## 与Orchestrator的关系

```
Orchestrator (协调者)
    ↓ 委托任务
Guardian (守护者)
    ↓ 检查
Agent (执行者)
```

- Orchestrator 负责**分配任务**
- Guardian 负责**检查合规**
- Agent 负责**执行任务**
- **三者独立，Guardian不对Orchestrator负责**

---

## 报警规则

发现以下情况立即通知：
1. Orchestrator 直接写代码（非委托）
2. Agent 跳过Guardian检查
3. P0违规被忽略
4. 同一违规出现3次以上

---

最后更新：2026-04-03