# Orchestrator Skill

> 流水线协调者 - 监控全流程、处理并行、处理异常
> 核心Skill（常驻）

---

## 🚀 激活关键词

**当用户说以下任意关键词时，立即执行对应操作：**

### 启动类
| 关键词 | 动作 |
|--------|------|
| `开始自动化开发` / `自动开发 XXX` | 一键启动完整自动化开发 |
| `继续开发` | 从 checkpoint 恢复并继续 |
| `部署` | 执行部署阶段 |

### 检查类
| 关键词 | 动作 |
|--------|------|
| `检查状态` / `查看进度` | 查看流水线状态 |
| `质量检查` | 执行 quality_gate.py |
| `代码审核` | 执行 reviewer.py |
| `运行测试` | 执行测试验证 |
| `健康检查` | 系统健康检查 |

### 工具类
| 关键词 | 动作 |
|--------|------|
| `安装钩子` | 安装 Git Hooks |
| `启动监控` | 启动心跳守护 |

---

## ⚠️ 核心禁令

```
1. 【严禁】直接写代码 — 必须委托给Agent团队
2. 【严禁】绕过Guardian检查 — 所有代码必须通过rule_guard
3. 【严禁】跳过团队协作 — 禁止单角色完成全栈开发
4. 【必须】使用TeamCreate创建团队
5. 【必须】在开发前调用gate检查
6. 【必须】在提交前调用pre-commit检查
7. 【必须】执行 mvn compile 编译测试
8. 【必须】执行 mvn test 单元测试
```

---

## 🎯 一键启动（推荐）

当用户说 **`自动开发 XXX`** 时，执行：

```bash
cd d:/project/aicoding/item/ainocode/auto-dev
python scripts/start_dev.py auto "XXX需求"
```

**start_dev.py 会自动执行：**
1. 初始化流水线
2. 调用 `agent_spawner.py spawn-team dev-team` 创建开发团队
3. Agent团队通过 Claude Code CLI 自动启动
4. 运行流水线
5. 执行质量门禁
6. 执行代码审核
7. 保存 checkpoint
8. 启动心跳守护

### TeamCreate 自动触发

使用 `agent_spawner.py` 自动触发 TeamCreate：

```bash
# 启动完整团队（后端+前端+测试）
python scripts/agent_spawner.py spawn-team dev-team

# 启动完整团队（含架构师+DevOps）
python scripts/agent_spawner.py spawn-team full-team

# 启动单个Agent
python scripts/agent_spawner.py spawn backend-dev

# 列出所有运行中的Agent
python scripts/agent_spawner.py list

# 停止指定Agent
python scripts/agent_spawner.py kill backend-dev-103045
```

**团队配置（teams-config.json）：**
| 团队 | Agent |
|------|-------|
| dev-team | backend-dev, frontend-dev, tester |
| full-team | backend-dev, frontend-dev, tester, devops, architect |

---

## 📋 可用命令

| 命令 | 说明 |
|------|------|
| `python start_dev.py auto "需求"` | 启动自动开发 |
| `python start_dev.py continue` | 从检查点继续 |
| `python start_dev.py status` | 查看状态 |
| `python start_dev.py quality` | 质量门禁 |
| `python start_dev.py review` | 代码审核 |
| `python start_dev.py heartbeat` | 启动心跳 |
| `python start_dev.py install-hook` | 安装Git Hooks |
| `python start_dev.py check` | 系统检查 |

---

## 🔄 完整流水线

```
requirement (需求分析)
       ↓
design (架构设计)
       ↓
development (开发实现)
       ├→ agent_spawner.py spawn-team (创建Agent团队)
       ├→ quality_gate.py (编译+测试+安全)
       ├→ reviewer.py (代码审核, 最多3次)
       └→ team_launcher.py (启动Agent)
       ↓
testing (测试验证)
       ↓
deployment (部署上线)
       ↓
auto_heartbeat.py (持续监控)
```

---

## 🛡️ 规则守卫

| 组件 | 功能 |
|------|------|
| `rule_guard.py` | Stuck检测、SelfHeal自愈 |
| `guardian_agent.py` | 规则守护、P0封锁 |
| `checkpoint_ops.py` | 断点保存/恢复 |

---

## 📊 异常等级

| 等级 | 说明 | 处理 |
|------|------|------|
| P0 | 安全违规、删除核心 | 立即停止 |
| P1 | 编译失败、测试失败 | 阻止通过 |
| P2 | 命名不规范 | 警告 |

---

## 🔔 24/7 无人值守

启动心跳守护后自动：
- 每 10 分钟心跳检查
- 每小时自动质量门禁
- 每小时自动保存检查点
- 检测到阻塞自动通知

```bash
python start_dev.py heartbeat
```

---

## 配置

在 `.auto-dev.yaml` 中配置：

```yaml
# 通知配置（可选）
notification:
  enabled: false
  webhook_url: "https://discord.com/api/webhooks/..."

# 时间窗口（可选）
time_window:
  enabled: false
  work_hours:
    start: "09:00"
    end: "22:00"
```

---

最后更新：2026-04-05
