# Skill 实体索引

> 记录所有Skill实体及其属性
> 最后更新：2026-04-03

---

## Skill 列表

### 核心Skills

| Skill | 角色 | 触发词 | 状态 |
|-------|------|--------|------|
| project-manager-skill | 项目经理 | 项目管理、任务协调 | active |
| orchestrator-skill | 协调者 | 流水线协调、任务监控 | active |
| memory-ops | 记忆操作 | 记住、存储、搜索、整理 | active |
| knowledge-sync | 知识同步 | 同步记忆、知识同步 | active |
| daily-routine | 日常自动化 | 早间简报、晚间复盘、周回顾 | active |
| knowledge-refiner | 知识精炼 | 整理记忆、去重、合并 | active |
| task-analyzer | 任务分析 | 分析任务、制定计划、分解任务 | active |

### 工作Skills

| Skill | 角色 | 触发词 | 状态 |
|-------|------|--------|------|
| product-manager-skill | 产品经理 | 需求分析、编写需求文档 | active |
| architect-skill | 架构师 | 技术方案、系统设计 | active |
| backend-dev-skill | 后端开发 | Java开发、后端实现 | active |
| frontend-dev-skill | 前端开发 | Vue开发、前端实现 | active |
| tester-skill | 测试工程师 | 测试用例、缺陷报告 | active |
| devops-skill | DevOps | 构建部署、CI/CD | active |
| operation-skill | 运维 | 环境部署、监控上线 | active |

---

## Skill 属性

### memory-ops
```yaml
name: memory-ops
description: 持久化记忆管理
trigger: 记住、存储、记忆、是什么、上次
category: memory
memory_file: skills/memory-ops.md
```

### task-analyzer
```yaml
name: task-analyzer
description: 任务分析、执行
trigger: 分析任务、制定计划、执行
category: workflow
memory_file: skills/task-analyzer.md
```

---

## Skill 依赖关系

```yaml
project-manager-skill:
  └── orchestrator-skill
       ├── product-manager-skill
       ├── architect-skill
       ├── backend-dev-skill
       ├── frontend-dev-skill
       ├── tester-skill
       ├── devops-skill
       └── operation-skill

memory-ops:
  └── knowledge-sync
       └── knowledge-refiner

daily-routine:
  └── memory-ops
```

---

## Skill 使用统计

| Skill | 使用次数 | 最后使用 | 成功率 |
|-------|----------|----------|--------|
| memory-ops | - | - | - |
| task-analyzer | - | - | - |
| daily-routine | - | - | - |

---

最后更新：2026-04-03