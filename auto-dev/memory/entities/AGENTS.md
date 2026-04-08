# Agent 实体索引

> 记录所有Agent实体及其属性
> 最后更新：2026-04-03

---

## Agent 列表

| Agent | 角色 | 类型 | 状态 | 创建时间 |
|-------|------|------|------|----------|
| project-manager | 项目经理 | 核心 | active | 2026-04-03 |
| orchestrator | 协调者 | 核心 | active | 2026-04-02 |
| product-manager | 产品经理 | 工作 | active | 2026-04-03 |
| architect | 架构师 | 工作 | active | 2026-04-03 |
| backend-dev | 后端开发 | 工作 | active | 2026-04-02 |
| frontend-dev | 前端开发 | 工作 | active | 2026-04-02 |
| tester | 测试工程师 | 工作 | active | 2026-04-03 |
| devops | DevOps | 工作 | active | 2026-04-02 |
| operation | 运维 | 工作 | active | 2026-04-03 |

---

## Agent 属性

### project-manager
```yaml
name: project-manager
role: 项目经理
type: core
skills:
  - project-manager-skill
memory:
  directory: memory/agents/project-manager.md
```

### orchestrator
```yaml
name: orchestrator
role: 协调者
type: core
skills:
  - orchestrator-skill
memory:
  directory: memory/agents/orchestrator.md
```

### backend-dev
```yaml
name: backend-dev
role: 后端开发
type: working
skills:
  - backend-dev-skill
expertise:
  - Java/Spring
  - PF4J
  - Liquor
memory:
  directory: memory/agents/backend-dev.md
```

---

## Agent 关系

```yaml
project-manager
  ├── orchestartor (协作者)
  ├── product-manager (管理)
  ├── architect (管理)
  ├── backend-dev (分配任务)
  ├── frontend-dev (分配任务)
  ├── tester (分配任务)
  └── operation (分配任务)
```

---

最后更新：2026-04-03