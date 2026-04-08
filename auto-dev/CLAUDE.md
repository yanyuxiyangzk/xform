# Auto-Dev Team Claude Code 配置

> 本文件用于配置 Claude Code 启动时的行为
> 让 Claude Code 以团队模式运行自动开发系统

---

## 🚀 快速开始

**只需对Claude说：`开始自动化开发 零代码平台`**

系统将自动完成：
1. 初始化流水线
2. 创建开发团队（TeamCreate）
3. 并行启动后端/前端/测试Agent
4. 执行Guardian质量检查
5. 运行测试验证

---

## 启动方式

### 方式1：启动完整团队（推荐）

```bash
cd d:/project/aicoding/item/ainocode
claude-code --team auto-dev
```

### 方式2：单独启动Orchestrator（调试用）

```bash
cd d:/project/aicoding/item/ainocode/auto-dev
claude-code --agent orchestrator
```

### 方式3：单次执行模式

```bash
cd d:/project/aicoding/item/ainocode/auto-dev
claude-code --agent orchestrator --mode execute
```

---

## 定时任务配置

### Cron表达式说明

| 任务 | Cron表达式 | 说明 |
|------|-----------|------|
| 状态检查 | `*/10 * * * *` | 每10分钟 |
| 任务执行 | `0 * * * *` | 每小时整点 |
| 日报生成 | `0 9 * * 1-5` | 工作日早9点 |
| 周报生成 | `0 9 * * 1` | 每周一早9点 |

### 设置定时任务

```bash
# 使用 Claude Code 的 /loop 命令设置循环

/loop 10m check-status    # 每10分钟检查状态
/loop 1h run-task          # 每小时执行任务
```

---

## 环境要求

- Claude Code CLI 已安装
- 项目目录：`d:/project/aicoding/item/ainocode`
- 记忆目录：`d:/project/aicoding/item/ainocode/auto-dev/memory`
- 任务目录：`d:/project/aicoding/item/ainocode/auto-dev/tasks`

---

## 初始化记忆

首次使用前，请确保以下记忆文件存在：

```bash
# 用户偏好
auto-dev/memory/user/profile.md

# 项目状态
auto-dev/memory/project/state.md

# Agent知识
auto-dev/memory/agents/orchestrator.md
auto-dev/memory/agents/product-manager.md
```

---

## Agent团队（8角色）

| Agent | 角色 | 启动命令 |
|-------|------|----------|
| orchestrator | 项目CEO | `--agent orchestrator` |
| product-manager | 产品经理 | `--agent product-manager` |
| backend-dev | 后端开发 | `--agent backend-dev` |
| frontend-dev | 前端开发 | `--agent frontend-dev` |
| ui-designer | UI设计师 | `--agent ui-designer` |
| tester | 测试工程师 | `--agent tester` |
| devops | DevOps | `--agent devops` |
| operation | 运维 | `--agent operation` |

### 启动单个Agent
```bash
# 启动后端开发
claude-code --agent backend-dev

# 启动产品经理
claude-code --agent product-manager

# 启动测试工程师
claude-code --agent tester
```

### 启动多个Agent并行
```bash
# 同时启动多个Agent
claude-code --agent backend-dev &
claude-code --agent frontend-dev &
claude-code --agent tester &
```

---

## 调试技巧

### 查看任务队列
```bash
cat auto-dev/tasks/backlog.md
cat auto-dev/tasks/in_progress.md
```

### 查看日志
```bash
cat auto-dev/logs/daily/$(date +%Y-%m-%d)-orchestrator.log
```

### 手动清空状态
```bash
# 重置进行中的任务到待办
mv auto-dev/tasks/in_progress.md auto-dev/tasks/backlog.md
```
