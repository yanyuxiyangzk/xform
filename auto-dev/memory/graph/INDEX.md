# 知识图谱

> 存储实体之间的关联关系
> 最后更新：2026-04-03

---

## 图谱概述

```
节点数: 6
边数: 8
最后一次更新: 2026-04-03
```

---

## 初始节点

| ID | 类型 | 名称 | 属性 |
|----|------|------|------|
| AGENT-PM | agent | project-manager | role=manager |
| AGENT-BE | agent | backend-dev | role=developer |
| AGENT-FE | agent | frontend-dev | role=developer |
| SKILL-MEM | skill | memory-ops | 功能=记忆存储 |
| SKILL-SELF | skill | self-improving | 功能=自我改进 |
| PROJECT-RY | project | RuoYi-Cloud-Nocode | tech=Java+Vue |

---

## 初始边

| 源 | 边 | 目标 |
|----|---|------|
| AGENT-BE | related_to | AGENT-FE |
| AGENT-PM | manages | AGENT-BE |
| AGENT-PM | manages | AGENT-FE |
| SKILL-MEM | used_by | AGENT-PM |
| SKILL-SELF | enhances | SKILL-MEM |
| PROJECT-RY | uses | AGENT-BE |
| PROJECT-RY | uses | AGENT-FE |
| PROJECT-RY | managed_by | AGENT-PM |

---

## 节点类型

| 类型 | 描述 | 示例 |
|------|------|------|
| `agent` | Agent实体 | project-manager, backend-dev |
| `skill` | Skill实体 | memory-ops, task-analyzer |
| `task` | 任务实体 | PIPELINE-20260402-001 |
| `memory` | 记忆实体 | MEM-20260403-001 |
| `project` | 项目实体 | RuoYi-Cloud-Nocode |
| `concept` | 概念实体 | PF4J, Liquor, Vue3 |

---

## 边类型

| 类型 | 描述 | 示例 |
|------|------|------|
| `related_to` | 相关 | A related_to B |
| `depends_on` | 依赖 | A depends_on B |
| `implements` | 实现 | A implements B |
| `part_of` | 属于 | A part_of B |
| `blocks` | 阻塞 | A blocks B |
| `supersedes` | 取代 | A supersedes B |

---

## 查询示例

```markdown
# 查询所有与"backend-dev"相关的节点
/skill memory-ops
> 查询图谱：backend-dev

# 查询某个任务的所有依赖
/skill memory-ops
> 查询：PIPELINE-20260402-001的依赖
```

---

## 最近更新

| 时间 | 操作 | 节点 | 边 |
|------|------|------|---|
| - | - | - | - |

---

最后更新：2026-04-03